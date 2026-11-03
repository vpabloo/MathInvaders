import { beforeEach, describe, expect, it, vi } from 'vitest';
import { emptyOperationPoints, type RunSummary } from '../math/engine';
import { readLocalRecord, readSelectedOperators, saveLocalRun, saveSelectedOperators } from './storage';

const store = new Map<string, string>();

beforeEach(() => {
  store.clear();
  vi.stubGlobal('localStorage', {
    getItem: (key: string) => store.get(key) ?? null,
    setItem: (key: string, value: string) => { store.set(key, value); },
  });
});

describe('Almacenamiento de modalidades y récords', () => {
  it('comienza con suma y permite guardar una selección múltiple', () => {
    expect(readSelectedOperators()).toEqual(['+']);
    saveSelectedOperators(['*', '/', '+']);
    expect(readSelectedOperators()).toEqual(['+', '*', '/']);
    expect(() => saveSelectedOperators([])).toThrow();
  });

  it('conserva los récords del almacenamiento anterior', () => {
    store.set('mathinvaders:web:record:v1', JSON.stringify({
      best: 80, games: 3, total: 130,
    }));
    const record = readLocalRecord();
    expect(record.best).toBe(80);
    expect(record.games).toBe(3);
    expect(record.total).toBe(130);
    expect(record.operationTotals).toEqual(emptyOperationPoints());
  });

  it('suma los puntos netos de cada modalidad y conserva el récord general', () => {
    const summary: RunSummary = {
      score: 35,
      correct_count: 2,
      wrong_count: 1,
      level_reached: 1,
      duration_seconds: 25,
      client_run_id: 'id',
      selected_operators: ['+', '/'],
      operation_points: { '+': 10, '-': 0, '*': 0, '/': 25 },
    };
    const first = saveLocalRun(summary);
    expect(first.best).toBe(35);
    expect(first.operationTotals['/']).toBe(25);
    const second = saveLocalRun(summary);
    expect(second.total).toBe(70);
    expect(second.operationTotals['+']).toBe(20);
    expect(second.operationTotals['/']).toBe(50);
    expect(second.best).toBe(35);
    expect(second.games).toBe(2);
  });
});
