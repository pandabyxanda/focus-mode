import sqlite3
import time


class DataBase:
    def __init__(self, db_name):
        self.db_name = db_name
        self.database_connection = None
        self.cursor = None

    def connect(self):
        self.database_connection = sqlite3.connect(self.db_name)
        self.cursor = self.database_connection.cursor()

    def create_table_if_not_exists(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS data (
            id integer PRIMARY KEY, 
            full_name VARCHAR(255), 
            time_start DATETIME, 
            time_end DATETIME, 
            tag VARCHAR(255)
            )
            """
        )

    def disconnect(self):
        self.cursor.close()

    def query_save(self, max_id, last_active_window, time_app_opened, time_closed):
        self.cursor.execute(
            """
            INSERT INTO data VALUES(?, ?, ?, ?, NULL)
            """,
            (max_id, last_active_window, time_app_opened, time_closed)
        )
        self.database_connection.commit()

    def query_simple_load_on_date(self, date1, date2, shortest_time):
        """
        returns data, joined in big groups
        """

        self.cursor.execute(
            """
            select REPLACE(f, '.exe', '') as ff, sum(d), sum(c_f) from (
                select
                substr(full_name, 1, 13) as f,
                sum(julianday(time_end)-julianday(time_start))*24*60*60 as d,
                count(full_name) as c_f
                
                from data
                where substr(full_name, 1, 13) = "Google Chrome" and 
                substr(full_name, 1, 21) != "Google Chrome-YouTube" and 
                time_end BETWEEN :date1 AND :date2 and 
                (julianday(time_end)-julianday(time_start))*24*60*60 >= :shortest_time
                group by f
                
                union
                
                select
                substr(full_name, 15, 7) as f,
                sum(julianday(time_end)-julianday(time_start))*24*60*60 as d,
                count(full_name) as c_f
                
                from data
                where substr(full_name, 1, 21) = "Google Chrome-YouTube" and 
                time_end BETWEEN :date1 AND :date2 and 
                (julianday(time_end)-julianday(time_start))*24*60*60 >= :shortest_time
                group by f
    
                union
    
                select substr(full_name, 1, INSTR(full_name, "-")-1) as f, 
                sum(julianday(time_end)-julianday(time_start))*24*60*60 as d, 
                count(full_name) as c_f
                from data
                where substr(full_name, 1, 13) != "Google Chrome" and 
                full_name like "%-%" and 
                time_end BETWEEN :date1 AND :date2 and 
                (julianday(time_end)-julianday(time_start))*24*60*60 >= :shortest_time
                group by substr(full_name, 1, INSTR(full_name, "-")-1)
    
                union
    
                select full_name as f, 
                sum(julianday(time_end)-julianday(time_start))*24*60*60 as d, 
                count(full_name) as c_f
                from data
                where substr(full_name, 1, 13) != "Google Chrome" and 
                full_name not like "%-%" and 
                time_end BETWEEN :date1 AND :date2 and 
                (julianday(time_end)-julianday(time_start))*24*60*60 >= :shortest_time
                group by full_name
                )

            group by ff
            order by d desc
            """,
            {'date1': date1, 'date2': date2, 'shortest_time': shortest_time}
        )

        return self.cursor.fetchall()

    def query_extended_load_on_date(self, date1, date2, shortest_time):
        """
        returns raw data
        """
        self.cursor.execute(
            """
            select REPLACE(full_name, '.exe', '') as f, 
            sum(julianday(time_end)-julianday(time_start))*24*60*60 as d, 
            count(full_name) as c_f
            
            from data
            
            where time_end BETWEEN :date1 AND :date2 and 
            (julianday(time_end)-julianday(time_start))*24*60*60 >= :shortest_time
            
            group by full_name
            order by d desc
            """,
            {'date1': date1, 'date2': date2, 'shortest_time': shortest_time}
        )
        return self.cursor.fetchall()

    def query_get_all_raw(self, date1, date2, shortest_time):
        self.cursor.execute(
            """
            select full_name as f, 
            count(full_name) as c_f, 
            sum(julianday(time_end)-julianday(time_start))*24*60*60 as d, 
            count(full_name) as c_f
            
            from data
            
            where time_end BETWEEN :date1 AND :date2 and 
            (julianday(time_end)-julianday(time_start))*24*60*60 >= :shortest_time
            
            group by full_name
            order by d desc
            """,
            {'date1': date1, 'date2': date2, 'shortest_time': shortest_time}
        )
        return self.cursor.fetchall()

    def query_select_max_id(self):
        self.cursor.execute(
            """
            select max(id) from data
            """
        )
        return self.cursor.fetchone()[0]


if __name__ == "__main__":
    db = DataBase("database.db")
    db.connect()
    db.create_table_if_not_exists()
    date_1 = '2023-01-12 07:00:00'
    date_2 = '2023-01-13 06:59:59'
    short_time = 31
    res = db.query_simple_load_on_date(date_1, date_2, short_time)
    print(f"{time.strftime('%H:%M:%S', time.gmtime(sum([x[1] for x in res])))}")
    print(f"{res = }")
    print(f"{len(res) = }")
    print()
    res = db.query_extended_load_on_date(date_1, date_2, short_time)
    print(f"{time.strftime('%H:%M:%S', time.gmtime(sum([x[1] for x in res])))}")
    print(f"{res = }")
    print(f"{len(res) = }")
    print()
    res = db.query_get_all_raw(date_1, date_2, short_time)
    print(f"{time.strftime('%H:%M:%S', time.gmtime(sum([x[1] for x in res])))}")
    # s = [print(x) for x in res]
    print(f"{res = }")
    print(f"{len(res) = }")

    db.disconnect()
