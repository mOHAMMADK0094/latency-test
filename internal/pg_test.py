import psycopg2
import datetime
import time
import os


# I've got these functions from https://www.postgresqltutorial.com/postgresql-python/
def load_config():
    config = {}
    config['host']=os.environ.get('DB_HOST','127.0.0.1')
    config['port']=os.environ.get('DB_PORT',5432)
    config['database']=os.environ.get('DB_NAME','networklatency')
    config['user']=os.environ.get('DB_USER','networklatency')
    config['password']=os.environ.get('DB_PASSWORD','password')
    return config


def connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)


def create_tables():
    """ Create tables in the PostgreSQL database"""
    commands = ("CREATE TABLE nwltable (first_char character varying(128) NOT NULL, second_char character varying(64), first_time timestamp without time zone DEFAULT now(), first_json jsonb, second_json jsonb)",)
    try:
        config = load_config()
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # execute the CREATE TABLE statement
                for command in commands:
                    cur.execute(command)
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)


def insert_data(data_list):
    """ Insert a row into nwltable table """

    sql = "INSERT INTO nwltable(first_char, second_char, first_time, first_json, second_json) VALUES(%s, %s, %s, %s, %s) RETURNING first_time;"
    
    first_time = None
    config = load_config()

    try:
        with  psycopg2.connect(**config) as conn:
            with  conn.cursor() as cur:
                # execute the INSERT statement
                cur.execute(sql, data_list)
                # get the generated id back                
                rows = cur.fetchone()
                if rows:
                    first_time = rows[0]

                # commit the changes to the database
                conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)    
    finally:
        return first_time


def get_data():
    """ Retrieve data from nwltable table """
    config  = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT first_time FROM nwltable ORDER BY first_time DESC LIMIT 1;")
                row = cur.fetchone()
        return row
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def delete_data(del_time):
    """ Delete the inserted row from Postgresql """

    rows_deleted  = 0
    sql = 'DELETE FROM nwltable WHERE first_time = %s'
    config = load_config()

    try:
        with  psycopg2.connect(**config) as conn:
            with  conn.cursor() as cur:
                # execute the DELETE statement
                cur.execute(sql, (del_time,))
                rows_deleted = cur.rowcount

            # commit the changes to the database
            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)    
    finally:
        return rows_deleted


def run():
    '''
        Inserts a row in a table then select those valuse then deletes them. 

            Returns:
                    cpuTimespent (dict): The time used by cpu in each step
    '''

    current_time = datetime.datetime.now()
    mylist = ['MK73',  #Char
            'MK94',  #Char
            current_time,  #Date time
            # Two following jsons
            '{"list": [20, 14, 1, 17, 1, 17, 14, 0], "item": 7, "itemNum": 0, "number": 0, "oneTime": "2024-07-13T13:27:40.2718783Z"}',
            '{"justTime": "2024-07-13T13:27:40.2718783Z"}',
            ]

    startTime=time.perf_counter()

    if insert_data(mylist) == current_time:   #Inserting data returning field is first_time
        endTimeInsert=time.perf_counter()
        if get_data()[0] == current_time:     #Selecting first_time and cheking with current_time
            endTimeSelect=time.perf_counter()
            if delete_data(current_time)==1:  #Deleting a row based on current time and check affected rows
                endTime=time.perf_counter()
                return {"totalTime": endTime-startTime, "selectTime": endTimeSelect-endTimeInsert, "insertTime": endTimeInsert-startTime, "deleteTime": endTime-endTimeSelect}
            else:
                return -1
        else:
            return -1
    else:
        return -1


if __name__ == '__main__':
    print(run())