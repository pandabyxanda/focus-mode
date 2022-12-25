import sqlite3
import datetime

today = datetime.date.today()
now = datetime.datetime.now()
print(today)
print(now)
print(type(now))

database_connection = sqlite3.connect("database.db")
database_cursor = database_connection.cursor()
# cur.execute("CREATE TABLE movie(title, year, score)")
a = "CREATE TABLE IF NOT EXISTS data (\
id integer PRIMARY KEY, \
full_name VARCHAR(255), \
time_start DATETIME, \
time_end DATETIME, \
tag VARCHAR(255))"

print(a)

database_cursor.execute(a)
#

# cur.execute("""
#     INSERT INTO data VALUES
#         (?, ?, ?, ?, NULL)
# """,
#             (2, "bem balabom2", now, now))
# con.commit()


database_cursor.execute("select * from data")
# print(f"{type(cur.fetchone())}")
row = database_cursor.fetchone()
print(f"{row = } {row[2] = }")
print(type(row[2]))
print(datetime.datetime.fromisoformat(row[2]))
print(type(datetime.datetime.fromisoformat(row[2])))
# row = database_cursor.fetchone()
# print(f"{row = } {row[2] = }")

database_cursor.execute("select count(*) from data")
row = database_cursor.fetchone()
print(f"{row = }")

# # database_cursor.execute("select count(id), full_name, time_end-time_start from data group by full_name order by count(id)")
# database_cursor.execute("select id, full_name, time_end, time_start, (julianday(time_end)-julianday(time_start))*24*60*60 from data order by julianday(time_end)-julianday(time_start) desc")
# for i in range(0, 12):
#     try:
#         row = database_cursor.fetchone()
#         print(f"{row = }")
#     except:
#         break

print("-==========")
database_cursor.execute("""select full_name, sum((julianday(time_end)-julianday(time_start))*24*60*60) 
from data 
group by full_name 
order by julianday(time_end)-julianday(time_start) desc""")
all_rows = database_cursor.fetchall()
[print(x) for x in all_rows]





#
#
#
# cur.execute("""
#     INSERT INTO data VALUES
#         (1, 'movie lol bgg', ),
#         ('And Now for Something Completely Different', 1971, 7.5)
# """)
#
# con.commit()
#
#
#
#
#
database_cursor.close()
