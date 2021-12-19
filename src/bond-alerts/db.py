from os.path import isfile
from sqlite3 import connect

DB_PATH = "./database.db"
BUILD_PATH = "./build.sql"

cxn = connect(DB_PATH, check_same_thread=False)
cur = cxn.cursor()

def with_commit(func):
    def inner(*args, **kwargs):
        func(*args, **kwargs)
        save()
    return inner

@with_commit
def build():
    if isfile(BUILD_PATH):
        scriptexec(BUILD_PATH)

def save():
    cxn.commit()

def close():
    cxn.close()

def field(command, *values):
    cur.execute(command, tuple(values))

    if (fetch := cur.fetchone()) is not None:
        return fetch[0]

def record(command, *values):
    cur.execute(command, tuple(values))

    return cur.fetchone()

def records(command, *values):
    cur.execute(command, tuple(values))

    return cur.fetchall()

def column(command, *values):
    cur.execute(command, tuple(values))

    return [item[0] for item in cur.fetchall()]

def execute (command, *values):
    cur.execute(command, tuple(values))

def multiexec (command, *values):
    cur.execute(command, valueset)

def scriptexec(path):
	with open(path, "r", encoding="utf-8") as script:
		cur.executescript(script.read())

build()