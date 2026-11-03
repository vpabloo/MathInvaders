import { describe, expect, it } from 'vitest';
import { MathEngine } from './engine';

describe('Motor matemático de MathInvaders', () => {
  it('genera cinco opciones distintas y una sola respuesta correcta', () => {
    const engine = new MathEngine();
    for (let i = 0; i < 300; i++) {
      expect(engine.question.options).toHaveLength(5);
      expect(new Set(engine.question.options).size).toBe(5);
      expect(engine.question.options.filter((v) => v === engine.question.answer)).toHaveLength(1);
      engine.nextQuestion();
    }
  });

  it('el error conserva la pregunta y penaliza al menos un punto', () => {
    const game = new MathEngine();
    const initial = game.question;
    const wrong = initial.options.find((n) => n !== initial.answer)!;
    expect(game.answer(wrong)).toBe(false);
    expect(game.question).toBe(initial);
    expect(game.score).toBeLessThanOrEqual(-1);
    expect(game.wrongCount).toBe(1);
  });

  it('cada cinco aciertos aumenta el nivel, sin destruir distractores', () => {
    const game = new MathEngine();
    for (let i = 0; i < 5; i++) {
      expect(game.answer(game.question.answer)).toBe(true);
      expect(() => game.answer(game.question.answer)).toThrow();
      game.nextQuestion();
    }
    expect(game.correctCount).toBe(5);
    expect(game.level).toBe(2);
  });

  it('habilita restas no negativas desde el nivel 3', () => {
    const game = new MathEngine();
    game.level = 3;
    const ops = new Set();
    for (let i = 0; i < 100; i++) {
      ops.add(game.nextQuestion().operator);
      expect(game.question.answer).toBeGreaterThanOrEqual(0);
    }
    expect(ops).toEqual(new Set(['+', '-']));
  });

  it('controla vidas y reinicio', () => {
    const game = new MathEngine();
    expect(game.loseLife()).toBe(false);
    expect(game.loseLife()).toBe(false);
    expect(game.loseLife()).toBe(true);
    expect(game.loseLife()).toBe(true);
    game.reset();
    expect(game.lives).toBe(3);
    expect(game.level).toBe(1);
    expect(game.score).toBe(0);
  });

  it('crea un resumen con puntuación nunca negativa y duración válida', () => {
    const game = new MathEngine();
    const wrong = game.question.options.find(n => n !== game.question.answer)!;
    game.answer(wrong);
    const summary = game.makeSummary(0.3, 'session-id');
    expect(summary.score).toBe(0);
    expect(summary.duration_seconds).toBe(1);
  });
});
