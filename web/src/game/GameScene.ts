import Phaser from 'phaser';
import { MathEngine, POINTS_PER_CORRECT, OPERATORS, type Operator, type RunSummary } from '../math/engine';
import { gameEvents } from './events';

const WIDTH = 1080;
const HEIGHT = 686;
type Phase = 'menu' | 'playing' | 'over';

interface FallingStar {
  sprite: Phaser.GameObjects.Image;
  label: Phaser.GameObjects.Text;
  number: number;
  lane: number;
  speed: number;
  fast: boolean;
}

export class GameScene extends Phaser.Scene {
  private engine = new MathEngine();
  private phase: Phase = 'menu';
  private ship!: Phaser.GameObjects.Image;
  private equationLabel!: Phaser.GameObjects.Text;
  private scoreLabel!: Phaser.GameObjects.Text;
  private levelLabel!: Phaser.GameObjects.Text;
  private lifeLabel!: Phaser.GameObjects.Text;
  private operationLabel!: Phaser.GameObjects.Text;
  private stars: FallingStar[] = [];
  private lasers: Phaser.GameObjects.Image[] = [];
  private overlay?: Phaser.GameObjects.Container;
  private keys?: Record<string, Phaser.Input.Keyboard.Key>;
  private startedAt = 0;
  private lastShotAt = 0;
  private invulnerableUntil = 0;
  private currentFeedback?: Phaser.GameObjects.Text;
  private ready = false;

  constructor() {
    super({ key: 'MathInvaders' });
  }

  preload(): void {
    const assets = import.meta.env.BASE_URL + 'assets/';
    this.load.image('background', assets + 'wallpaper.jpg');
    this.load.image('rocket', assets + 'rocket.png');
    this.load.image('laser', assets + 'laser.png');
    this.load.image('star', assets + 'star.png');
    this.load.image('heart', assets + 'heart.png');
    this.load.audio('shot', assets + 'lasser.wav');
  }

  create(): void {
    this.add.image(WIDTH / 2, HEIGHT / 2, 'background')
      .setDisplaySize(WIDTH, HEIGHT).setDepth(0);
    this.add.rectangle(WIDTH / 2, 64, 1030, 105, 0x030b21, 0.82)
      .setDepth(15).setStrokeStyle(1, 0x2f598c, 0.65);
    const font = 'VT323, monospace';
    this.equationLabel = this.add.text(35, 26, '', {
      fontFamily: font, fontSize: '62px', color: '#f4f8ff',
    }).setDepth(16);
    this.levelLabel = this.add.text(660, 24, '', {
      fontFamily: font, fontSize: '30px', color: '#97cdfd',
    }).setDepth(16);
    this.scoreLabel = this.add.text(660, 60, '', {
      fontFamily: font, fontSize: '30px', color: '#ffffff',
    }).setDepth(16);
    this.lifeLabel = this.add.text(855, 60, '', {
      fontFamily: font, fontSize: '30px', color: '#ffb3bd',
    }).setDepth(16);
    this.operationLabel = this.add.text(36, 130, '', {
      fontFamily: font, fontSize: '27px', color: '#a8ffd8',
      backgroundColor: '#071527',
    }).setDepth(16);
    this.add.text(30, HEIGHT - 38,
      'WASD: mover  |  ESPACIO: disparar  |  Móvil: arrastra y usa DISPARAR', {
        fontFamily: font, fontSize: '23px', color: '#b9cee2',
        backgroundColor: '#071323',
      }).setDepth(16);

    this.ship = this.add.image(WIDTH / 2, HEIGHT - 92, 'rocket')
      .setDisplaySize(72, 72).setDepth(9);
    this.keys = this.input.keyboard?.addKeys('W,A,S,D') as Record<string, Phaser.Input.Keyboard.Key> | undefined;
    this.input.keyboard?.on('keydown-SPACE', () => this.fire());
    this.input.keyboard?.on('keydown-ENTER', () => {
      if (this.phase !== 'playing') this.startGame();
    });
    this.input.keyboard?.on('keydown-R', () => {
      if (this.phase === 'over') this.startGame();
    });
    this.input.on('pointerdown', () => {
      if (this.phase !== 'playing') this.startGame();
    });

    this.setHud();
    this.drawOverlay('MATH INVADERS',
      'Resuelve operaciones disparando a la respuesta correcta',
      'HAZ CLIC O PULSA ENTER PARA JUGAR');
    this.ready = true;
    gameEvents.emit('ready');
  }

