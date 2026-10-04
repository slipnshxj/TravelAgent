from utils.postgres import get_connection

def main():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT version()")
        result=cursor.fetchone()

    print("[PostgreSQL] 连接成功")
    print(result[0])

    connection.close()

if __name__=="__main__":
    main()