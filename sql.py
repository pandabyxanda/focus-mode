import sqlite3
import datetime

today = datetime.date.today()
now = datetime.datetime.now()
# print(today)
# print(now)
# print(type(now))

database_connection = sqlite3.connect("database.db")
database_cursor = database_connection.cursor()
# cur.execute("CREATE TABLE movie(title, year, score)")
a = "CREATE TABLE IF NOT EXISTS data (\
id integer PRIMARY KEY, \
full_name VARCHAR(255), \
time_start DATETIME, \
time_end DATETIME, \
tag VARCHAR(255))"

# print(a)

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
# print(f"{row = } {row[2] = }")
# print(type(row[2]))
# print(datetime.datetime.fromisoformat(row[2]))
# print(type(datetime.datetime.fromisoformat(row[2])))
# row = database_cursor.fetchone()
# print(f"{row = } {row[2] = }")

database_cursor.execute("select count(*) from data")
row = database_cursor.fetchone()
# print(f"{row = }")

# # database_cursor.execute("select count(id), full_name, time_end-time_start from data group by full_name order by count(id)")
# database_cursor.execute("select id, full_name, time_end, time_start, (julianday(time_end)-julianday(time_start))*24*60*60 from data order by julianday(time_end)-julianday(time_start) desc")
# for i in range(0, 12):
#     try:
#         row = database_cursor.fetchone()
#         print(f"{row = }")
#     except:
#         break

# print("-==========")
# database_cursor.execute("""select full_name, sum((julianday(time_end)-julianday(time_start))*24*60*60)
# from data
# group by full_name
# order by sum(julianday(time_end)-julianday(time_start)) desc""")
# all_rows = database_cursor.fetchall()
# [print(x) for x in all_rows]

# print("-==========")
# database_cursor.execute("""select full_name, substr(full_name, 1, 6), sum((julianday(time_end)-julianday(time_start))*24*60*60)
# from data
# group by substr(full_name, 1, 6)
# order by sum(julianday(time_end)-julianday(time_start)) desc""")
# all_rows = database_cursor.fetchall()
# [print(x) for x in all_rows]

print("-==========")
# database_cursor.execute("""
# select f, d from
# (
# select full_name as f, sum(julianday(time_end)-julianday(time_start))*24*60*60 as d
# from data
# where substr(full_name, 1, 13) = "Google Chrome"
# group by full_name
# union all
# select substr(full_name, 1, 10) as f, sum(julianday(time_end)-julianday(time_start))*24*60*60 as d
# from data
# where substr(full_name, 1, 13) != "Google Chrome"
# group by substr(full_name, 1, 10)
# )
# order by d desc
# """)
# all_rows = database_cursor.fetchall()
# [print(x) for x in all_rows]

database_cursor.execute("""
        select REPLACE(f, '.exe', '') as ff, d from
        (
        select 
        substr(full_name, 1, INSTR(full_name, "-")-1) || 
        " " || 
        trim(substr(substr(full_name, INSTR(full_name, "-")+1, length(full_name)), 1, INSTR(substr(full_name, INSTR(full_name, "-")+1, length(full_name)), "-")), "-") as f, 
        sum(julianday(time_end)-julianday(time_start))*24*60*60 as d 
        from data
        where substr(full_name, 1, 13) = "Google Chrome"
        group by full_name

        union

        select substr(full_name, 1, INSTR(full_name, "-")-1) as f, sum(julianday(time_end)-julianday(time_start))*24*60*60 as d 
        from data
        where substr(full_name, 1, 13) != "Google Chrome" and full_name like "%-%"
        group by substr(full_name, 1, INSTR(full_name, "-")-1)

        UNION

        select full_name as f, sum(julianday(time_end)-julianday(time_start))*24*60*60 as d 
        from data
        where substr(full_name, 1, 13) != "Google Chrome" and full_name not like "%-%"
        group by full_name
        )
        where d >= 1
        group by f        
        order by d desc
        """)
all_rows = database_cursor.fetchall()
[print(x) for x in all_rows]

database_cursor.execute("""select max(id) from data""")
all_rows = database_cursor.fetchone()[0]
print(all_rows)





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
