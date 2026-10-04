from utils.postgres import get_connection


def list_memory_users() -> list[str]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT DISTINCT user_id FROM memories ORDER BY user_id")
            return [row[0] for row in cursor.fetchall()]


def save_memory(
    user_id: str,
    category: str,
    content: str,
    importance: int = 1,
    source: str = "conversation",
) -> int:
    sql = """
    INSERT INTO memories (user_id, category, content, importance, source)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (user_id, category, content)
    DO UPDATE SET
        importance = EXCLUDED.importance,
        source = EXCLUDED.source,
        updated_at = NOW(),
        is_active = TRUE
    RETURNING id;
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                sql,
                (user_id, category, content, importance, source),
            )
            memory_id = cursor.fetchone()[0]
        connection.commit()
    return memory_id


def list_memories(
    user_id: str,
    category: str | None = None,
    limit: int = 100,
    include_archived: bool = False,
) -> list[tuple]:
    active_filter = "" if include_archived else "AND is_active = TRUE"
    if category:
        sql = f"""
        SELECT id, user_id, category, content, importance, source,
               is_active, created_at, updated_at
        FROM memories
        WHERE user_id = %s AND category = %s {active_filter}
        ORDER BY importance DESC, updated_at DESC
        LIMIT %s;
        """
        params = (user_id, category, limit)
    else:
        sql = f"""
        SELECT id, user_id, category, content, importance, source,
               is_active, created_at, updated_at
        FROM memories
        WHERE user_id = %s {active_filter}
        ORDER BY importance DESC, updated_at DESC
        LIMIT %s;
        """
        params = (user_id, limit)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()


def archive_memory(
    user_id: str,
    memory_id: int,
    archived: bool = True,
) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE memories
                SET is_active = %s, updated_at = NOW()
                WHERE id = %s AND user_id = %s
                """,
                (not archived, memory_id, user_id),
            )
            updated = cursor.rowcount > 0
        connection.commit()
    return updated


def delete_memory(user_id: str, memory_id: int) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM memories WHERE id = %s AND user_id = %s",
                (memory_id, user_id),
            )
            deleted = cursor.rowcount > 0
        connection.commit()
    return deleted
