import type { RunSummary } from '../math/engine';

const KEY = 'mathinvaders:web:record:v1';

export interface LocalRecord {
  best: number;
  games: number;
  total: number;
}

export function readLocalRecord(): LocalRecord {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const value: unknown = JSON.parse(raw);
      if (value && typeof value === 'object') {
        const record = value as Partial<LocalRecord>;
        if (Number.isFinite(record.best) && Number.isFinite(record.games) &&
            Number.isFinite(record.total)) {
          return {
            best: Math.max(0, Number(record.best)),
            games: Math.max(0, Number(record.games)),
            total: Math.max(0, Number(record.total)),
          };
        }
      }
    }
  } catch { /* Almacenamiento bloqueado: permitir juego invitado igualmente. */ }
  return { best: 0, games: 0, total: 0 };
}

export function saveLocalRun(run: RunSummary): LocalRecord {
  const current = readLocalRecord();
  const next = {
    best: Math.max(current.best, run.score),
    games: current.games + 1,
    total: current.total + run.score,
  };
  try {
    localStorage.setItem(KEY, JSON.stringify(next));
  } catch { /* Sin persistencia si el navegador la bloquea. */ }
  return next;
}
