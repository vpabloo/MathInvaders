import { describe, expect, it } from 'vitest';
import { movementVector, shouldPreventGameScroll } from './keyboard';

const idle = { up: false, down: false, left: false, right: false };

describe('controles de teclado', () => {
  it('mueve con los cuatro sentidos', () => {
    expect(movementVector({ ...idle, up: true })).toEqual({ x: 0, y: -1 });
    expect(movementVector({ ...idle, down: true })).toEqual({ x: 0, y: 1 });
    expect(movementVector({ ...idle, left: true })).toEqual({ x: -1, y: 0 });
    expect(movementVector({ ...idle, right: true })).toEqual({ x: 1, y: 0 });
  });

  it('normaliza diagonales y cancela movimientos contrarios', () => {
    const diagonal = movementVector({ ...idle, up: true, right: true });
    expect(Math.hypot(diagonal.x, diagonal.y)).toBeCloseTo(1, 10);
    expect(diagonal.x).toBeGreaterThan(0);
    expect(diagonal.y).toBeLessThan(0);
    expect(movementVector({ ...idle, left: true, right: true })).toEqual({ x: 0, y: 0 });
  });

  it('evita el scroll del navegador con espacio y flechas', () => {
    for (const code of ['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight']) {
      expect(shouldPreventGameScroll(code)).toBe(true);
    }
    expect(shouldPreventGameScroll('KeyW')).toBe(false);
    expect(shouldPreventGameScroll('Enter')).toBe(false);
  });
});
