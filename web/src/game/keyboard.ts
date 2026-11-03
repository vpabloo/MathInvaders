/** Normaliza teclado WASD y flechas; función pura para pruebas. */
export interface DirectionKeys {
  up: boolean;
  down: boolean;
  left: boolean;
  right: boolean;
}

export function movementVector(keys: DirectionKeys): { x: number; y: number } {
  const x = Number(keys.right) - Number(keys.left);
  const y = Number(keys.down) - Number(keys.up);
  const length = Math.hypot(x, y);
  return length ? { x: x / length, y: y / length } : { x: 0, y: 0 };
}

export function shouldPreventGameScroll(code: string): boolean {
  return ['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(code);
}