  private drawOverlay(title: string, detail: string, hint: string): void {
    this.overlay?.destroy();
    const font = 'VT323, monospace';
    const backdrop = this.add.rectangle(
      WIDTH / 2, HEIGHT / 2, WIDTH, HEIGHT, 0x030919, 0.87,
    );
    const heading = this.add.text(WIDTH / 2, 220, title, {
      fontFamily: font, fontSize: '94px', color: '#f8e5a0',
      shadow: { offsetX: 0, offsetY: 0, color: '#2a8eff', blur: 22, fill: true },
    }).setOrigin(0.5);
    const caption = this.add.text(WIDTH / 2, 320, detail, {
      fontFamily: font, fontSize: '35px', color: '#e7f2ff',
      align: 'center', wordWrap: { width: 850 },
    }).setOrigin(0.5);
    const action = this.add.text(WIDTH / 2, 424, hint, {
      fontFamily: font, fontSize: '34px', color: '#5affca',
    }).setOrigin(0.5);
    this.overlay = this.add.container(0, 0, [
      backdrop, heading, caption, action,
    ]).setDepth(100);
  }

  setOperators(operators: readonly Operator[]): void {
    if (this.phase === 'playing') return;
    this.engine.setOperators(operators);
    this.setHud();
  }

  startGame(): void {
    if (!this.ready) return;
    this.engine.reset();
    this.startedAt = this.time.now;
    this.lastShotAt = -1000;
    this.invulnerableUntil = 0;
    this.ship.setPosition(WIDTH / 2, HEIGHT - 92).setVisible(true);
    this.currentFeedback?.destroy();
    this.currentFeedback = undefined;
    this.overlay?.destroy();
    this.overlay = undefined;
    this.phase = 'playing';
    this.spawnWave();
    this.setHud();
    gameEvents.emit('started');
  }

  fire(): void {
    if (!this.ready || this.phase !== 'playing') return;
    if (this.time.now - this.lastShotAt < 180) return;
    this.lastShotAt = this.time.now;
    const laser = this.add.image(this.ship.x, this.ship.y - 39, 'laser')
      .setDisplaySize(16, 32).setDepth(7);
    this.lasers.push(laser);
    if (this.cache.audio.exists('shot')) {
      this.sound.play('shot', { volume: 0.19 });
    }
  }

  private spawnWave(): void {
    this.clearWave();
    const fastCount = Math.min(5, Math.floor(this.engine.level / 5));
    const fastLanes = new Set(
      Phaser.Utils.Array.Shuffle([0, 1, 2, 3, 4]).slice(0, fastCount),
    );
    this.engine.question.options.forEach((number, lane) => {
      const x = 180 * (lane + 1);
      const y = -75 - Math.random() * 260;
      const fast = fastLanes.has(lane);
      const sprite = this.add.image(x, y, 'star')
        .setDisplaySize(72, 72).setDepth(5);
      const label = this.add.text(x, y, String(number), {
        fontFamily: 'VT323, monospace',
        fontSize: number >= 100 ? '33px' : '44px',
        color: '#ffffff',
        stroke: '#0c102c',
        strokeThickness: 6,
      }).setOrigin(0.5).setDepth(6);
      this.stars.push({
        sprite, label, number, lane, fast,
        speed: (70 + (this.engine.level - 1) * 6) * (fast ? 2.2 : 1),
      });
    });
  }

  private clearWave(): void {
    this.stars.forEach(({ sprite, label }) => {
      sprite.destroy();
      label.destroy();
    });
    this.stars = [];
    this.lasers.forEach((laser) => laser.destroy());
    this.lasers = [];
  }

  private setHud(): void {
    const q = this.engine.question;
    const operationSymbol = q.operator === '*' ? '×' : q.operator === '/' ? '÷' : q.operator;
    this.equationLabel?.setText(q.left + ' ' + operationSymbol + ' ' + q.right + ' = ?');
    this.levelLabel?.setText('NIVEL ' + this.engine.level);
    this.scoreLabel?.setText('PUNTOS ' + this.engine.score);
    this.lifeLabel?.setText('VIDAS ' + '♥'.repeat(this.engine.lives));
    this.operationLabel?.setText(
      OPERATORS.map(op => {
        const symbol = op === '*' ? '×' : op === '/' ? '÷' : op;
        return symbol + ' ' + this.engine.operationPoints[op];
      }).join('    ') + '   |   ACIERTO ' +
      (POINTS_PER_CORRECT[q.operator] * this.engine.level) + ' PTS',
    );
  }

