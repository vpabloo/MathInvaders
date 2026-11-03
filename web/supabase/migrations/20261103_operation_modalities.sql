-- Ejecutar UNA VEZ para una instalación Supabase anterior a las modalidades.
-- Para una instalación nueva, basta ejecutar el schema.sql actualizado.

alter table public.scores
  add column if not exists selected_operators text[] not null
    default array['+']::text[];

alter table public.scores
  add column if not exists operation_points jsonb not null
    default '{"+" : 0, "-" : 0, "*" : 0, "/" : 0}'::jsonb;

alter table public.scores
  drop constraint if exists basic_score_ceiling;

alter table public.scores
  add constraint basic_score_ceiling check (
    score <= correct_count * (40 * level_reached)
  );

-- Información de los récords históricos: las partidas anteriores no incluían
-- desgloses. Sus puntuaciones originales se conservan en "score".
