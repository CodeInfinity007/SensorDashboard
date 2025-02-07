import mysql.connector
from mysql.connector import Error
from configparser import ConfigParser
import pandas as pd

class MySQLConnection:
    def __init__(self, filename='config.ini', section='mysql'):
        self.filename = filename
        self.section = section
        self.db_config = self.read_db_config()
        self.conn = None

    def read_db_config(self):
        parser = ConfigParser()
        parser.read(self.filename)

        db = {}
        if parser.has_section(self.section):
            params = parser.items(self.section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception(f'Section {self.section} not found in the {self.filename} file')

        return db

    def start_connection(self):
        try:
            print('Connecting to MySQL database...')
            self.conn = mysql.connector.connect(**self.db_config)

            if self.conn.is_connected():
                print('Connection established.')
                return self.conn

        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            return None

    def close_connection(self):
        if self.conn and self.conn.is_connected():
            self.conn.close()
            print('Connection closed.')

    def execute_query(self, query):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.conn.commit()
            cursor.close()
            print("Query executed successfully.")
        except Error as e:
            print(f"Error executing query: {e}")

    def import_csv_to_mysql(self, csv_file, table_name):
        try:
            df = pd.read_csv(csv_file)
            print(df.head())
            
            # self.execute_query("CREATE DATABSE sensors;")
            self.execute_query("USE sensors;")
            print("using sensors")

            # # Drop existing table if it exists
            # drop_table_query = f"DROP TABLE IF EXISTS {table_name}"
            # self.execute_query(drop_table_query)

            # Create new table
            # create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ("
            # for column in df.columns:
            #     create_table_query += f"{column} FLOAT(255), "
            # create_table_query = create_table_query[:-2] + ");"
            self.execute_query("CREATE TABLE IF NOT EXISTS sensor_data (temperature FLOAT, humidity INT,pressure INT,random_date DATE,random_year INT);")
            print("creating table")

            # Insert data into the table
            cursor = self.conn.cursor()
            for _, row in df.iterrows():
                insert_query = f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES ({', '.join(['%s'] * len(df.columns))});"
                cursor.execute(insert_query, tuple(row))
                print(insert_query)
            self.conn.commit()
            cursor.close()

            print(f"CSV file '{csv_file}' imported into MySQL table '{table_name}' successfully.")

        except Error as e:
            print(f"Error importing CSV file into MySQL: {e}")

    def fetch_data(self, query):
        try:
            df = pd.read_sql(query, self.conn)
            return df
        except Error as e:
            print(f"Error fetching data: {e}")
            return None

if __name__ == "__main__":
    mysql_conn = MySQLConnection()
    mysql_conn.start_connection()

    mysql_conn.import_csv_to_mysql('sensor.csv', 'sensor_data')
    # mysql_conn.execute_query("use sensors;")

    sensor_data = mysql_conn.fetch_data("USE sensors; SELECT * FROM sensor;")
    # sensor_data = pd.DataFrame(sensor_data)
    print(sensor_data)
    
    mysql_conn.close_connection()