  private showFeedback(message: string, color: string, x: number, y: number): void {
    this.currentFeedback?.destroy();
    const label = this.add.text(x, y, message, {
      fontFamily: 'VT323, monospace', fontSize: '37px',
      color, stroke: '#020817', strokeThickness: 4,
    }).setOrigin(0.5).setDepth(20);
    this.currentFeedback = label;
    this.tweens.add({
      targets: label,
      y: y - 65,
      alpha: 0,
      duration: 820,
      onComplete: () => {
        if (this.currentFeedback === label) this.currentFeedback = undefined;
        label.destroy();
      },
    });
  }

  private recycle(star: FallingStar): void {
    const y = -75 - Math.random() * 230;
    star.sprite.setY(y);
    star.label.setY(y);
  }

  private processHit(star: FallingStar): void {
    const pointsForCorrect = POINTS_PER_CORRECT[this.engine.question.operator] * this.engine.level;
    const correct = this.engine.answer(star.number);
    this.showFeedback(correct ? '+' + pointsForCorrect + ' PUNTOS' : 'INCORRECTO',
      correct ? '#67ffb2' : '#ff7482', star.sprite.x, star.sprite.y);
    if (correct) {
      this.engine.nextQuestion();
      this.spawnWave();
    } else {
      this.recycle(star);
    }
    this.setHud();
  }

  private endGame(): void {
    this.phase = 'over';
    this.clearWave();
    const seconds = (this.time.now - this.startedAt) / 1000;
    const summary: RunSummary = this.engine.makeSummary(
      seconds,
      globalThis.crypto?.randomUUID?.() ?? '00000000-0000-4000-8000-000000000000',
    );
    this.drawOverlay('FIN DE LA PARTIDA',
      'PUNTOS ' + summary.score + '  |  ACIERTOS ' + summary.correct_count +
      '  |  NIVEL ' + summary.level_reached,
      'HAZ CLIC O PULSA R PARA REINICIAR');
    gameEvents.emit('finished', summary);
  }

  update(_time: number, delta: number): void {
    if (this.phase !== 'playing') return;
    const dt = Math.min(delta, 50) / 1000;
    const keys = this.keys;
    let vx = Number(Boolean(keys?.D?.isDown)) - Number(Boolean(keys?.A?.isDown));
    let vy = Number(Boolean(keys?.S?.isDown)) - Number(Boolean(keys?.W?.isDown));
    if (vx !== 0 || vy !== 0) {
      const magnitude = Math.hypot(vx, vy);
      vx /= magnitude;
      vy /= magnitude;
      this.ship.x += vx * 330 * dt;
      this.ship.y += vy * 330 * dt;
    } else if (this.input.activePointer.isDown) {
      const pointer = this.input.activePointer;
      this.ship.x += (pointer.x - this.ship.x) * Math.min(1, dt * 12);
      this.ship.y += (pointer.y - this.ship.y) * Math.min(1, dt * 12);
    }
    this.ship.x = Phaser.Math.Clamp(this.ship.x, 40, WIDTH - 40);
    this.ship.y = Phaser.Math.Clamp(this.ship.y, 165, HEIGHT - 65);

    for (const star of this.stars) {
      star.sprite.y += star.speed * dt;
      star.label.setPosition(star.sprite.x, star.sprite.y);
      if (star.sprite.y > HEIGHT + 50) this.recycle(star);
      if (this.time.now >= this.invulnerableUntil &&
          Phaser.Geom.Intersects.RectangleToRectangle(
            star.sprite.getBounds(), this.ship.getBounds(),
          )) {
        this.recycle(star);
        this.invulnerableUntil = this.time.now + 1200;
        this.engine.loseLife();
        this.setHud();
        if (this.engine.lives <= 0) {
          this.endGame();
          return;
        }
      }
    }

    this.ship.setAlpha(
      this.time.now < this.invulnerableUntil &&
        Math.floor(this.time.now / 110) % 2 === 0 ? 0.35 : 1,
    );

    for (const laser of [...this.lasers]) {
      laser.y -= 640 * dt;
      if (laser.y < -45) {
        this.removeLaser(laser);
        continue;
      }
      const hit = this.stars.find((star) =>
        Phaser.Geom.Intersects.RectangleToRectangle(
          laser.getBounds(), star.sprite.getBounds(),
        ),
      );
      if (hit) {
        this.removeLaser(laser);
        this.processHit(hit);
        // La ronda pudo cambiar; no procesar colisiones de la oleada anterior.
        return;
      }
    }
  }

  private removeLaser(laser: Phaser.GameObjects.Image): void {
    this.lasers = this.lasers.filter((candidate) => candidate !== laser);
    laser.destroy();
  }
}
