from Crane import Crane
from colorama import Fore, Style
import time
import random


class Transporter(Crane):
    def __init__(self, name):
        Crane.__init__(self, name)

    def transport(self, mediator, container_list):
        self.times_used += 1
        found_and_emptied = False
        while not found_and_emptied:
            for storage_areas in mediator.container_storage:
                storage_dictionary = mediator.container_storage[storage_areas]
                if storage_dictionary["Locker"].locked() or len(storage_dictionary["Containers"]) > 6000:
                    if len(storage_dictionary["Containers"]) > 6000:
                        print(f"{Fore.YELLOW} WORKER:{Style.RESET_ALL} Storage area {storage_areas} is full.")
                    continue
                else:
                    storage_dictionary["Locker"].acquire()
                    time.sleep(random.randint(1, 3))
                    for container in container_list:
                        container.place_stored = storage_areas
                        storage_dictionary["Containers"].append(container)
                        mediator.insert_sql(command="Containers", object=container, column=None, starting_time=None)
                    print(f"{Fore.YELLOW} WORKER:{Style.RESET_ALL}Transported containers to {storage_areas}.")
                    storage_dictionary["Locker"].release()
                    found_and_emptied = True
                    break