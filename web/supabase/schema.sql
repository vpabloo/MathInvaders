-- MathInvaders: esquema opcional para Supabase (PostgreSQL).
-- Ejecutar desde el SQL Editor del proyecto como administrador.
-- NO expone correos ni puntuaciones individuales en el ranking público.
-- Las puntuaciones del cliente son provisionales: se requiere validación servidor
-- antes de competir por premios o reconocimientos.

create schema if not exists private;
revoke all on schema private from anon, authenticated;

create table if not exists public.schools (
  id uuid primary key default gen_random_uuid(),
  name text not null check (char_length(btrim(name)) between 3 and 120),
  slug text not null unique check (slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'),
  kind text not null check (kind in ('school', 'academy')),
  created_at timestamptz not null default now()
);

create table if not exists private.school_invites (
  school_id uuid primary key references public.schools(id) on delete cascade,
  code text not null unique check (char_length(code) between 12 and 40)
);

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text not null default 'Estudiante'
    check (char_length(btrim(display_name)) between 1 and 60),
  school_id uuid references public.schools(id) on delete restrict,
  created_at timestamptz not null default now()
);

create table if not exists public.scores (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  client_run_id uuid not null,
  score integer not null check (score between 0 and 1000000),
  selected_operators text[] not null default array['+']::text[],
  operation_points jsonb not null default '{"+":0,"-":0,"*":0,"/":0}'::jsonb,
  correct_count integer not null check (correct_count between 0 and 100000),
  wrong_count integer not null check (wrong_count between 0 and 100000),
  level_reached integer not null check (level_reached >= 1),
  duration_seconds integer not null check (duration_seconds between 1 and 86400),
  created_at timestamptz not null default now(),
  unique (user_id, client_run_id),
  constraint level_matches_correct_answers check (
    level_reached = 1 + correct_count / 5
  ),
  constraint basic_score_ceiling check (
    score <= correct_count * (40 * level_reached)
  ),
  constraint basic_play_rate check (
    correct_count <= duration_seconds * 8
  )
);
create index if not exists idx_scores_user_best
  on public.scores (user_id, score desc);
create index if not exists idx_profiles_school
  on public.profiles (school_id);

-- Impedir acceso directo a instituciones y códigos desde el cliente.
revoke all on public.schools from anon, authenticated;
revoke all on private.school_invites from anon, authenticated;
grant select on public.profiles to authenticated;
grant select, insert on public.scores to authenticated;

alter table public.schools enable row level security;
alter table private.school_invites enable row level security;
alter table public.profiles enable row level security;
alter table public.scores enable row level security;

drop policy if exists "Alumno lee su perfil" on public.profiles;
create policy "Alumno lee su perfil" on public.profiles
  for select to authenticated using ((select auth.uid()) = id);

drop policy if exists "Alumno lee sus partidas" on public.scores;
create policy "Alumno lee sus partidas" on public.scores
  for select to authenticated using ((select auth.uid()) = user_id);

drop policy if exists "Alumno registra su partida" on public.scores;
create policy "Alumno registra su partida" on public.scores
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

-- El trigger crea el perfil: el usuario no puede inventar su escuela.
create or replace function public.handle_mathinvaders_signup()
returns trigger
language plpgsql security definer set search_path = ''
as $$
begin
  insert into public.profiles (id, display_name)
  values (
    new.id,
    coalesce(
      nullif(left(btrim(new.raw_user_meta_data ->> 'display_name'), 60), ''),
      'Estudiante'
    )
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_mathinvaders_signup on auth.users;
create trigger on_mathinvaders_signup
  after insert on auth.users
  for each row execute function public.handle_mathinvaders_signup();

-- Única operación autorizada para vincularse: código privado y una sola vez.
create or replace function public.join_school(invitation_code text)
returns uuid
language plpgsql security definer set search_path = ''
as $$
declare
  target_school uuid;
begin
  if (select auth.uid()) is null then
    raise exception 'Debes iniciar sesión';
  end if;
  select school_id into target_school
  from private.school_invites
  where code = upper(btrim(invitation_code));

  if target_school is null then
    raise exception 'Código institucional inválido';
  end if;

  update public.profiles
    set school_id = target_school
  where id = (select auth.uid()) and school_id is null;

  if not found then
    raise exception 'Ya perteneces a una institución. Solicita asistencia para cambiarla';
  end if;

  return target_school;
end;
$$;
revoke all on function public.join_school(text) from public;
grant execute on function public.join_school(text) to authenticated;

-- Sumar UNA vez el récord máximo de cada alumno, sin datos de menores.
create or replace function public.school_leaderboard(result_limit integer default 20)
returns table (
  school_id uuid,
  school_name text,
  school_kind text,
  student_count bigint,
  total_score bigint
)
language sql stable security definer set search_path = ''
as $$
  select
    s.id, s.name, s.kind, count(p.id)::bigint,
    coalesce(sum(coalesce(personal_best.best_score, 0)), 0)::bigint
  from public.schools as s
  left join public.profiles as p on p.school_id = s.id
  left join lateral (
    select max(sc.score) as best_score
    from public.scores sc
    where sc.user_id = p.id
  ) as personal_best on true
  group by s.id, s.name, s.kind
  order by total_score desc, student_count desc, school_name asc
  limit least(100, greatest(1, coalesce(result_limit, 20)));
$$;

revoke all on function public.school_leaderboard(integer) from public;
grant execute on function public.school_leaderboard(integer) to anon, authenticated;

-- CREACIÓN DE INSTITUCIONES: exclusivamente por administradores (SQL Editor).
-- Sustituye valores y utiliza un código aleatorio de longitud suficiente.
--
-- with created as (
--   insert into public.schools(name,slug,kind)
--   values ('Academia Ejemplo','academia-ejemplo','academy')
--   returning id
-- )
-- insert into private.school_invites(school_id,code)
-- select id, upper(replace(gen_random_uuid()::text,'-','')) from created
-- returning code;
--
-- Entrega el código SOLO al responsable de la institución. No lo publiques.
