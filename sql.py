import sqlite3
import datetime
import time



# today = datetime.date.today()
# now = datetime.datetime.now()
# print(today)
# print(now)
# print(type(now))



class DataBase():
    def __init__(self, db_name):
        self.db_name = db_name
        self.database_connection = None
        self.cursor = None

    def connect(self):
        self.database_connection = sqlite3.connect(self.db_name)
        self.cursor = self.database_connection.cursor()

    def create_table_if_not_exists(self):
        a = "CREATE TABLE IF NOT EXISTS data (\
        id integer PRIMARY KEY, \
        full_name VARCHAR(255), \
        time_start DATETIME, \
        time_end DATETIME, \
        tag VARCHAR(255))"
        self.cursor.execute(a)

    def disconnect(self):
        self.cursor.close()

    def query_load_on_date(self, date=""):
        a = "Postman"
        # self.cursor.execute("""select ? from data""", (a,))
        # self.cursor.execute("""select :what from data""", {"what": '*'})
        self.cursor.execute("""select * from data where full_name=?""", (a,))
        # self.cursor.execute("select full_name from data")
        return self.cursor.fetchall()





    def query_save(self, max_id, LastActiveWindow, TimeAppOpened, TimeClosed):
        self.cursor.execute("""
                            INSERT INTO data VALUES(?, ?, ?, ?, NULL)
                            """,
                            (max_id, LastActiveWindow, TimeAppOpened, TimeClosed))
        self.database_connection.commit()

    def query_simple_load_on_date(self, date1, date2):
        self.cursor.execute("""
                select REPLACE(f, '.exe', '') as ff, d, sum(c_f) from
                (
                select
                substr(full_name, 1, 13) as f,
                sum(julianday(time_end)-julianday(time_start))*24*60*60 as d,
                count(full_name) as c_f
                
                from data
                where substr(full_name, 1, 13) = "Google Chrome" and substr(full_name, 1, 21) != "Google Chrome-YouTube" and time_end BETWEEN :date1 AND :date2 and (julianday(time_end)-julianday(time_start))*24*60*60 >= 0
                group by f
                
                union
                
                select
                substr(full_name, 15, 7) as f,
                sum(julianday(time_end)-julianday(time_start))*24*60*60 as d,
                count(full_name) as c_f
                
                from data
                where substr(full_name, 1, 21) = "Google Chrome-YouTube" and time_end BETWEEN :date1 AND :date2 and (julianday(time_end)-julianday(time_start))*24*60*60 >= 0
                group by f

                union

                select substr(full_name, 1, INSTR(full_name, "-")-1) as f, 
                sum(julianday(time_end)-julianday(time_start))*24*60*60 as d, 
                count(full_name) as c_f
                from data
                where substr(full_name, 1, 13) != "Google Chrome" and full_name like "%-%" and time_end BETWEEN :date1 AND :date2 and (julianday(time_end)-julianday(time_start))*24*60*60 >= 0
                group by substr(full_name, 1, INSTR(full_name, "-")-1)

                UNION

                select full_name as f, 
                sum(julianday(time_end)-julianday(time_start))*24*60*60 as d, 
                count(full_name) as c_f
                from data
                where substr(full_name, 1, 13) != "Google Chrome" and full_name not like "%-%" and time_end BETWEEN :date1 AND :date2 and (julianday(time_end)-julianday(time_start))*24*60*60 >= 0
                group by full_name
                )

                group by ff
                order by d desc
                """, {'date1': date1, 'date2': date2})




        return self.cursor.fetchall()

    def query_simple_load_on_date_test(self, date1, date2):
        self.cursor.execute("""
                select REPLACE(f, '.exe', '') as ff, d from
                (
                select
                substr(full_name, 1, INSTR(full_name, "-")-1) ||
                " " ||
                trim(substr(substr(full_name, INSTR(full_name, "-")+1, length(full_name)), 1, INSTR(substr(full_name, INSTR(full_name, "-")+1, length(full_name)), "-")), "-") as f,
                sum(julianday(time_end)-julianday(time_start))*24*60*60 as d
                from data
                where substr(full_name, 1, 13) = "Google Chrome" and time_end BETWEEN :date1 AND :date2 and (julianday(time_end)-julianday(time_start))*24*60*60 >= 0
                group by f
                )
                where d >= 1
                group by f
                order by d desc
                """, {'date1': date1, 'date2': date2})
        return self.cursor.fetchall()

    def query_extended_load_on_date(self, date1, date2):
        self.cursor.execute("""
                            select REPLACE(full_name, '.exe', '') as f, sum(julianday(time_end)-julianday(time_start))*24*60*60 as d, count(full_name) as c_f
                            from data
                            where time_end BETWEEN :date1 AND :date2 and (julianday(time_end)-julianday(time_start))*24*60*60 >= 0
                            group by full_name
                            order by d desc
                            """,
                            {'date1': date1, 'date2': date2}
                            )
        return self.cursor.fetchall()

    def query_get_all_raw(self, date1, date2):
        self.cursor.execute("""
                            select full_name as f, count(full_name) as c_f, sum(julianday(time_end)-julianday(time_start))*24*60*60 as d, count(full_name) as c_f
                            from data
                            where time_end BETWEEN :date1 AND :date2 and (julianday(time_end)-julianday(time_start))*24*60*60 >= 0
                            group by full_name
                            order by d desc
                            """,
                            {'date1': date1, 'date2': date2}
                            )
        return self.cursor.fetchall()

    def query_select_max_id(self):
        self.cursor.execute("""
                            select max(id) from data
                            """
                            )
        return self.cursor.fetchone()[0]






