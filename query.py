import sqlite3
import enum


class Mode(enum.Enum):
    FETCH_NONE = 0
    FETCH_ONE = 1
    FETCH_ALL = 2

def run(
    command: str, 
    queryMode: Mode = Mode.FETCH_NONE
):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.row_factory = sqlite3.Row

    print(command)
    cursor.execute(command)

    result = None
    if(queryMode == Mode.FETCH_NONE):
        pass
    elif(queryMode == Mode.FETCH_ONE):
        result = cursor.fetchone()
    elif(queryMode == Mode.FETCH_ALL):
        result = cursor.fetchall()

    connection.commit()
    cursor.close()
    connection.close()

    return result
