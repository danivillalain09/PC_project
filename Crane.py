import threading
import random
import time
from colorama import Fore, Style


class Crane:
    def __init__(self, name):
        self.name = name
        self.locker = threading.Lock()
        self.active = False
        self.speed = random.randint(5, 8)
        self.residual_value = random.randint(10000, 50000)
        self.fuel_consumption = int(self.speed * 1.5)
        self.refueled = "No"
        self.fuel_capacity = 1000
        self.fuel_level = random.randint(0, self.fuel_capacity)
        self.times_used = 0
        self.bought = random.choice(["Purchased", "Leased"])

    def use_machine(self):
        self.times_used += 1
        time.sleep(self.speed)
        self.fuel_level -= self.fuel_consumption * self.speed
        if self.fuel_level <= 10:
            print(f"{Fore.YELLOW} WORKER:{Style.RESET_ALL} Fuel level too low.")
            self.refueled = "Yes"
            time.sleep(6)
            self.fuel_level = self.fuel_capacity
            print(f"{Fore.YELLOW} WORKER:{Style.RESET_ALL} Refueled.")

        return True