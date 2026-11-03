/** Motor matemático, independiente de Phaser y del navegador. */
export type Operator = '+' | '-';
export type RandomSource = () => number;

export interface Question {
  left: number;
  right: number;
  operator: Operator;
  answer: number;
  options: number[];
}

export interface RunSummary {
  score: number;
  correct_count: number;
  wrong_count: number;
  level_reached: number;
  duration_seconds: number;
  client_run_id: string;
}

const integer = (rng: RandomSource, min: number, max: number) =>
  Math.floor(rng() * (max - min + 1)) + min;

export function shuffle<T>(items: T[], rng: RandomSource): T[] {
  const result = [...items];
  for (let index = result.length - 1; index > 0; index--) {
    const next = integer(rng, 0, index);
    [result[index], result[next]] = [result[next], result[index]];
  }
  return result;
}

export class MathEngine {
  score = 0;
  lives = 3;
  level = 1;
  correctCount = 0;
  wrongCount = 0;
  question!: Question;
  private completed = false;
  private readonly random: RandomSource;

  constructor(random: RandomSource = Math.random) {
    this.random = random;
    this.nextQuestion();
  }

  reset(): void {
    this.score = 0;
    this.lives = 3;
    this.level = 1;
    this.correctCount = 0;
    this.wrongCount = 0;
    this.completed = false;
    this.nextQuestion();
  }

  nextQuestion(): Question {
    const previous = this.question;
    let left = 0;
    let right = 0;
    let operator: Operator = '+';
    let answer = 0;

    for (let attempt = 0; attempt < 30; attempt++) {
      operator = this.level < 3 || this.random() < 0.5 ? '+' : '-';
      if (operator === '+') {
        left = integer(this.random, 1, 5);
        right = integer(this.random, 1, 5);
        answer = left + right;
      } else {
        left = integer(this.random, 1, 10);
        right = integer(this.random, 0, left);
        answer = left - right;
      }
      if (!previous || previous.left !== left ||
          previous.right !== right || previous.operator !== operator) break;
    }

    const distractors = shuffle(
      Array.from({ length: 11 }, (_, index) => index).filter((n) => n !== answer),
      this.random,
    ).slice(0, 4);
    this.question = {
      left, right, operator, answer,
      options: shuffle([answer, ...distractors], this.random),
    };
    this.completed = false;
    return this.question;
  }

  answer(value: number): boolean {
    if (this.completed) throw new Error('La ronda ya terminó');
    if (!this.question.options.includes(value)) throw new Error('Opción inválida');

    if (value === this.question.answer) {
      this.score += Math.max(1, value) * this.level;
      this.correctCount += 1;
      this.level = 1 + Math.floor(this.correctCount / 5);
      this.completed = true;
      return true;
    }

    this.score -= Math.max(1, Math.floor(Math.abs(value) / 2));
    this.wrongCount += 1;
    return false;
  }

  loseLife(): boolean {
    this.lives = Math.max(0, this.lives - 1);
    return this.lives === 0;
  }

  makeSummary(seconds: number, runId: string): RunSummary {
    return {
      score: Math.max(0, this.score),
      correct_count: this.correctCount,
      wrong_count: this.wrongCount,
      level_reached: this.level,
      duration_seconds: Math.max(1, Math.floor(seconds)),
      client_run_id: runId,
    };
  }
}
