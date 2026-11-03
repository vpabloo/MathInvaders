import { describe, expect, it } from 'vitest';
import { MathEngine, OPERATORS, POINTS_PER_CORRECT, normalizeOperators } from './engine';

describe('Modalidades y puntuación MathInvaders', () => {
  it('exige alguna modalidad y elimina selecciones repetidas', () => {
    expect(() => new MathEngine(Math.random, [])).toThrow();
    expect(normalizeOperators(['+', '+', '/'])).toEqual(['+', '/']);
    expect(() => normalizeOperators(['%', 'sin'])).toThrow();
  });

  it('para cada operación genera exactamente una opción correcta entre cinco números únicos', () => {
    for (const op of OPERATORS) {
      const engine = new MathEngine(Math.random, [op]);
      for (let i = 0; i < 200; i++) {
        const q = engine.question;
        expect(q.operator).toBe(op);
        expect(q.options).toHaveLength(5);
        expect(new Set(q.options).size).toBe(5);
        expect(q.options.filter((n) => n === q.answer)).toHaveLength(1);
        switch (op) {
          case '+': expect(q.answer).toBe(q.left + q.right); break;
          case '-': expect(q.answer).toBe(q.left - q.right); break;
          case '*': expect(q.answer).toBe(q.left * q.right); break;
          case '/':
            expect(q.right).toBeGreaterThan(0);
            expect(q.left % q.right).toBe(0);
            expect(q.answer).toBe(q.left / q.right);
            break;
        }
        expect(q.answer).toBeGreaterThanOrEqual(0);
        engine.nextQuestion();
      }
    }
  });

  it('solo presenta las modalidades seleccionadas; permite combinar las cuatro', () => {
    const rng = Math.random;
    const mixed = new MathEngine(rng, ['+', '-', '*', '/']);
    const seen = new Set<string>();
    for (let i = 0; i < 250; i++) {
      seen.add(mixed.question.operator);
      mixed.nextQuestion();
    }
    expect(seen).toEqual(new Set(OPERATORS));
    mixed.setOperators(['*', '/']);
    for (let i = 0; i < 100; i++) {
      expect(['*', '/']).toContain(mixed.question.operator);
      mixed.nextQuestion();
    }
  });

  it('otorga más puntos por operaciones difíciles, con multiplicador de nivel', () => {
    const scores = OPERATORS.map((op) => {
      const engine = new MathEngine(Math.random, [op]);
      expect(engine.answer(engine.question.answer)).toBe(true);
      expect(engine.operationPoints[op]).toBe(POINTS_PER_CORRECT[op]);
      expect(engine.score).toBe(POINTS_PER_CORRECT[op]);
      return engine.score;
    });
    expect(scores).toEqual([10, 20, 30, 40]);
    const game = new MathEngine(Math.random, ['/']);
    for (let i = 0; i < 5; i++) {
      game.answer(game.question.answer);
      game.nextQuestion();
    }
    expect(game.level).toBe(2);
    game.answer(game.question.answer);
    expect(game.operationPoints['/']).toBe(5 * 40 + 80);
  });

  it('penaliza errores en la modalidad activa y no cambia de pregunta', () => {
    const engine = new MathEngine(Math.random, ['*']);
    const question = engine.question;
    const wrong = question.options.find((n) => n !== question.answer)!;
    const penalty = Math.max(1, Math.floor(wrong / 2));
    expect(engine.answer(wrong)).toBe(false);
    expect(engine.question).toBe(question);
    expect(engine.score).toBe(-penalty);
    expect(engine.operationPoints['*']).toBe(-penalty);
    expect(engine.wrongCount).toBe(1);
    const summary = engine.makeSummary(2.5, 'test-session');
    expect(summary.score).toBe(0);
    expect(summary.operation_points['*']).toBe(-penalty);
    expect(summary.selected_operators).toEqual(['*']);
    expect(summary.duration_seconds).toBe(2);
  });

  it('reinicia el puntaje, pero conserva las modalidades seleccionadas', () => {
    const game = new MathEngine(Math.random, ['-', '/']);
    game.answer(game.question.answer);
    game.loseLife();
    game.reset();
    expect(game.score).toBe(0);
    expect(game.lives).toBe(3);
    expect(game.level).toBe(1);
    expect(game.operationPoints).toEqual({ '+': 0, '-': 0, '*': 0, '/': 0 });
    expect(game.selectedOperators).toEqual(['-', '/']);
  });
});
