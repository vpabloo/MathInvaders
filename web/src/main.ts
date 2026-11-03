import Phaser from 'phaser';
import './style.css';
import { GameScene } from './game/GameScene';
import { gameEvents } from './game/events';
import type { RunSummary } from './math/engine';
import {
  backend, currentUser, fetchMyBest, fetchSchoolLeaderboard,
  getProfile, joinSchool, signIn, signOut, signUp, submitRun,
} from './services/backend';
import { readLocalRecord, saveLocalRun } from './services/storage';

function el<T extends HTMLElement>(id: string): T {
  const value = document.getElementById(id);
  if (!value) throw new Error('Elemento no encontrado: ' + id);
  return value as T;
}

const startButton = el<HTMLButtonElement>('start-button');
const fireButton = el<HTMLButtonElement>('fire-button');
const accountStatus = el<HTMLElement>('session-status');
const accountForm = el<HTMLFormElement>('auth-form');
const disabledMessage = el<HTMLElement>('auth-disabled');
const signedInPanel = el<HTMLElement>('signed-in');
const authFeedback = el<HTMLElement>('auth-feedback');
const schoolForm = el<HTMLFormElement>('school-form');
const schoolMembership = el<HTMLElement>('school-membership');
const nameField = el<HTMLInputElement>('student-name');
const emailField = el<HTMLInputElement>('student-email');
const passwordField = el<HTMLInputElement>('student-password');
const schoolCode = el<HTMLInputElement>('school-code');
const schoolTable = el<HTMLTableSectionElement>('leaderboard-body');

const pretty = (value: number) => value.toLocaleString('es-MX');

function showLocalRecord(): void {
  const local = readLocalRecord();
  el<HTMLElement>('best-score').textContent = pretty(local.best);
  el<HTMLElement>('games-count').textContent = pretty(local.games);
  el<HTMLElement>('total-score').textContent = pretty(local.total);
}

function message(text: string): void {
  authFeedback.textContent = text;
}

async function updateLeaderboard(): Promise<void> {
  if (!backend) {
    schoolTable.replaceChildren();
    const row = schoolTable.insertRow();
    const cell = row.insertCell();
    cell.colSpan = 4;
    cell.textContent = 'El ranking estará disponible al conectar la base de datos.';
    return;
  }

  try {
    const schools = await fetchSchoolLeaderboard();
    schoolTable.replaceChildren();
    if (!schools.length) {
      const row = schoolTable.insertRow();
      const cell = row.insertCell();
      cell.colSpan = 4;
      cell.textContent = 'Aún no hay instituciones registradas.';
    }
    for (const [index, school] of schools.entries()) {
      const row = schoolTable.insertRow();
      const values = [
        String(index + 1),
        school.school_name,
        pretty(Number(school.student_count)),
        pretty(Number(school.total_score)),
      ];
      for (const value of values) row.insertCell().textContent = value;
    }
  } catch {
    schoolTable.replaceChildren();
    const row = schoolTable.insertRow();
    const cell = row.insertCell();
    cell.colSpan = 4;
    cell.textContent = 'No fue posible cargar el ranking.';
  }
}

async function refreshSession(): Promise<void> {
  if (!backend) {
    accountForm.hidden = true;
    signedInPanel.hidden = true;
    disabledMessage.hidden = false;
    accountStatus.textContent = 'Modo invitado';
    el<HTMLElement>('account-tag').textContent = 'PRÓXIMAMENTE';
    return;
  }
  const user = await currentUser();
  accountForm.hidden = Boolean(user);
  signedInPanel.hidden = !user;
  disabledMessage.hidden = true;
  if (!user) {
    accountStatus.textContent = 'Modo invitado';
    return;
  }
  try {
    const profile = await getProfile();
    accountStatus.textContent = 'Sesión de alumno';
    el<HTMLElement>('welcome-message').textContent = '¡Hola, ' +
      (profile?.display_name ?? 'estudiante') + '!';
    el<HTMLElement>('online-best').textContent = 'Récord en línea: ' +
      pretty(await fetchMyBest()) + ' puntos';
    const linkedSchool = profile?.school_id;
    schoolForm.hidden = Boolean(linkedSchool);
    schoolMembership.hidden = !linkedSchool;
    if (linkedSchool) {
      const schools = await fetchSchoolLeaderboard();
      const name = schools.find((school) => school.school_id === linkedSchool)?.school_name;
      schoolMembership.textContent = name
        ? 'Institución vinculada: ' + name
        : 'Ya perteneces a una institución.';
    }
  } catch (error) {
    message(error instanceof Error ? error.message : 'No se pudo cargar el perfil.');
  }
}

