# Spec: cv-agent (fase 1)

## Objetivo
Guardar mi información profesional (experiencias, proyectos, skills) en una BD. Un agente usa esos datos para responder peticiones de proyecto (`ProjectRequest`).

## Alcance de la fase 1
Solo la **persistencia de datos**. El agente y el endpoint quedan para fases siguientes.

## Datos

| Entidad | Campos principales |
|---|---|
| **Skill** | nombre (único), categoría, nivel (opcional) |
| **Experience** | empresa, rol, descripción, ubicación (opcional), fecha inicio, fecha fin (opcional) |
| **Project** | nombre, descripción, mi rol (opcional), fechas (opcionales), experiencia asociada (opcional) |
| **ProjectRequest** | título, descripción, estado (`pending`, `processing`, `done`, `failed`), fecha de creación |

**Relaciones**
- Una Experience tiene muchas Skills, y una Skill puede estar en muchas Experiences.
- Un Project tiene muchas Skills, y una Skill puede estar en muchos Projects.
- Un Project puede pertenecer a una Experience, pero no es obligatorio.

## Pasos de desarrollo

1. **Dependencias**: añadir `sqlmodel`, `asyncpg`, `pydantic-settings` y `aiosqlite` (dev).
   *Hecho cuando:* `uv sync` termina sin errores.
2. **`src/models.py`**: las 4 entidades y las 2 tablas de relación.
   *Hecho cuando:* `mypy` en modo strict pasa.
3. **`src/db.py`**: lee la config del `.env`, crea el engine async y la sesión.
   *Hecho cuando:* construye la URL de Postgres a partir de `POSTGRES_*`.
4. **Tests** (con SQLite en memoria):
   - Se pueden crear y leer Skill, Experience y Project.
   - La relación con Skills funciona en ambos sentidos.
   - No se pueden duplicar nombres de Skill.
   - Una `ProjectRequest` nueva nace en `pending`.
   *Hecho cuando:* `pytest` pasa, incluido el test que ya existía.
5. **Calidad**: `ruff` y `pre-commit` en verde.

## Migraciones (Alembic)
El esquema de la BD lo gestiona Alembic; la app ya no crea tablas al arrancar.

- **Conexión:** `DATABASE_URL` en el `.env` (si existe) o, si no, las variables `POSTGRES_*`.
- **Aplicar el esquema:** `uv run alembic upgrade head`.
- **Cambiar un modelo:** editar `src/models.py` → `uv run alembic revision --autogenerate -m "descripción"` → revisar el archivo generado → `uv run alembic upgrade head`.
- **Deshacer:** `uv run alembic downgrade -1`.
- **Control:** un test falla si los modelos difieren de las migraciones.

