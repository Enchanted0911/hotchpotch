from mysql.connector.pooling import MySQLConnectionPool


def demo():
    conn = mysql_pool.get_connection()
    cursor = conn.cursor()
    try:
        selectsql = "select chapterFile from tech_book_chapter_0728 where ID = 177821"
        cursor.execute(selectsql)
        r = cursor.fetchall()
        return r[0]
    except Exception as dbex:
        print("插入转图片错误记录", dbex)
    finally:
        cursor.close()
        conn.close()

mysql_pool = MySQLConnectionPool(
    host="192.168.100.13",  # 数据库主机地址
    user="root",  # 数据库用户名
    passwd="tilde",  # 数据库密码
    port=3306,
    database='cjml_knowledge_base',
    pool_size=30,
    charset='utf8',
    encoding='utf8'
)

if __name__ == '__main__':
    print(demo()[0])
    print(demo()[0][-18])
    print(demo()[0][-18].encode('utf-8'))
    print(type('?'.encode('utf-8')))
    print('?'.encode('utf-8') == demo()[0][-18].encode('utf-8'), '?'.encode('utf-8'), demo()[0][-18].encode('utf-8'))
    print('?'.encode('gbk') == demo()[0][-18].encode('gbk'), '?'.encode('gbk'), demo()[0][-18].encode('gbk'))
    print('ä'.encode('utf-8'))
