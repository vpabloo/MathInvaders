/** Motor matemático puro: modalidades, preguntas y puntuaciones sin Phaser. */
export type Operator = '+' | '-' | '*' | '/';
export type RandomSource = () => number;

export const OPERATORS: readonly Operator[] = ['+', '-', '*', '/'];
export const POINTS_PER_CORRECT: Readonly<Record<Operator, number>> = {
  '+': 10,
  '-': 20,
  '*': 30,
  '/': 40,
};
export const OPERATION_NAMES: Readonly<Record<Operator, string>> = {
  '+': 'Suma',
  '-': 'Resta',
  '*': 'Multiplicación',
  '/': 'División',
};

export type OperationPoints = Record<Operator, number>;

export const emptyOperationPoints = (): OperationPoints =>
  ({ '+': 0, '-': 0, '*': 0, '/': 0 });

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
  selected_operators: Operator[];
  operation_points: OperationPoints;
}

const integer = (rng: RandomSource, min: number, max: number): number =>
  Math.floor(rng() * (max - min + 1)) + min;

export function shuffle<T>(items: T[], rng: RandomSource): T[] {
  const result = [...items];
  for (let index = result.length - 1; index > 0; index--) {
    const next = integer(rng, 0, index);
    [result[index], result[next]] = [result[next], result[index]];
  }
  return result;
}

export function normalizeOperators(values: readonly string[]): Operator[] {
  const selected = OPERATORS.filter((op) => values.includes(op));
  if (!selected.length) throw new Error('Selecciona al menos una modalidad');
  return selected;
}

export class MathEngine {
  score = 0;
  lives = 3;
  level = 1;
  correctCount = 0;
  wrongCount = 0;
  operationPoints: OperationPoints = emptyOperationPoints();
  selectedOperators: Operator[];
  question!: Question;
  private completed = false;
  private readonly random: RandomSource;

  constructor(random: RandomSource = Math.random, operators: readonly Operator[] = ['+']) {
    this.random = random;
    this.selectedOperators = normalizeOperators(operators);
    this.nextQuestion();
  }

  /** Solo debe cambiarse fuera de una partida; conserva la selección al reiniciar. */
  setOperators(operators: readonly Operator[]): void {
    this.selectedOperators = normalizeOperators(operators);
    this.nextQuestion();
  }

  reset(): void {
    this.score = 0;
    this.lives = 3;
    this.level = 1;
    this.correctCount = 0;
    this.wrongCount = 0;
    this.operationPoints = emptyOperationPoints();
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
      operator = this.selectedOperators[integer(this.random, 0, this.selectedOperators.length - 1)];
      switch (operator) {
        case '+':
          left = integer(this.random, 1, 9);
          right = integer(this.random, 1, 9);
          answer = left + right;
          break;
        case '-':
          left = integer(this.random, 1, 18);
          right = integer(this.random, 0, left);
          answer = left - right;
          break;
        case '*':
          left = integer(this.random, 1, 9);
          right = integer(this.random, 1, 9);
          answer = left * right;
          break;
        case '/': {
          // Producto construido de un cociente entero; sin cero ni decimales.
          right = integer(this.random, 1, 9);
          answer = integer(this.random, 1, 9);
          left = right * answer;
          break;
        }
      }
      if (!previous || previous.left !== left ||
          previous.right !== right || previous.operator !== operator) break;
    }

    // Distractores próximos a la respuesta: funcionan incluso si es > 10.
    const lower = Math.max(0, answer - 12);
    const distractors = shuffle(
      Array.from({ length: answer + 13 - lower }, (_, i) => lower + i)
        .filter((n) => n !== answer),
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

    const operator = this.question.operator;
    if (value === this.question.answer) {
      const earned = POINTS_PER_CORRECT[operator] * this.level;
      this.score += earned;
      this.operationPoints[operator] += earned;
      this.correctCount += 1;
      this.level = 1 + Math.floor(this.correctCount / 5);
      this.completed = true;
      return true;
    }

    const penalty = Math.max(1, Math.floor(Math.abs(value) / 2));
    this.score -= penalty;
    this.operationPoints[operator] -= penalty;
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
      selected_operators: [...this.selectedOperators],
      operation_points: { ...this.operationPoints },
    };
  }
}