async function withFeedback(operation: () => Promise<void>): Promise<void> {
  message('Procesando...');
  try {
    await operation();
    await refreshSession();
    await updateLeaderboard();
  } catch (error) {
    message(error instanceof Error ? error.message : 'Ocurrió un error de conexión.');
  }
}

accountForm.addEventListener('submit', (event) => {
  event.preventDefault();
  void withFeedback(async () => {
    await signIn(emailField.value.trim(), passwordField.value);
    passwordField.value = '';
    message('Sesión iniciada correctamente.');
  });
});

el<HTMLButtonElement>('register-button').addEventListener('click', () => {
  void withFeedback(async () => {
    const displayName = nameField.value.trim();
    if (displayName.length < 2) throw new Error('Escribe un nombre o alias de al menos 2 caracteres.');
    if (!emailField.reportValidity() || !passwordField.reportValidity()) return;
    const confirm = await signUp(emailField.value.trim(), passwordField.value, displayName);
    passwordField.value = '';
    message(confirm
      ? 'Revisa tu correo para confirmar el registro antes de iniciar sesión.'
      : 'Registro completado; tu sesión está activa.');
  });
});

el<HTMLButtonElement>('logout-button').addEventListener('click', () => {
  void withFeedback(async () => {
    await signOut();
    message('Sesión cerrada.');
  });
});

schoolForm.addEventListener('submit', (event) => {
  event.preventDefault();
  void withFeedback(async () => {
    if (!schoolCode.value.trim()) throw new Error('Introduce el código de la institución.');
    await joinSchool(schoolCode.value);
    schoolCode.value = '';
    message('Vinculación completada.');
  });
});

const scene = new GameScene();
gameEvents.on('ready', () => {
  startButton.disabled = false;
  startButton.textContent = '▶ INICIAR PARTIDA';
});
gameEvents.on('started', () => {
  startButton.textContent = '↻ REINICIAR PARTIDA';
});
gameEvents.on('finished', (summary: RunSummary) => {
  void saveFinishedRun(summary);
});

async function saveFinishedRun(summary: RunSummary): Promise<void> {
  const local = saveLocalRun(summary);
  showLocalRecord();
  const notice = el<HTMLElement>('save-message');
  notice.textContent = 'Partida guardada. Tu récord local es ' + pretty(local.best) + ' puntos.';
  if (!backend) return;

  try {
    const user = await currentUser();
    if (!user) {
      notice.textContent += ' Inicia sesión antes de jugar para registrar puntos en línea.';
      return;
    }
    await submitRun(summary);
    notice.textContent += ' Puntuación registrada en tu cuenta.';
    await refreshSession();
    await updateLeaderboard();
  } catch (error) {
    notice.textContent += ' No se pudo sincronizar en línea: ' +
      (error instanceof Error ? error.message : 'error de conexión');
  }
}

startButton.addEventListener('click', () => scene.startGame());
fireButton.addEventListener('pointerdown', (event) => {
  event.preventDefault();
  scene.fire();
});
window.addEventListener('keydown', (event) => {
  if (event.code === 'Space' && event.target instanceof HTMLElement &&
      !['INPUT', 'TEXTAREA', 'BUTTON'].includes(event.target.tagName)) {
    event.preventDefault();
  }
});

showLocalRecord();
void refreshSession();
void updateLeaderboard();

document.fonts.ready.then(() => {
  new Phaser.Game({
    type: Phaser.AUTO,
    width: 1080,
    height: 686,
    parent: 'game',
    backgroundColor: '#030819',
    scale: {
      mode: Phaser.Scale.FIT,
      autoCenter: Phaser.Scale.CENTER_BOTH,
      width: 1080,
      height: 686,
    },
    render: { antialias: true },
    scene: [scene],
    input: { activePointers: 2 },
  });
});
