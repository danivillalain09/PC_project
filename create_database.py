import pandas as pd
import mysql.connector


def create_database():

    """Creates a database with the given name and password."""
    password = input("Enter the password for the mysql connection: ")

    database_name = input("Enter the name of the database: ")
    connection_successful = False

    while not connection_successful:
        try:
            connection = mysql.connector.connect(password=password, host="127.0.0.1", database=database_name)
            connection_successful = True
        except mysql.connector.errors.ProgrammingError as err:
            print("Connection to database failed. Please try again...")
            password = input("Enter the password: ")
            database_name = input("Enter the name of the database: ")

    return database_name, password