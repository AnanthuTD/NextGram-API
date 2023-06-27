import atexit
from django.db import connection

def truncate_room_table():
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE chat_room CASCADE")

atexit.register(truncate_room_table)
