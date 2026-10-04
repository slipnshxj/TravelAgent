from utils.postgres import get_connection


def list_memory_users() -> list[str]:
    sql = """
    SELECT DISTINCT user_id
    FROM memories
    ORDER BY user_id;
    """

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            return [row[0] for row in cursor.fetchall()]


def save_memory(
    user_id: str,
    category: str,
    content: str,
    importance: int = 1,
    source: str = "conversation",
):
    sql = """
    INSERT INTO memories (
        user_id,
        category,
        content,
        importance,
        source
    )
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (user_id, category, content)
    DO UPDATE SET
        importance = EXCLUDED.importance,
        source = EXCLUDED.source,
        updated_at = NOW(),
        is_active = TRUE
    RETURNING id;
    """

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                sql,
                (
                    user_id,
                    category,
                    content,
                    importance,
                    source,
                ),
            )
            memory_id = cursor.fetchone()[0]

        conn.commit()
        return memory_id


def get_memories(
    user_id: str,
    category: str | None = None,
    limit: int = 20,
):
    return list_memories(
        user_id=user_id,
        category=category,
        limit=limit,
        include_archived=False,
    )


def list_memories(
    user_id: str,
    category: str | None = None,
    limit: int = 100,
    include_archived: bool = False,
) -> list[tuple]:
    active_filter = "" if include_archived else "AND is_active = TRUE"
    if category:
        sql = """
        SELECT id, user_id, category, content,
               importance, source, is_active,
               created_at, updated_at
        FROM memories
        WHERE user_id = %s
          AND category = %s
          {active_filter}
        ORDER BY importance DESC, updated_at DESC
        LIMIT %s;
        """.format(active_filter=active_filter)
        params = (user_id, category, limit)
    else:
        sql = """
        SELECT id, user_id, category, content,
               importance, source, is_active,
               created_at, updated_at
        FROM memories
        WHERE user_id = %s
          {active_filter}
        ORDER BY importance DESC, updated_at DESC
        LIMIT %s;
        """.format(active_filter=active_filter)
        params = (user_id, limit)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()


def archive_memory(
    user_id: str,
    memory_id: int,
    archived: bool = True,
) -> bool:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE memories
                SET is_active = %s,
                    updated_at = NOW()
                WHERE id = %s
                  AND user_id = %s
                """,
                (not archived, memory_id, user_id),
            )
            updated = cursor.rowcount > 0
        connection.commit()
        return updated
    finally:
        connection.close()
def deactivate_memory(
        user_id:str,
        memory_id:str
):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE memories
                SET
                    is_active = FALSE,
                    updated_at = NOW()
                WHERE id = %s
                    AND user_id = %s
                """,
                (
                    memory_id,
                    user_id,
                ),
            )
        connection.commit()
    finally:
        connection.close()


def delete_memory(
        user_id:str,
        memory_id:int
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM memories
                WHERE id = %s
                    AND user_id = %s
                """,
                (
                    memory_id,
                    user_id,
                ),
            )
            deleted = cursor.rowcount > 0
        connection.commit()
        return deleted
    finally:
        connection.close()

