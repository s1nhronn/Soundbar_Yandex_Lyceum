import sqlite3
from config import db


def first_join(path: str, sound_name: str, guild_id: int) -> None:
    """
    Добавление звука в базу данных
    :param path: Путь до звука
    :param sound_name: Имя звука
    :param guild_id: ID сервера дискорд
    :return:
    """
    connection = sqlite3.connect(db)
    q = connection.cursor()
    req = "SELECT name FROM sqlite_master WHERE type='table' AND name='guild" + str(guild_id) + "'"
    if q.execute(req).fetchone() is None:
        q.execute("""CREATE TABLE IF NOT EXISTS guild""" + str(guild_id) + """(
            id         INTEGER PRIMARY KEY
                               UNIQUE ON CONFLICT REPLACE
                               NOT NULL ON CONFLICT IGNORE,
            path       TEXT    UNIQUE ON CONFLICT REPLACE
                               NOT NULL ON CONFLICT IGNORE,
            sound_name TEXT    NOT NULL ON CONFLICT IGNORE
        );
""")
    q.execute("INSERT INTO guild" + str(guild_id) + " (path,  sound_name) VALUES ('%s','%s')" % (path, sound_name))
    connection.commit()
    connection.close()


def fetch_data(start_id: int, end_id: int, guild_id: int) -> list:
    """
    Получение звуков из базы данных
    :param start_id: ID начала среза списка из звуков
    :param end_id: ID конца среза списка из звуков
    :param guild_id: ID сервера дискорд
    :return: Список с информацией о звуках
    """
    connection = sqlite3.connect(db)
    q = connection.cursor()
    req = "SELECT name FROM sqlite_master WHERE type='table' AND name='guild" + str(guild_id) + "'"
    if q.execute(req).fetchone() is None:
        q.execute("""CREATE TABLE IF NOT EXISTS guild""" + str(guild_id) + """(
                id         INTEGER PRIMARY KEY
                                   UNIQUE ON CONFLICT REPLACE
                                   NOT NULL ON CONFLICT IGNORE,
                path       TEXT    UNIQUE ON CONFLICT REPLACE
                                   NOT NULL ON CONFLICT IGNORE,
                sound_name TEXT    NOT NULL ON CONFLICT IGNORE
            );
""")
    q.execute("SELECT * FROM guild" + str(guild_id) + f" WHERE id BETWEEN {start_id} AND {end_id};")
    data = q.fetchall()
    connection.close()
    return data


def path_to_delete(name: str, guild_id: int) -> str | None:
    """
    Получение пути до звука для дальнейшего удаления
    :param name: Имя звука
    :param guild_id: ID сервера дискорд
    :return: Путь до звука или None, если такого звука нет
    """
    connection = sqlite3.connect(db)
    q = connection.cursor()
    req = "SELECT name FROM sqlite_master WHERE type='table' AND name='guild" + str(guild_id) + "'"
    if q.execute(req).fetchone() is None:
        q.execute("""CREATE TABLE IF NOT EXISTS guild""" + str(guild_id) + """(
                    id         INTEGER PRIMARY KEY
                                       UNIQUE ON CONFLICT REPLACE
                                       NOT NULL ON CONFLICT IGNORE,
                    path       TEXT    UNIQUE ON CONFLICT REPLACE
                                       NOT NULL ON CONFLICT IGNORE,
                    sound_name TEXT    NOT NULL ON CONFLICT IGNORE
                );
""")
    q = q.execute("SELECT path FROM guild" + str(guild_id) + f" WHERE sound_name = '{name}'")
    row = q.fetchone()
    connection.close()
    try:
        return row[0]
    except TypeError:
        return None


def delete_sound(path: str, guild_id: int) -> None:
    """
    Удаление звука из базы данных
    :param path: Путь до звука
    :param guild_id: ID сервера дискорд
    :return:
    """
    connection = sqlite3.connect(db)
    q = connection.cursor()
    req = "SELECT name FROM sqlite_master WHERE type='table' AND name='guild" + str(guild_id) + "'"
    if q.execute(req).fetchone() is None:
        q.execute("""CREATE TABLE IF NOT EXISTS guild""" + str(guild_id) + """(
                    id         INTEGER PRIMARY KEY
                                       UNIQUE ON CONFLICT REPLACE
                                       NOT NULL ON CONFLICT IGNORE,
                    path       TEXT    UNIQUE ON CONFLICT REPLACE
                                       NOT NULL ON CONFLICT IGNORE,
                    sound_name TEXT    NOT NULL ON CONFLICT IGNORE
                );
""")
    q.execute("DELETE FROM guild" + str(guild_id) + f" WHERE path = '{str(path)}'")
    connection.commit()
    connection.close()
