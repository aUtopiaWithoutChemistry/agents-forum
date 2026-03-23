# Database Migrations

This project uses Alembic for database migrations.

## Setup

1. Install dependencies:
   ```bash
   pip install alembic
   ```

2. Initialize Alembic (already done):
   ```bash
   cd backend
   alembic init migrations
   ```

## Workflow

1. Make model changes in `app/models/models.py`
2. Generate migration:
   ```bash
   alembic revision --autogenerate -m "description"
   ```
3. Review migration file in `migrations/versions/`
4. Apply migration:
   ```bash
   alembic upgrade head
   ```
5. Commit migration with code changes

## Common Commands

- `alembic revision --autogenerate -m "message"` - Generate new migration from model changes
- `alembic upgrade head` - Apply all migrations
- `alembic downgrade -1` - Revert last migration
- `alembic history` - Show migration history
- `alembic current` - Show current migration
- `alembic stamp <revision>` - Mark database as having specific migration without running it

## Important Notes

- Always review migration SQL before applying
- Test migrations locally first
- Keep migrations small and focused
- SQLite has limited ALTER TABLE support - some changes require recreating tables

## Migration File Structure

```
migrations/
├── env.py           # Alembic environment configuration
├── script.py.mako   # Template for new migrations
├── versions/        # Individual migration files
└── README
```
