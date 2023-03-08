import mysql.connector
import threading
import time


class SQLConnection:
    def __init__(self, password, database_name):
        self.cnx = mysql.connector.connect(password=password, host="127.0.0.1", database=database_name)
        self.cursor = self.cnx.cursor()
        self.create_tables()
        self.sql_locker = threading.Lock()

    def create_tables(self):
        try:
            self.cursor.execute("CREATE TABLE Boats (Boat VARCHAR(255))")
            self.cursor.execute("CREATE TABLE Boats_arrivals (Boat VARCHAR(255), Dock VARCHAR(255), Arrival_time INT, Departure_time INT)")
            self.cursor.execute("CREATE TABLE Machines (Machine VARCHAR(255))")
            self.cursor.execute("CREATE TABLE Employees (Employee VARCHAR(255))")
            self.cursor.execute("CREATE TABLE Storage_Area (Number VARCHAR(255))")
            self.cursor.execute("CREATE TABLE Employees_Race (Employee VARCHAR(255), Machine VARCHAR(255), Picture VARCHAR(255))")

        except mysql.connector.errors.ProgrammingError:
            print("Creating the table...")
            time.sleep(2)
            print("Creating the table...")
            time.sleep(2)
            self.cursor.execute("DROP TABLE Boats")
            self.cursor.execute("DROP TABLE Boats_arrivals")
            self.cursor.execute("DROP TABLE Machines")
            self.cursor.execute("DROP TABLE Employees")
            self.cursor.execute("DROP TABLE Storage_Area")
            self.cursor.execute("DROP TABLE Employees_Race")
            self.cursor.execute("CREATE TABLE Boats (Boat VARCHAR(255))")
            self.cursor.execute("CREATE TABLE Boats_arrivals (Boat VARCHAR(255), Dock VARCHAR(255), Arrival_time INT, Departure_time INT)")
            self.cursor.execute("CREATE TABLE Machines (Machine VARCHAR(255))")
            self.cursor.execute("CREATE TABLE Employees (Employee VARCHAR(255))")
            self.cursor.execute("CREATE TABLE Storage_Area (Number VARCHAR(255))")
            self.cursor.execute("CREATE TABLE Employees_Race (Employee VARCHAR(255), Machine VARCHAR(255), Picture VARCHAR(255))")
            time.sleep(2)
            print("Table created successfully!")