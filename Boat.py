import faker
import random
import time
from colorama import Fore, Style
from datetime import date
import traceback


class Boats:
    def __init__(self, name, port_object, sql_connection, starting_time):
        # Attributes that make the boat know the other instances.
        fake = faker.Faker()
        self.name = "Boat " + str(name)  # Name of the boat
        self.mediator = port_object  # Port Object
        self.sql = sql_connection  # SQL Connection

        # Attributes that make the boat know its own state.
        self.active = False  # If the boat is active or not
        self.disable_delay = True  # Disable delay
        self.disable_priority = True  # Disable priority

        # Attributes that modify during the execution.
        self.priority = None  # Priority in the queue
        self.dock = None  # Dock where the boat is.
        self.start = starting_time

        # Attributes to fill in the table.
        self.destination = "Spain"
        self.place_of_origin = random.choice(['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czechia', 'Denmark',
                                          'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Ireland',
                                          'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands',
                                          'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Sweden'])
        self.departure_date = fake.date_time_between(start_date='-1y', end_date='now')
        self.arrival_date = date.today()
        self.model = random.choice(["Model 1", "Model 2", "Model 3"])
        self.fuel = random.randint(100, 500)
        self.refueled = "No"
        self.merchandise = "Item1"
        self.containers = 0
        self.checked_by_police = "No"
        self.price = 0
        self.value_in_market = 0
        self.initialise_attributes()

    def initialise_attributes(self):
        if self.model == "Model 1":
            self.containers = random.randint(20, 50)
        elif self.model == "Model 2":
            self.containers = random.randint(51, 150)
        else:
            self.containers = random.randint(151, 250)

        item_list, price_list = ["Fruit", "Vegetables", "Clothes", "Technology", "Construction Material", "Toys"], \
                                [5, 6, 30, 150, 200, 10]
        key_value_of_items = dict(zip(item_list, price_list))
        self.merchandise = random.choice(item_list)

        self.value_in_market = self.containers * key_value_of_items[self.merchandise]

        if random.randint(1, 200) == 1:
            self.merchandise = "Cocaine"

    def delay_in_arriving(self):
        if not self.disable_delay:
            while not self.active:
                time.sleep(5)
                if random.randint(1, 3) == 2:
                    self.active = True
        # print(f"{Fore.LIGHTBLUE_EX}CONTROL{Style.RESET_ALL}: {self.name} has arrived.")

    def get_into_queue(self):
        self.mediator.entrance_queue_locker.acquire()
        self.mediator.entrance_queue.append(self)
        self.priority = self.mediator.entrance_queue.index(self)
        self.mediator.entrance_queue_locker.release()

    def ask_entry_port(self):
        if not self.disable_priority:

            while not self.mediator.entrance_confirmation(self):
                time.sleep(1)
                continue

            print(f"{Fore.LIGHTBLUE_EX}CONTROL{Style.RESET_ALL}: {self.name} has entered the port.")

    def out_of_queue(self):
        time.sleep(3)
        self.mediator.entrance_queue_locker.acquire()
        self.mediator.entrance_queue.remove(self)
        self.mediator.entrance_queue_locker.release()

    def ask_entry_dock(self):
        self.dock = self.mediator.dock_response_entry(self)
        while self.dock is None or self.dock == "You are not allowed to enter the port":
            if self.dock == "You are not allowed to enter the port":
                self.active = False
                self.mediator.leave_confirmation()
                self.mediator.insert_sql(command="Initial", column=None, boat=self, starting_time=None)
                exit()
            print(f"{self.name} cannot enter the port.")

            time.sleep(3)
        else:
            print(f"{Fore.LIGHTBLUE_EX}CONTROL{Style.RESET_ALL}: {self.name} has docked in {self.dock}.")
            pass

    def refuel_ask(self):
        if self.fuel <= 200:
            refueled = self.mediator.refuel(self)
            self.refueled = "Yes"

            while not refueled:
                time.sleep(1)
                continue

            print(f"{Fore.LIGHTBLUE_EX}CONTROL{Style.RESET_ALL}: {self.name} has refueled.")

    def unload_request(self, job):
        while not self.mediator.crane_request(job, selected_boat=self):
            print(f"{Fore.RED}CONTROL: {self.name} did not find a {job}.{Style.RESET_ALL}")
            time.sleep(3)

    def ask_leave_dock(self):
        self.mediator.dock_response_leave(self, self.dock)
        print(f"{Fore.LIGHTBLUE_EX}CONTROL{Style.RESET_ALL}: {self.name} has left {self.dock}.")
        time.sleep(random.randint(1, 6))

    def ask_leave_port(self):
        self.mediator.leave_confirmation()
        print(f"{Fore.LIGHTBLUE_EX}CONTROL{Style.RESET_ALL}: {self.name} has left the port.")

    def simulation(self):
        try:
            self.delay_in_arriving()
            self.mediator.insert_sql(command="Arrival", column=None, object=self, starting_time=self.start)
            activity_time = time.time()
            self.get_into_queue()
            self.ask_entry_port()
            self.out_of_queue()
            self.refuel_ask()
            self.mediator.insert_sql(command="Time", column="Time_in_queue", object=self, starting_time=activity_time)
            activity_time = time.time()
            self.ask_entry_dock()
            self.mediator.insert_sql(command="Time", column="Time_waiting_confirmation", object=self,
                                     starting_time=activity_time)
            activity_time = time.time()
            self.unload_request("Crane")
            self.mediator.insert_sql(command="Time", column="Time_in_dock", object=self, starting_time=activity_time)
            activity_time = time.time()
            self.ask_leave_dock()
            self.ask_leave_port()
            self.mediator.insert_sql(command="Time", column="Time_leaving", object=self, starting_time=activity_time)
            self.mediator.calculate_price(self, self.start)
            self.mediator.insert_sql(command="Departure", column=None, object=self, starting_time=self.start)
            self.mediator.insert_sql(command="Initial", column=None, object=self, starting_time=None)

        except Exception:
            traceback.print_exc()