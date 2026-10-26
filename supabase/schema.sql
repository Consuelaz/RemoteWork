-- ============================================================
-- Junes远程 · 会员权益与兑换系统
-- 执行方式：Supabase 控制台 → SQL Editor → 粘贴全量执行（可重复执行）
-- 设计要点：
--   1. 兑换码状态存服务端，前端永远拿不到未使用的码
--   2. redeem_code() 用 SELECT ... FOR UPDATE 行锁串行化同码并发请求
--   3. redemptions.code 唯一约束作为兜底：即便逻辑出 bug，
--      第二个事务也会因唯一键冲突整体回滚，不可能出现"一码两兑"
--   4. job_access 存放真正需要付费才能看的数据（申请链接 / 内推联系方式）
-- ============================================================

-- ============ 0. 扩展 ============
create extension if not exists "pgcrypto";

-- ============ 1. 用户档案 ============
create table if not exists public.profiles (
  id         uuid primary key references auth.users(id) on delete cascade,
  -- 登录方式：邮箱验证码 / 魔法链接
  email      text,
  -- 预留：后续若加手机号绑定，填这里（当前登录不走手机号）
  phone      text,
  nickname   text,
  created_at timestamptz not null default now()
);

-- ============ 2. 会员权益（每个用户一行，续费即延长 expires_at）============
create table if not exists public.memberships (
  user_id    uuid primary key references auth.users(id) on delete cascade,
  plan       text not null default 'monthly',
  started_at timestamptz not null default now(),
  expires_at timestamptz not null,
  updated_at timestamptz not null default now()
);
create index if not exists memberships_expires_idx on public.memberships (expires_at);

-- ============ 3. 兑换码 ============
create table if not exists public.redeem_codes (
  code          text primary key,
  plan          text not null default 'monthly',
  duration_days int  not null default 30,
  batch         text,
  status        text not null default 'unused' check (status in ('unused', 'used', 'disabled')),
  used_by       uuid references auth.users(id),
  used_at       timestamptz,
  expires_at    timestamptz,
  created_at    timestamptz not null default now()
);
create index if not exists redeem_codes_status_idx on public.redeem_codes (status);
create index if not exists redeem_codes_batch_idx  on public.redeem_codes (batch);

-- ============ 4. 兑换流水（审计 + 唯一约束兜底防重复）============
create table if not exists public.redemptions (
  id            bigserial primary key,
  code          text not null unique,           -- 一个码在全局只能产生一条流水
  user_id       uuid not null references auth.users(id) on delete cascade,
  plan          text not null,
  duration_days int  not null,
  redeemed_at   timestamptz not null default now()
);
create index if not exists redemptions_user_idx on public.redemptions (user_id);

-- ============ 5. 会员专属数据（岗位申请链接 / 内推人联系方式）============
create table if not exists public.job_access (
  job_id       text primary key,
  apply_url    text,
  contact      text,
  contact_type text,
  updated_at   timestamptz not null default now()
);
create index if not exists job_access_updated_idx on public.job_access (updated_at);

-- ============ 6. 判定函数：当前用户是否为有效会员 ============
-- 注意：必须在下面的 RLS 策略之前创建，否则 job_access 策略引用时会报
--       "function public.is_member() does not exist"
create or replace function public.is_member()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.memberships m
    where m.user_id = auth.uid()
      and m.expires_at > now()
  );
$$;

-- ============ 7. RLS ============
alter table public.profiles     enable row level security;
alter table public.memberships  enable row level security;
alter table public.redeem_codes enable row level security;
alter table public.redemptions  enable row level security;
alter table public.job_access   enable row level security;

-- profiles：只能看/改自己的
drop policy if exists "profiles_self" on public.profiles;
create policy "profiles_self" on public.profiles
  for select using (auth.uid() = id);

-- memberships：只能看自己的
drop policy if exists "memberships_self" on public.memberships;
create policy "memberships_self" on public.memberships
  for select using (auth.uid() = user_id);

-- redemptions：只能看自己的兑换记录
drop policy if exists "redemptions_self" on public.redemptions;
create policy "redemptions_self" on public.redemptions
  for select using (auth.uid() = user_id);

-- redeem_codes：故意不给任何 select/update 策略
-- → 普通用户（含已登录）无法枚举、无法篡改兑换码，只能通过 redeem_code() 函数访问

-- job_access：只有会员能读
drop policy if exists "job_access_member_only" on public.job_access;
create policy "job_access_member_only" on public.job_access
  for select using (public.is_member());

