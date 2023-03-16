import mysql.connector
import threading
import time
import pandas as pd
import copy


class Connection:
    def __init__(self, password, database, reset_database):
        self.reset_database = reset_database
        self.cnx = mysql.connector.connect(user="root",
                                           password=password,
                                           host="127.0.0.1",
                                           database=database,
                                           ssl_disabled=True)

        self.cursor = self.cnx.cursor()
        self.create_new_tables()
        self.sql_locker = threading.Lock()

    def create_new_tables(self):
        if self.reset_database:
            try:
                self.cursor.execute("CREATE TABLE Boats (Boat VARCHAR(255))")
                self.cursor.execute("CREATE TABLE Boats_arrivals (Boat VARCHAR(255), Dock VARCHAR(255), Arrival_time INT, Departure_time INT)")
                self.cursor.execute("CREATE TABLE Machines (Machine VARCHAR(255))")
                self.cursor.execute("CREATE TABLE Employees (Employee VARCHAR(255))")
                self.cursor.execute("CREATE TABLE Storage_Area (Number VARCHAR(255))")
                self.cursor.execute("CREATE TABLE Employees_Race (Employee VARCHAR(255), Machine VARCHAR(255), Picture VARCHAR(255))")

            except mysql.connector.errors.ProgrammingError:
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

    def add_columns(self, boat, container, employee, machine):
        if self.reset_database:
            boat_attributes = vars(boat)
            for keys in boat_attributes:
                format = type(boat_attributes[keys])
                format = str(format)
                if keys == "sql" or keys == "mediator" or keys == "active" or keys == "priority" or keys == "name" \
                        or keys == "start" or keys == "price" or keys == "disable_delay" or keys == "disable_priority":
                    continue
                if format == "<class 'str'>" or keys == "dock":
                    query = "ALTER TABLE Boats ADD {} VARCHAR (255)".format(keys.capitalize())
                elif format == "<class 'datetime.datetime'>" or format == "<class 'datetime.date'>":
                    query = "ALTER TABLE Boats ADD {} datetime".format(keys.capitalize())
                else:
                    query = "ALTER TABLE Boats ADD {} INT ".format(keys.capitalize())
                self.cursor.execute(query)

            column_list = ["Time_in_queue", "Time_waiting_confirmation", "Time_in_dock", "Time_leaving",
                           "Amount_Charged"]
            for column in column_list:
                query = "ALTER TABLE Boats_arrivals ADD {} INT".format(column.capitalize())
                self.cursor.execute(query)

            machine = vars(machine)
            for keys in machine:
                format = type(machine[keys])
                format = str(format)
                if keys == "locker" or keys == "active" or keys == "name":
                    continue
                if format == "<class 'str'>":
                    query = "ALTER TABLE Machines ADD {} VARCHAR (255)".format(keys.capitalize())
                else:
                    query = "ALTER TABLE Machines ADD {} INT ".format(keys.capitalize())
                self.cursor.execute(query)

            employee = vars(employee)
            for keys in employee:
                format = type(employee[keys])
                format = str(format)
                if keys == "mediator" or keys == "boat" or keys == "active" or keys == "dock" \
                        or keys == "finished" or keys == "name" or keys == "number_containers":
                    continue
                if format == "<class 'str'>" or keys == "dock" or format == "<class '__main__.Crane'>" or keys == "machine":
                    query = "ALTER TABLE Employees ADD {} VARCHAR (255)".format(keys.capitalize())
                else:
                    query = "ALTER TABLE Employees ADD {} INT ".format(keys.capitalize())
                self.cursor.execute(query)

            container = vars(container)
            for keys in container:
                format = type(container[keys])
                format = str(format)
                if keys == "number":
                    continue
                if format == "<class 'str'>":
                    query = "ALTER TABLE Storage_Area ADD {} VARCHAR (255)".format(keys.capitalize())
                else:
                    query = "ALTER TABLE Storage_Area ADD {} INT ".format(keys.capitalize())
                self.cursor.execute(query)

    def get_starting_number(self):
        self.cursor.execute("SELECT Boat FROM Boats")
        result = self.cursor.fetchall()
        result_list = []
        for x in result:
            x = x[0]
            x = x.split(" ")
            x = x[1]
            result_list.append(int(x))
        if len(result_list) == 0:
            maximum = 0 + 1
        else:
            maximum = max(result_list) + 1

        return maximum

    def insert_values_initial(self, boat):
        copy_boat = copy.copy(boat)
        attributes = vars(copy_boat)
        attributes.pop("sql")
        attributes.pop("mediator")
        attributes.pop("active")
        attributes.pop("priority")
        attributes.pop("start")
        attributes.pop("price")
        attributes.pop("disable_delay")
        attributes.pop("disable_priority")

        query = "INSERT INTO Boats VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s)"
        values = tuple(attributes.values())
        self.cursor.execute(query, values)

        self.cnx.commit()

    def insert_values_employees(self, employee):
        copy_employee = copy.copy(employee)
        attributes = vars(copy_employee)
        attributes.pop("finished")
        attributes.pop("mediator")
        attributes.pop("active")
        attributes.pop("boat")
        attributes.pop("dock")
        attributes.pop("number_containers")
        attributes["machine"] = employee.machine.name
        query = "INSERT INTO Employees VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = tuple(attributes.values())
        self.cursor.execute(query, values)

        self.cnx.commit()

    def insert_boats_arrivals(self, starting_time, boat):
        query = f"INSERT INTO Boats_arrivals (Boat, Arrival_time) VALUES ('{boat.name}',{time.time() - starting_time});"
        self.cursor.execute(query)
        self.cnx.commit()

    def insert_boats_departures(self, starting_time, boat):
        query = f"UPDATE Boats_arrivals SET Departure_time= ({time.time() - starting_time}) WHERE Boat =('{boat.name}');"
        self.cursor.execute(query)
        query = f"UPDATE Boats_arrivals SET Amount_charged=({int(boat.price)}) WHERE Boat =('{boat.name}');"
        self.cursor.execute(query)
        self.cnx.commit()

    def insert_boats_time(self, column_name, starting_time, boat):
        if column_name == "Time_in_dock":
            self.cursor.execute(
                f"UPDATE Boats_arrivals SET {column_name}=({time.time() - starting_time}) WHERE Boat=('{boat.name}');")
            column_name = "Dock"
            self.cursor.execute(
                f"UPDATE Boats_arrivals SET {column_name}=('{boat.dock}') WHERE Boat=('{boat.name}');")
        else:
            self.cursor.execute(
                f"UPDATE Boats_arrivals SET {column_name}=({time.time() - starting_time}) WHERE Boat=('{boat.name}');")

        self.cnx.commit()

    def insert_machines(self, machine):
        copy_machine = copy.copy(machine)
        attributes = vars(copy_machine)
        attributes.pop("locker")
        attributes.pop("active")
        query = "INSERT INTO Machines VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = tuple(attributes.values())
        self.cursor.execute(query, values)

        self.cnx.commit()

    def insert_containers(self, container):
        container = copy.copy(container)
        attributes = vars(container)
        query = "INSERT INTO Storage_Area VALUES (%s, %s, %s, %s, %s)"
        values = tuple(attributes.values())
        self.cursor.execute(query, values)

        self.cnx.commit()



