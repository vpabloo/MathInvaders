"""Reglas y estado del juego. No depende de Pygame ni de la interfaz gráfica."""

from dataclasses import dataclass
import random


@dataclass(frozen=True)
class Equation:
    left: int
    right: int
    operator: str

    @property
    def answer(self) -> int:
        if self.operator == "+":
            return self.left + self.right
        if self.operator == "-":
            return self.left - self.right
        raise ValueError(f"Operador no soportado: {self.operator}")

    @property
    def label(self) -> str:
        return f"{self.left} {self.operator} {self.right} = ?"


class MathEngine:
    """Controla preguntas, puntuación, vidas, niveles y respuestas."""

    def __init__(self, rng=None, questions_per_level=5, initial_lives=3):
        if questions_per_level < 1 or initial_lives < 1:
            raise ValueError("La configuración debe ser positiva")
        self.rng = rng or random.Random()
        self.questions_per_level = questions_per_level
        self.initial_lives = initial_lives
        self.reset()

    def reset(self):
        self.score = 0
        self.lives = self.initial_lives
        self.level = 1
        self.correct_answers = 0
        self.wrong_answers = 0
        self.equation = None
        self.choices = ()
        self._completed = False
        self.next_round()

    def _make_equation(self):
        # Los primeros dos niveles usan únicamente sumas sencillas.
        if self.level < 3 or self.rng.choice((True, False)):
            return Equation(self.rng.randint(1, 5), self.rng.randint(1, 5), "+")
        left = self.rng.randint(1, 10)
        return Equation(left, self.rng.randint(0, left), "-")

    def next_round(self):
        previous = self.equation
        for _ in range(30):
            candidate = self._make_equation()
            if candidate != previous:
                break
        self.equation = candidate
        correct = self.equation.answer
        distractors = [value for value in range(11) if value != correct]
        options = [correct, *self.rng.sample(distractors, 4)]
        self.rng.shuffle(options)
        self.choices = tuple(options)
        self._completed = False
        return self.equation

    def submit(self, answer):
        """Devuelve True al acertar. No cambia de pregunta automáticamente."""
        if self._completed:
            raise RuntimeError("La pregunta ya se resolvió; inicia una ronda nueva")
        if answer == self.equation.answer:
            self.score += max(1, self.equation.answer) * self.level
            self.correct_answers += 1
            self.level = 1 + self.correct_answers // self.questions_per_level
            self._completed = True
            return True
        self.score -= max(1, abs(answer) // 2)
        self.wrong_answers += 1
        return False

    def lose_life(self):
        self.lives = max(0, self.lives - 1)
        return self.lives == 0