if __name__ == "__main__":

    db = DataBase("database.db")
    db.connect()
    db.create_table_if_not_exists()
    # res = db.query_load_on_date()
    # '2023-01-04 07:00:00', '2023-01-05 07:00:00'
    # '2022-12-30 00:00:00', '2022-12-30 23:59:59'
    date1 = '2023-01-10 07:00:00'
    date2 = '2023-01-11 07:00:00'
    res = db.query_simple_load_on_date(date1, date2)
    print(f"{time.strftime('%H:%M:%S', time.gmtime(sum([x[1] for x in res])))}")
    print(f"{res = }")
    print(f"{len(res) = }")
    res = db.query_extended_load_on_date(date1, date2)
    print(f"{time.strftime('%H:%M:%S', time.gmtime(sum([x[1] for x in res])))}")
    print(f"{res = }")
    print(f"{len(res) = }")
    res = db.query_get_all_raw(date1, date2)
    print(f"{time.strftime('%H:%M:%S', time.gmtime(sum([x[1] for x in res])))}")
    # s = [print(x) for x in res]
    print(f"{res = }")
    print(f"{len(res) = }")

    db.disconnect()


# database_connection = sqlite3.connect("database.db")
# database_cursor = database_connection.cursor()
# # cur.execute("CREATE TABLE movie(title, year, score)")
# a = "CREATE TABLE IF NOT EXISTS data (\
# id integer PRIMARY KEY, \
# full_name VARCHAR(255), \
# time_start DATETIME, \
# time_end DATETIME, \
# tag VARCHAR(255))"
#
# # print(a)
#
# database_cursor.execute(a)
#

# cur.execute("""
#     INSERT INTO data VALUES
#         (?, ?, ?, ?, NULL)
# """,
#             (2, "bem balabom2", now, now))
# con.commit()


# database_cursor.execute("select * from data")
# # print(f"{type(cur.fetchone())}")
# row = database_cursor.fetchone()
# print(f"{row = } {row[2] = }")
# print(type(row[2]))
# print(datetime.datetime.fromisoformat(row[2]))
# print(type(datetime.datetime.fromisoformat(row[2])))
# row = database_cursor.fetchone()
# print(f"{row = } {row[2] = }")

# database_cursor.execute("select count(*) from data")
# row = database_cursor.fetchone()
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

# print("-==========")
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





# database_cursor.execute("""
#         select REPLACE(f, '.exe', '') as ff, d from
#         (
#         select
#         substr(full_name, 1, INSTR(full_name, "-")-1) ||
#         " " ||
#         trim(substr(substr(full_name, INSTR(full_name, "-")+1, length(full_name)), 1, INSTR(substr(full_name, INSTR(full_name, "-")+1, length(full_name)), "-")), "-") as f,
#         sum(julianday(time_end)-julianday(time_start))*24*60*60 as d
#         from data
#         where substr(full_name, 1, 13) = "Google Chrome" and time_end BETWEEN '2022-12-28 00:00:00' AND '2022-12-28 23:59:59'
#         group by full_name
#
#         union
#
#         select substr(full_name, 1, INSTR(full_name, "-")-1) as f, sum(julianday(time_end)-julianday(time_start))*24*60*60 as d
#         from data
#         where substr(full_name, 1, 13) != "Google Chrome" and full_name like "%-%" and time_end BETWEEN '2022-12-28 00:00:00' AND '2022-12-28 23:59:59'
#         group by substr(full_name, 1, INSTR(full_name, "-")-1)
#
#         UNION
#
#         select full_name as f, sum(julianday(time_end)-julianday(time_start))*24*60*60 as d
#         from data
#         where substr(full_name, 1, 13) != "Google Chrome" and full_name not like "%-%" and time_end BETWEEN '2022-12-28 00:00:00' AND '2022-12-28 23:59:59'
#         group by full_name
#         )
#         where d >= 1
#         group by f
#         order by d desc
#         """)
# all_rows = database_cursor.fetchall()
# [print(x) for x in all_rows]





#
# database_cursor.execute("""select max(id) from data""")
# all_rows = database_cursor.fetchone()[0]
# print(all_rows)





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
# database_cursor.close()
