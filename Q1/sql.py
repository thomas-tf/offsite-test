import os
import uuid
import random
import psycopg2
import psycopg2.extras

from datetime import datetime


class SQLTest:
    """
    prepare environment and settings for Q1
    """

    def __init__(self, table_name='piwik_track'):
        # Establishing the connection
        self.conn = psycopg2.connect(
            database=os.environ.get('POSTGRESQL_DATABASE', 'postgres'),
            user=os.environ.get('POSTGRESQL_USERNAME', 'postgres'),
            password=os.environ.get('POSTGRESQL_PASSWORD', 'very_safe_password'),
            host=os.environ.get('POSTGRESQL_HOST', '127.0.0.1'),
            port=os.environ.get('POSTGRESQL_PORT', 5432)
        )
        self.conn.autocommit = True

        # Creating a cursor object using the cursor() method
        self.cursor = self.conn.cursor()

        self.table_name = table_name
        self.enum_type_values = ['FIRST_INSTALL', 'A', 'B']
        self.number_of_records = 10000
        self.number_of_users = 1000

        self.setup()
        self.populate()

    def setup(self):

        create_enum_type_query = f'''
        CREATE TYPE eventEnum AS ENUM('{','.join(self.enum_type_values)}')
        '''

        self.cursor.execute(create_enum_type_query)

        create_table_query = f'''
        CREATE TABLE {self.table_name}(
            time timestamp,
            uid varchar(256),
            event_name varchar(256)
        )
        '''

        self.cursor.execute(create_table_query)

    def populate(self):

        start = datetime.strptime('2017-04-01', '%Y-%m-%d')
        end = datetime.strptime('2017-04-10', '%Y-%m-%d')
        user_ids = [uuid.uuid4().hex for _ in range(self.number_of_users)]

        dummy_data = [(
            random.random() * (end - start) + start,  # time
            random.choice(user_ids),  # uid
            random.choice(self.enum_type_values),
        ) for _ in range(self.number_of_records)]

        insert_query = f'INSERT INTO {self.table_name} (time, uid, event_name) values %s'
        psycopg2.extras.execute_values(
            self.cursor, insert_query, dummy_data
        )

    def query(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def teardown(self):

        drop_type_query = 'DROP TYPE eventEnum'

        self.cursor.execute(drop_type_query)

        tear_down_query = f'DROP TABLE {self.table_name}'

        self.cursor.execute(tear_down_query)

        self.conn.close()


if __name__ == '__main__':

    table_name = 'piwik_track'

    sqltest = SQLTest(table_name)

    select_query = f'''
        WITH USER_WHO_INSTALLED_APP_ON_DATE AS ( 
            SELECT DISTINCT
                {table_name}.uid
            FROM
                {table_name}
            WHERE
                DATE({table_name}.time) = to_date('2017-04-01', 'YYYY-MM-DD') 
                AND {table_name}.event_name = 'FIRST_INSTALL'
        ), USER_WHO_USED_APP_AT_LEAST_ONCE_IN_TIME_RANGE AS (
            SELECT DISTINCT
                {table_name}.uid
            FROM
                {table_name}
            WHERE
                {table_name}.time BETWEEN to_date('2017-04-02', 'YYYY-MM-DD') 
                AND to_date('2017-04-08', 'YYYY-MM-DD')
        )
        SELECT
            COUNT(uid)
        FROM
            USER_WHO_INSTALLED_APP_ON_DATE
        INNER JOIN
            USER_WHO_USED_APP_AT_LEAST_ONCE_IN_TIME_RANGE
        USING 
            (uid)
    '''

    print("SQL query:")
    print(select_query)

    print(f"Table name: {table_name}")
    print(f"Number of dummy records: {sqltest.number_of_records}")
    print(f"Number of dummy users: {sqltest.number_of_users}")

    print(sqltest.query(select_query)[0][0])

    sqltest.teardown()
