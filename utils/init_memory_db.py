from utils.postgres import get_connection

def init_memory_database():
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id BIGSERIAL PRIMARY KEY,

                user_id VARCHAR(100) NOT NULL,

                category VARCHAR(100) NOT NULL,

                content TEXT NOT NULL,

                importance INTEGER NOT NULL DEFAULT 1,

                source VARCHAR(100) NOT NULL DEFAULT 'conversation',

                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

                is_active BOOLEAN NOT NULL DEFAULT TRUE
            )
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_memory_user_id
            ON memories(user_id)
            """
        )
        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_memories_user_category_content
            ON memories(user_id, category, content)
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_memory_category
            ON memories(user_id,category)
            """
        )
        connection.commit()
    connection.close()
    print("[Database] memories 表初始化完成")

if __name__ == "__main__":
    init_memory_database()

