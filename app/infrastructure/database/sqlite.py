from __future__ import annotations

from pathlib import Path
import aiosqlite
from app.domain import ReviewRepository, CodeReview


def _row_to_review(row: aiosqlite.Row) -> CodeReview:
    """Map a database row to a CodeReview domain entity."""
    return CodeReview(
        id=row["id"],
        original_code=row["original_code"],
        language=row["language"],
        annotated_code=row["annotated_code"],
        explanation=row["explanation"],
        provider=row["provider"],
        model=row["model"],
        created_at=row["created_at"],
    )


class SQLiteReviewRepository(ReviewRepository):
    """Async SQLite-backed review repository using aiosqlite

    The table is created automatically on first use if it does not exists.
    """

    def __init__(self, db_path: str = "reviews.db") -> None:
        self._db_path = db_path
        self._initialized = False

    async def _ensure_table(self) -> None:
        if self._initialized:
            return

        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id TEXT PRIMARY KEY,
                    original_code TEXT NOT NULL,
                    language TEXT,
                    annotated_code TEXT NOT NULL,
                    explanation TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )                 
            """)
            await db.commit()
        self._initialized = True

    async def save(self, review: CodeReview) -> CodeReview:
        await self._ensure_table()
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            await db.execute(
                """
                INSERT INTO reviews(
                    id, original_code, language, annotated_code,
                    explanation, provider, model, created_at  
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    str(review.id),
                    review.original_code,
                    review.language,
                    review.annotated_code,
                    review.explanation,
                    review.provider,
                    review.model,
                    review.created_at.isoformat(),
                ),
            )

            await db.commit()
        return review

    async def get_all(self) -> list[CodeReview]:
        await self._ensure_table()
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM reviews ORDER BY created_at DESC")
            rows = await cursor.fetchall()
        return [_row_to_review(row) for row in rows]

    async def get_by_id(self, review_id: str) -> CodeReview | None:
        await self._ensure_table()
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM reviews WHERE id = ?", (review_id,)
            )
            row = await cursor.fetchone()
        if row is None:
            return None
        return _row_to_review(row)

    async def delete(self, review_id: str) -> bool:
        await self._ensure_table()
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "DELETE FROM reviews WHERE id = ?", (review_id,)
            )
            await db.commit()
        return cursor.rowcount > 0