-- ============ 8. 核心：原子兑换函数 ============
-- 返回 json：{ok:boolean, error?:text, plan?:text, expires_at?:text, days?:int}
-- 错误码：not_authenticated / code_not_found / code_disabled / code_expired
--         code_already_used / already_used_by_you
create or replace function public.redeem_code(p_code text)
returns json
language plpgsql
security definer
set search_path = public
as $$
declare
  v_uid   uuid := auth.uid();
  v_code  text := upper(btrim(coalesce(p_code, '')));
  v_row   public.redeem_codes;
  v_base  timestamptz;
  v_exp   timestamptz;
begin
  if v_uid is null then
    return json_build_object('ok', false, 'error', 'not_authenticated');
  end if;

  if v_code = '' then
    return json_build_object('ok', false, 'error', 'code_not_found');
  end if;

  -- 关键：FOR UPDATE 行锁。同一兑换码的并发请求会在这里排队，
  -- 第二个事务读到的是第一个事务提交后的 status='used'，从而被拒绝。
  select * into v_row
  from public.redeem_codes
  where code = v_code
  for update;

  if not found then
    return json_build_object('ok', false, 'error', 'code_not_found');
  end if;

  if v_row.status = 'disabled' then
    return json_build_object('ok', false, 'error', 'code_disabled');
  end if;

  if v_row.status = 'used' or v_row.used_by is not null then
    if v_row.used_by = v_uid then
      return json_build_object('ok', false, 'error', 'already_used_by_you');
    else
      return json_build_object('ok', false, 'error', 'code_already_used');
    end if;
  end if;

  if v_row.expires_at is not null and v_row.expires_at < now() then
    return json_build_object('ok', false, 'error', 'code_expired');
  end if;

  -- 1) 写流水：redemptions.code 唯一约束是最后一道防线
  insert into public.redemptions (code, user_id, plan, duration_days)
  values (v_code, v_uid, v_row.plan, v_row.duration_days);

  -- 2) 标记兑换码已使用
  update public.redeem_codes
     set status  = 'used',
         used_by = v_uid,
         used_at = now()
   where code = v_code;

  -- 3) 开通/续期会员：已有会员则从原到期时间往后叠加，未过期不浪费
  select greatest(coalesce(m.expires_at, now()), now())
    into v_base
    from public.memberships m
   where m.user_id = v_uid;

  v_base := coalesce(v_base, now());
  v_exp  := v_base + (v_row.duration_days || ' days')::interval;

  insert into public.memberships (user_id, plan, started_at, expires_at, updated_at)
  values (v_uid, v_row.plan, now(), v_exp, now())
  on conflict (user_id) do update
    set plan       = excluded.plan,
        expires_at = v_exp,
        updated_at = now();

  return json_build_object(
    'ok', true,
    'plan', v_row.plan,
    'days', v_row.duration_days,
    'expires_at', to_char(v_exp at time zone 'Asia/Shanghai', 'YYYY-MM-DD HH24:MI')
  );
end;
$$;

-- ============ 9. 当前会员状态（前端刷新用）============
create or replace function public.my_membership()
returns table (plan text, started_at timestamptz, expires_at timestamptz, is_active boolean)
language sql
stable
security definer
set search_path = public
as $$
  select m.plan, m.started_at, m.expires_at, (m.expires_at > now()) as is_active
  from public.memberships m
  where m.user_id = auth.uid();
$$;

-- ============ 10. 批量取会员专属数据 ============
create or replace function public.get_job_access(p_job_ids text[])
returns table (job_id text, apply_url text, contact text, contact_type text)
language sql
stable
security definer
set search_path = public
as $$
  select ja.job_id, ja.apply_url, ja.contact, ja.contact_type
  from public.job_access ja
  where ja.job_id = any(p_job_ids)
    and public.is_member();
$$;

-- ============ 11. 注册即建档案 ============
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, email)
  values (new.id, new.email)
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ============ 12. 权限 ============
grant execute on function public.redeem_code(text)      to authenticated;
grant execute on function public.my_membership()        to authenticated;
grant execute on function public.get_job_access(text[]) to authenticated;
grant execute on function public.is_member()            to authenticated, anon;

-- ============================================================
-- 自检 SQL（在 SQL Editor 里单独跑，确认策略是否生效）
-- 1) 兑换码表对普通用户不可见（应返回 0 行或报权限错）
--    select * from public.redeem_codes limit 1;
-- 2) 非会员取不到权益数据（应返回 0 行）
--    select * from public.get_job_access(array['cn-v2ex-1250975-9']);
-- 3) 查看某码状态（service_role 身份执行）
--    select code, status, used_by, used_at from public.redeem_codes order by created_at desc limit 20;
-- ============================================================
