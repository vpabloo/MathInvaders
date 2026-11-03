# MathInvaders Web · Phaser + TypeScript

Versión para navegador de MathInvaders. La versión original de escritorio permanece en la raíz del repositorio.

## Desarrollo local

Requiere Node.js 20.19+ (recomendado Node 22).

    cd web
    npm install
    npm run dev

Abrir http://localhost:5173. Para verificar:

    npm run typecheck
    npm run test
    npm run build

El juego funciona como **invitado sin base de datos**. El récord y las partidas se guardan localmente en el navegador (no se transfieren entre dispositivos).

## Modalidades matemáticas y puntuación

El menú muestra cuatro casillas y permite seleccionar **una o varias** modalidades antes de empezar. La selección se guarda en el navegador y queda bloqueada mientras dure una partida.

| Modalidad | Puntos por respuesta correcta |
| --- | ---: |
| Suma (+) | 10 × nivel |
| Resta (−) | 20 × nivel |
| Multiplicación (×) | 30 × nivel |
| División (÷) | 40 × nivel |

- Cada 5 aciertos se sube un nivel. Las modalidades seleccionadas se mezclan aleatoriamente desde el nivel 1; ninguna requiere desbloqueo.
- Las restas no producen resultados negativos; las divisiones siempre son exactas, sin cero en el divisor.
- Una respuesta incorrecta resta del marcador global y del **marcador específico de la operación** el máximo entre 1 y la mitad entera de la opción incorrecta.
- En pantalla se ven tanto el total como el subtotal por operación; la sección **Mi progreso** acumula los puntos netos por modalidad entre partidas. Los récords locales anteriores se conservan sin desglose histórico.
- El resumen de cada partida registra selected_operators y operation_points. El ranking escolar conserva la regla de **mejor partida por alumno** (comparación ponderada por dificultad).

Si tu instancia Supabase ya ejecutó el esquema anterior, aplica una sola vez la migración de web/supabase/migrations/20261103_operation_modalities.sql. En una instalación nueva, basta el schema.sql actualizado.

## Publicación (GitHub Pages)

El workflow .github/workflows/deploy-web.yml compila la carpeta web/ y despliega web/dist desde la rama main. Incluye la ruta base /MathInvaders/ para recursos estáticos.

1. En el repositorio GitHub: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. Integrar la rama feature/phaser-web en main y revisar el workflow de publicación en **Actions**.
3. Sitio esperado: https://vpabloo.github.io/MathInvaders/

La primera publicación puede requerir habilitar Pages manualmente. El workflow se puede ejecutar desde **Actions → Publicar MathInvaders Web → Run workflow**.

Para otros dominios/servidores, compilar desde web/ con DEPLOY_BASE_PATH=/ npm run build; el directorio dist/ es estático y puede servirse desde cualquier servidor HTTPS.

## Cuentas y récords en línea (opcional)

La aplicación soporta **Supabase Auth + PostgreSQL** sin servidor de juegos propio.

1. Crear un proyecto en Supabase, activar email/password y **confirmación por correo**. Configurar Site URL y Redirect URLs para incluir https://vpabloo.github.io/MathInvaders/ (o tu dominio final).
2. Ejecutar web/supabase/schema.sql en el SQL Editor de Supabase (como administrador). Si ya se había instalado la base, ejecutar la migración indicada en **Modalidades matemáticas y puntuación**.
3. Crear escuelas o academias y códigos privados mediante el ejemplo SQL del final del archivo. Entregar cada código únicamente al responsable de la institución.
4. En desarrollo: copiar .env.example a .env.local y configurar VITE_SUPABASE_URL y VITE_SUPABASE_ANON_KEY.
5. Para GitHub Pages: crear las **Repository Variables** VITE_SUPABASE_URL y VITE_SUPABASE_ANON_KEY en Settings → Secrets and variables → Actions → Variables. Se incorporan durante la compilación. Son claves públicas del cliente; **nunca** poner service_role ni secretos privados.
6. Ejecutar de nuevo el workflow de publicación.

Con Supabase conectado, la interfaz permite registro e inicio de sesión, vinculación a **una** escuela mediante código, envío de puntuaciones al terminar cada partida y ranking agregado de instituciones. Una escuela suma **el récord máximo de cada alumno**, no todas sus partidas; esto evita premiar la repetición sin progreso. Los datos de estudiantes no se muestran públicamente.

Sin credenciales, los formularios de registro se ocultan y se juega como invitado.

## Seguridad y menores de edad

**IMPORTANTE:** el puntaje se calcula en el navegador y puede falsificarse manipulando el cliente. Hay comprobaciones de formato y límites básicos en SQL, pero **no hay antitrampas robusto**. No usar el ranking para premios, calificaciones ni competencias formales sin validación de partidas desde servidor (preguntas firmadas, eventos verificables y tiempos comprobables).

Antes de activar cuentas para menores: definir política de privacidad, consentimiento adecuado de tutores, retención/eliminación de datos y quién administra las instituciones. Solo se solicita alias y correo, no nombre completo obligatorio; el ranking solo publica nombres y cifras agregadas de instituciones. Se recomienda no habilitar el registro hasta completar estos requisitos.

No publicar códigos de inscripción en URLs, repositorios ni registros de consola.

## Arquitectura

    web/src/math/engine.ts       # Reglas y puntuación, sin Phaser
    web/src/math/engine.test.ts  # Pruebas automáticas
    web/src/game/GameScene.ts    # Render, teclado y táctil, colisiones, audio
    web/src/services/storage.ts  # Récord local
    web/src/services/backend.ts  # Cuentas, instituciones, resultados opcionales
    web/supabase/schema.sql      # PostgreSQL, RLS y ranking
    web/public/assets/          # Imágenes, audio y fuentes originales

Phaser dibuja el juego; el motor matemático es independiente y testeable con Vitest.
