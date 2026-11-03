import { describe, expect, it } from 'vitest';
import { MathEngine, OPERATORS, POINTS_PER_CORRECT, maxAnswerForLevel, normalizeOperators } from './engine';

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


  it('mantiene los resultados y las cinco opciones entre 0 y 10 en niveles 1–3', () => {
    for (const operator of OPERATORS) {
      const engine = new MathEngine(Math.random, [operator]);
      for (const level of [1, 2, 3]) {
        engine.level = level;
        for (let round = 0; round < 150; round++) {
          const q = engine.nextQuestion();
          expect(q.answer).toBeGreaterThanOrEqual(0);
          expect(q.answer).toBeLessThanOrEqual(10);
          expect(q.options).toHaveLength(5);
          expect(new Set(q.options).size).toBe(5);
          expect(q.options.every((option) => Number.isInteger(option) && option >= 0 && option <= 10)).toBe(true);
          if (operator === '/') {
            expect(q.left).toBeLessThanOrEqual(20);
            expect(q.right).toBeGreaterThan(0);
            expect(q.left % q.right).toBe(0);
          }
        }
      }
    }
  });

  it('aumenta la dificultad gradualmente cada dos niveles a partir del cuarto', () => {
    const expected = [
      [1, 10], [2, 10], [3, 10],
      [4, 15], [5, 15], [6, 20], [7, 20],
      [8, 30], [9, 30], [10, 40], [11, 40],
      [12, 50], [13, 50],
    ];
    for (const [level, cap] of expected) expect(maxAnswerForLevel(level)).toBe(cap);
    expect(maxAnswerForLevel(300)).toBe(999);
    expect(() => maxAnswerForLevel(0)).toThrow(RangeError);
    expect(() => maxAnswerForLevel(2.5)).toThrow(RangeError);
  });

  it('genera cifras más grandes en cada operación tras subir niveles', () => {
    for (const operator of OPERATORS) {
      const engine = new MathEngine(Math.random, [operator]);
      for (const level of [4, 6, 8, 12, 20]) {
        engine.level = level;
        const cap = maxAnswerForLevel(level);
        let exceededTen = false;
        for (let round = 0; round < 250; round++) {
          const q = engine.nextQuestion();
          expect(q.answer).toBeLessThanOrEqual(cap);
          expect(q.options.every((n) => n >= 0 && n <= cap)).toBe(true);
          if (q.answer > 10) exceededTen = true;
          if (operator === '/') expect(q.left / q.right).toBe(q.answer);
        }
        expect(exceededTen).toBe(true);
      }
    }
  });

  it('la subida de nivel modifica el límite solo después de los aciertos', () => {
    const game = new MathEngine(Math.random, ['+']);
    for (let i = 0; i < 15; i++) {
      expect(game.question.answer).toBeLessThanOrEqual(maxAnswerForLevel(game.level));
      game.answer(game.question.answer);
      game.nextQuestion();
    }
    expect(game.level).toBe(4);
    expect(maxAnswerForLevel(game.level)).toBe(15);
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
