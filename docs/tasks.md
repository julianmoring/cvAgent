# Tareas: cv-agent (fase 1)

Basadas en `docs/spec.md`. Cada tarea es un corte vertical: entrega algo que se puede probar (una llamada a un endpoint), no solo configuración.

**Reglas**
- Menos de 400 líneas por tarea (código + tests).
- Estimación de tokens: ~12 tokens por línea de código y ~3x esa cifra con lectura de contexto y edición.
- Cada tarea termina con tests y `ruff`, `mypy` y `pytest` en verde.

| # | Tarea | Líneas | Tokens (código / total) |
|---|---|---|---|
| 1 | Health con BD | ~110 | ~1.3k / ~4k |
| 2 | Skills | ~140 | ~1.7k / ~5k |
| 3 | Experiences | ~180 | ~2.2k / ~6.5k |
| 4 | Projects | ~190 | ~2.3k / ~7k |
| 5 | ProjectRequests | ~130 | ~1.6k / ~5k |
| 6 | Migraciones (Alembic) | ~330 | ~4k / ~12k |

## 1. Health con BD
Instala `sqlmodel`, `asyncpg`, `pydantic-settings`. Crea `src/db.py` (config desde `.env`, engine async, sesión) y `GET /health` en `src/api/main.py`.
- **Entrega:** `GET /health` → `{"status": "ok", "db": true}`.
- **Hecho cuando:** el test consulta `/health` contra Postgres y responde 200 con `db: true`.

## 2. Skills
Crea `Skill` en `src/models.py` y los endpoints `POST /skills` y `GET /skills`.
- **Entrega:** crear y listar skills por HTTP.
- **Hecho cuando:**
  - `POST /skills` devuelve 201 con la skill creada.
  - Repetir el mismo nombre devuelve 409.
  - `GET /skills` devuelve la lista.

## 3. Experiences
Crea `Experience` y la tabla de relación con Skill. Endpoints `POST /experiences` (acepta nombres de skills) y `GET /experiences`.
- **Entrega:** guardar una experiencia con sus skills y leerla de vuelta.
- **Hecho cuando:**
  - `POST` con skills existentes las enlaza.
  - `GET /experiences` devuelve cada experiencia con sus skills.
  - Una skill inexistente devuelve 422.

## 4. Projects
Crea `Project`, su relación con Skill y la FK opcional a Experience. Endpoints `POST /projects` y `GET /projects`.
- **Entrega:** guardar un proyecto con skills y, opcionalmente, su experiencia.
- **Hecho cuando:**
  - Un proyecto con `experience_id` válido se guarda y se devuelve con su experiencia.
  - Un `experience_id` inexistente devuelve 422.
  - `GET /projects` devuelve las skills de cada proyecto.

## 5. ProjectRequests
Crea `ProjectRequest` con su estado y fecha de creación. Endpoints `POST /project-requests` y `GET /project-requests/{id}`.
- **Entrega:** registrar una petición y consultar su estado.
- **Hecho cuando:**
  - `POST` devuelve 201 con `status: "pending"` y `created_at`.
  - `GET /{id}` devuelve la petición.
  - Un id inexistente devuelve 404.

## 6. Migraciones (Alembic)
Añade `alembic`, la carpeta `migrations/` (plantilla async), la migración inicial con las 6 tablas y soporte de `DATABASE_URL`. Se elimina la creación de tablas al arrancar la app.
- **Entrega:** `alembic upgrade head` crea todas las tablas en una BD vacía.
- **Hecho cuando:**
  - Un test aplica `upgrade head` sobre una base de Postgres vacía y existen las 6 tablas.
  - Un test falla si los modelos difieren de las migraciones.
  - `downgrade base` deja la BD vacía.
  - `ruff`, `mypy` y `pytest` en verde.

