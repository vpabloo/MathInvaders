/** Integración opcional. Sin credenciales la aplicación funciona como invitado. */
import { createClient, type User } from '@supabase/supabase-js';
import type { RunSummary } from '../math/engine';

const url = import.meta.env.VITE_SUPABASE_URL?.trim();
const publicKey = import.meta.env.VITE_SUPABASE_ANON_KEY?.trim();

export const backend = url && publicKey
  ? createClient(url, publicKey, { auth: { persistSession: true, autoRefreshToken: true } })
  : null;

export interface SchoolRow {
  school_id: string;
  school_name: string;
  school_kind: 'school' | 'academy';
  student_count: number;
  total_score: number;
}

export interface PlayerProfile {
  id: string;
  display_name: string;
  school_id: string | null;
}

function requireBackend() {
  if (!backend) throw new Error('Falta configurar Supabase');
  return backend;
}

function unwrap(error: { message: string } | null) {
  if (error) throw new Error(error.message);
}

export async function currentUser(): Promise<User | null> {
  if (!backend) return null;
  const { data, error } = await backend.auth.getUser();
  if (error) return null;
  return data.user;
}

export async function signUp(email: string, password: string, name: string): Promise<boolean> {
  const client = requireBackend();
  const { data, error } = await client.auth.signUp({
    email, password,
    options: { data: { display_name: name.trim().slice(0, 60) } },
  });
  unwrap(error);
  // true significa que puede requerirse validación por correo.
  return !data.session;
}

export async function signIn(email: string, password: string): Promise<void> {
  const { error } = await requireBackend().auth.signInWithPassword({ email, password });
  unwrap(error);
}

export async function signOut(): Promise<void> {
  const { error } = await requireBackend().auth.signOut();
  unwrap(error);
}

export async function getProfile(): Promise<PlayerProfile | null> {
  const client = requireBackend();
  const user = await currentUser();
  if (!user) return null;
  const { data, error } = await client
    .from('profiles')
    .select('id, display_name, school_id')
    .eq('id', user.id)
    .maybeSingle();
  unwrap(error);
  return data as PlayerProfile | null;
}

export async function joinSchool(code: string): Promise<string> {
  const { data, error } = await requireBackend().rpc('join_school', {
    invitation_code: code.trim().toUpperCase(),
  });
  unwrap(error);
  return String(data);
}

export async function submitRun(run: RunSummary): Promise<void> {
  const user = await currentUser();
  if (!user) throw new Error('Necesitas iniciar sesión para registrar tus puntos en línea.');
  const { error } = await requireBackend().from('scores').insert({
    user_id: user.id, ...run,
  });
  unwrap(error);
}

export async function fetchMyBest(): Promise<number> {
  const user = await currentUser();
  if (!user) return 0;
  const { data, error } = await requireBackend()
    .from('scores')
    .select('score')
    .eq('user_id', user.id)
    .order('score', { ascending: false })
    .limit(1);
  unwrap(error);
  return Number(data?.[0]?.score ?? 0);
}

export async function fetchSchoolLeaderboard(): Promise<SchoolRow[]> {
  if (!backend) return [];
  const { data, error } = await backend.rpc('school_leaderboard', { result_limit: 20 });
  unwrap(error);
  return (data ?? []) as SchoolRow[];
}
