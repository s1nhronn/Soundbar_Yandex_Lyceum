import sqlite3
from config import db


def first_join(path, sound_name, guild_id: int):
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


def fetch_data(start_id, end_id, guild_id: int):
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


def path_to_delete(name, guild_id: int):
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


def delete_sound(path, guild_id: int):
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
