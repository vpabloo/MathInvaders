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

/**
 * Límite inclusivo de las respuestas (y de las cinco opciones).
 * Los niveles 1–3 trabajan hasta 10, luego crece por tramos de dos niveles.
 * Se limita a 999 para que los números sigan cabiendo dentro de las estrellas.
 */
export function maxAnswerForLevel(level: number): number {
  if (!Number.isInteger(level) || level < 1) throw new RangeError('Nivel inválido');
  if (level <= 3) return 10;
  if (level <= 7) return 10 + 5 * Math.ceil((level - 3) / 2);
  return Math.min(999, 20 + 10 * Math.ceil((level - 7) / 2));
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
    const limit = maxAnswerForLevel(this.level);
    // En niveles avanzados predominan cifras acordes al rango desbloqueado.
    const targetMinimum = limit <= 10 ? 0 : Math.floor(limit * 0.35);
    let left = 0;
    let right = 0;
    let operator: Operator = '+';
    let answer = 0;

    for (let attempt = 0; attempt < 40; attempt++) {
      operator = this.selectedOperators[integer(this.random, 0, this.selectedOperators.length - 1)];
      switch (operator) {
        case '+':
          answer = integer(this.random, 2, limit);
          left = integer(this.random, 1, answer - 1);
          right = answer - left;
          break;
        case '-':
          answer = integer(this.random, 0, limit);
          left = integer(this.random, Math.max(1, answer), limit);
          right = left - answer;
          break;
        case '*': {
          // Dos factores reales, sin usar ×1, con producto dentro del rango.
          const factorLimit = Math.min(
            Math.floor(limit / 2),
            Math.max(5, Math.ceil(Math.sqrt(limit) * 1.6)),
          );
          left = integer(this.random, 2, factorLimit);
          right = integer(this.random, 2, Math.min(factorLimit, Math.floor(limit / left)));
          answer = left * right;
          break;
        }
        case '/': {
          // Cociente entero; divisores pequeños al inicio y mayores después.
          const maxDivisor = limit <= 10
            ? 3
            : Math.min(12, 3 + Math.floor((this.level - 1) / 2));
          right = integer(this.random, 2, maxDivisor);
          const maxQuotient = limit <= 10
            ? Math.min(limit, Math.floor(20 / right))
            : limit;
          answer = integer(this.random, 1, maxQuotient);
          left = right * answer;
          break;
        }
      }

      const isPrevious = previous && previous.left === left &&
        previous.right === right && previous.operator === operator;
      if (!isPrevious && answer >= targetMinimum) break;
    }

    // Nunca mostrar distractores superiores al máximo del nivel.
    const radius = Math.max(5, Math.min(12, Math.floor(limit / 4)));
    const lower = Math.max(0, answer - radius);
    const upper = Math.min(limit, answer + radius);
    const distractors = shuffle(
      Array.from({ length: upper - lower + 1 }, (_, i) => lower + i)
        .filter((number) => number !== answer),
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
