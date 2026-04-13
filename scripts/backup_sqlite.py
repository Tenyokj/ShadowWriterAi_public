from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil

from bot.config import DB_PATH, settings


def main() -> None:
    if settings.database_url:
        raise SystemExit(
            "SQLite backup is disabled because DATABASE_URL is configured. "
            "Use Supabase / Postgres backups for the production database."
        )

    source = Path(DB_PATH)
    if not source.exists():
        raise SystemExit(f"Database file not found: {source}")

    backup_dir = Path(settings.db_backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = backup_dir / f"shadow_writer_{timestamp}.sqlite3"
    shutil.copy2(source, target)
    print(target)


if __name__ == "__main__":
    main()
