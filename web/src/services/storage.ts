import {
  OPERATORS, emptyOperationPoints, normalizeOperators,
  type Operator, type OperationPoints, type RunSummary,
} from '../math/engine';

const RECORD_KEY = 'mathinvaders:web:record:v2';
const LEGACY_RECORD_KEY = 'mathinvaders:web:record:v1';
const MODE_KEY = 'mathinvaders:web:modalities:v1';

export interface LocalRecord {
  best: number;
  games: number;
  total: number;
  operationTotals: OperationPoints;
}

function safeNumber(value: unknown): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : 0;
}

export function readLocalRecord(): LocalRecord {
  const blank: LocalRecord = { best: 0, games: 0, total: 0, operationTotals: emptyOperationPoints() };
  try {
    const raw = localStorage.getItem(RECORD_KEY) ?? localStorage.getItem(LEGACY_RECORD_KEY);
    if (!raw) return blank;
    const value: unknown = JSON.parse(raw);
    if (!value || typeof value !== 'object') return blank;
    const record = value as Partial<LocalRecord>;
    const points = record.operationTotals;
    const totals = emptyOperationPoints();
    for (const op of OPERATORS) totals[op] = safeNumber(points?.[op]);
    return {
      best: Math.max(0, safeNumber(record.best)),
      games: Math.max(0, safeNumber(record.games)),
      total: Math.max(0, safeNumber(record.total)),
      operationTotals: totals,
    };
  } catch {
    return blank;
  }
}

export function saveLocalRun(run: RunSummary): LocalRecord {
  const current = readLocalRecord();
  const totals = { ...current.operationTotals };
  for (const op of OPERATORS) totals[op] += run.operation_points[op];
  const next = {
    best: Math.max(current.best, run.score),
    games: current.games + 1,
    total: current.total + run.score,
    operationTotals: totals,
  };
  try { localStorage.setItem(RECORD_KEY, JSON.stringify(next)); }
  catch { /* Navegación privada: juego sin persistencia. */ }
  return next;
}

export function readSelectedOperators(): Operator[] {
  try {
    const raw = localStorage.getItem(MODE_KEY);
    if (raw) {
      const data: unknown = JSON.parse(raw);
      if (Array.isArray(data) && data.every((value) => typeof value === 'string')) {
        return normalizeOperators(data as string[]);
      }
    }
  } catch { /* Volver a la suma. */ }
  return ['+'];
}

export function saveSelectedOperators(operators: readonly Operator[]): void {
  const normalized = normalizeOperators(operators);
  try { localStorage.setItem(MODE_KEY, JSON.stringify(normalized)); }
  catch { /* El estado de la sesión sigue funcionando. */ }
}
