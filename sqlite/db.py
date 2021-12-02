import sqlite3
import csv

from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    
    return conn

def create_table(conn, create_table_sql):
    print("in create_table")
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    """
    try:
        print("in try")
        c = conn.cursor()
        print("in try and after cursor")
        c.execute(create_table_sql)
        print("executed")
    except Error as e:
        # print("create table error")
        print(e)



def read_file(file_name):
    file = open(file_name)

    csvreader = csv.reader(file)
    header = next(csvreader)
    rows = []
    for row in csvreader:
        rows.append(row)
    print(rows)

    file.close()

    return rows

def main():
    print("in main")
    db = r"/Users/shizuka/CS50/project/sqlite/db/simpleweather.db"

    # sql_create_weather_types_table = """ CREATE TABLE IF NOT EXISTS weather_types (
    #     id integer PRIMARY KEY,
    #     descriptuon text NOT NULL
    # ); """

    # sql_create_weathers_table = """ CREATE TABLE IF NOT EXISTS weathers (
    #     id integer PRIMARY KEY,
    #     descriptuon text NOT NULL,
    #     weather_types_id integer NOT NULL,
    #     FOREIGN KEY (weather_types_id) REFERENCES weather_types (id)
    # ); """

    sql_create_users_table = """ CREATE TABLE IF NOT EXISTS users (
        id integer PRIMARY KEY,
        username text NOT NULL,
        hash integer NOT NULL
    ); """

    sql_create_user_locations_table = """ CREATE TABLE IF NOT EXISTS user_locations (
        id integer PRIMARY KEY,
        country text NOT NULL,
        zipcode text NOT NULL,
        from_hour integer NOT NULL,
        to_hour integer NOT NULL,
        user_id integer NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    ); """

    # create a database connection
    conn = create_connection(db)

    # create tables
    if conn is not None:
        print("in if")
        try:
            print("in try")
            c = conn.cursor()
        except Error as e:
            # print("insert data error")
            print(e)

        # # create weater_types table
        # create_table(conn, sql_create_weather_types_table)
        # # insert data from csv file into weater_types table
        # data = read_file('weather_types.csv')
        # c.executemany("INSERT OR IGNORE INTO weather_types VALUES (?, ?)", data)


        # # create weaters table
        # create_table(conn, sql_create_weathers_table)
        # # insert data from csv file into weater_types table
        # data = read_file('weathers.csv')
        # c.executemany("INSERT OR IGNORE INTO weathers VALUES (?, ?, ?)", data)

        # create users table
        print("after try")
        create_table(conn, sql_create_users_table)
        print("created users table")

        # create user_areas table
        create_table(conn, sql_create_user_locations_table)
        print("created user_locations table")

        conn.commit()
        print("commited")

    else:
        print("Erro! cannot create the database connection.")

    conn.close()


if __name__ == "__main__":
    main()