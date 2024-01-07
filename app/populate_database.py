import sqlite3

con = sqlite3.connect('app/database1.db')
cur = con.cursor()


def create_database():
    for table in open('app/schema.sql').read().split(';'):
        cur.execute(table)
        con.commit()


create_database()

def populate_table(table, data):
    command = 'INSERT INTO "{}" VALUES ('.format(table) + '?, ' * (len(data[0]) - 1) + '?' + ')'
    print(command)
    cur.executemany(command, data)
    con.commit()

for tables in open("app/data.txt").read().split('\n\n'):
    table, data = tables.split('\n', 1)
    cleared_data = []
    for line in data.split('\n'):
        line = line.split(',')
        cleared_data.append(list(entry.split(": ")[1].replace('"', "").replace("'", "") for entry in line))
    populate_table(table, cleared_data)

con.close()