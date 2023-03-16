import threading
from Police import Police
import random
import time
from colorama import Fore, Style


class Control:
    def __init__(self, n_boats, n_docks, sql_connection, starting_time):
        # OVERALL SIMULATION VARIABLES
        self.number_of_boats = n_boats
        self.finished_boats = 0
        self.sql = sql_connection
        self.start = starting_time
        self.entered_employees_sql = False

        # FOR WORKERS
        self.workers = []
        self.active_workers = []  # This is the list of active workers.
        self.active_workers_locker = threading.Lock()  # Lock for the threads to not collide.
        self.finished = False  # This is the variable that will be used to end the simulation.

        # FOR POLICE
        self.police = Police()

        # FOR BOATS
        self.docks = dict()
        self.add_dock(n_docks)
        self.entrance_queue = []
        self.entrance_queue_locker = threading.Lock()
        self.boat_request = []
        self.boat_request_locker = threading.Lock()
        self.container_storage = dict()
        self.add_storage()
        self.employee_track = dict()

    def add_dock(self, n_docks):
        for x in range(n_docks):
            model = "Dock " + str(x + 1)
            self.docks[model] = {
                "Type": random.choice(["Type 1", "Type 2"]),
                "Boat": None,
                "Crane": None,
                "Containers": []
            }

    def add_storage(self):
        for x in range(1, 4):
            model = "Storage " + str(x)
            self.container_storage[model] = {
                "Containers": [],
                "Locker": threading.Lock()
            }

    def refuel(self, boat):
        time.sleep(2)
        boat.fuel = 500
        return True

    def entrance_confirmation(self, boat):
        if boat.priority != 0:
            time.sleep(3)
            boat.priority = self.entrance_queue.index(boat)

            return False

        else:
            return True

    def call_police(self, boat):
        if boat.checked_by_police == "No" and self.police.active:
            illegal = self.police.check_boat(boat)
            if illegal:
                return "Alarm"

    def dock_response_entry(self, boat):
        found = False
        allowed = "Yes"
        if random.randint(1, 20) == 1:
            if self.call_police(boat) == "Alarm":
                print(f"Police has been called for {boat.name}")
                allowed = "No"

        if allowed == "Yes":
            while not found:
                for docks in self.docks:
                    if self.docks[docks]["Boat"] is None and len(self.docks[docks]["Containers"]) == 0:
                        self.docks[docks]["Boat"] = boat

                        return docks
                    else:  # If there is no space for the boat.
                        continue
        else:
            return "You are not allowed to enter the port"

    def crane_request(self, job, selected_boat):
        found = False
        for worker in self.active_workers:
            if worker.job == job:
                self.active_workers.remove(worker)
                unloading = worker.work(job, selected_boat)

                while not unloading:
                    time.sleep(2)

                self.active_workers.append(worker)
                found = True
                break
            else:
                continue

        return found

    def calculate_price(self, boat, start):
        time_in_port = time.time() - start
        if boat.model == "Model 1":
            boat.price = int((time_in_port * 0.15) * ((boat.value_in_market * 0.15) + (boat.containers * 0.15)))
        elif boat.model == "Model 2":
            boat.price = int((time_in_port * 0.17) * ((boat.value_in_market * 0.17) + (boat.containers * 0.17)))
        elif boat.model == "Model 3":
            boat.price = int((time_in_port * 0.20) * ((boat.value_in_market * 0.20) + (boat.containers * 0.20)))
        else:
            boat.price = 100000

    def dock_response_leave(self, boat, boat_dock):
        self.call_transporter(boat)
        if self.docks[boat_dock]["Boat"] is boat:
            self.docks[boat_dock]["Boat"] = None
        else:
            print("Error: Boat not in dock.")

    def leave_confirmation(self):
        self.finished_boats += 1  # Cada vez que un barco sale, se suma uno a la variable.
        # Si llega a ser igual al número de barcos, se manda un mensaje a los trabajadores para que terminen.
        if self.finished_boats == self.number_of_boats:
            self.finished = True

    def call_transporter(self, boat):
        for worker in self.active_workers:
            if worker.job == "Transporter":
                self.active_workers.remove(worker)
                print(f"{Fore.LIGHTBLUE_EX}CONTROL{Style.RESET_ALL}: A transporter has been called to {boat.dock}.")
                worker.work(job="Transporter", boat=boat)
                self.active_workers.append(worker)
                break

    def insert_sql(self, command, column, object, starting_time):
        while self.sql.sql_locker.locked():
            time.sleep(1)

        self.sql.sql_locker.acquire()
        if command == "Arrival":
            self.sql.insert_boats_arrivals(starting_time, object)
        elif command == "Departure":
            self.sql.insert_boats_departures(starting_time, object)
        elif command == "Time":
            self.sql.insert_boats_time(column, starting_time, object)
        elif command == "Initial":
            self.sql.insert_values_initial(object)
        elif command == "Machines":
            self.sql.insert_machines(object)
        elif command == "Machines_Usage":
            self.sql.insert_machines_used(object)
        elif command == "Containers":
            self.sql.insert_containers(object)
        elif command == "Employees":
            self.sql.insert_values_employees(object)
        else:
            print("Error: Command not found.")
        self.sql.sql_locker.release()

    def simulation(self):
        for worker in self.workers:
            self.sql.sql_locker.acquire()
            query = f"INSERT INTO Employees_Race (Employee, Machine, Picture) VALUES('{worker.name}','{worker.machine.name}','{worker.picture}');"
            self.sql.cursor.execute(query)
            self.sql.cnx.commit()
            time.sleep(1)
            self.sql.sql_locker.release()

        while not self.finished:
            time_to_record = int(time.time() - self.start)
            if time_to_record % 10 == 0:
                column_name = "Time_" + str(time_to_record)
                self.employee_track[column_name] = dict()
                for worker in self.workers:
                    self.employee_track[column_name][worker] = worker.number_containers
            time.sleep(1)

        for column in self.employee_track:
            self.sql.sql_locker.acquire()
            query = "ALTER TABLE Employees_Race ADD {} INT ".format(column.capitalize())
            self.sql.cursor.execute(query)
            self.sql.cnx.commit()
            for worker in self.employee_track[column]:
                query = f"UPDATE Employees_Race SET {column} =({self.employee_track[column][worker]}) WHERE Employee=('{worker.name}');"
                self.sql.cursor.execute(query)
            self.sql.cnx.commit()
            self.sql.sql_locker.release()