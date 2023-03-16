import faker
from colorama import Fore, Style
import time


class Police:
    def __init__(self):
        fake = faker.Faker()
        self.name = "Detective " + fake.name()
        self.active = True

    def check_boat(self, boat):
        boat.checked_by_police = "Yes"
        self.active = False
        print(f"{Fore.LIGHTRED_EX}POLICE{Style.RESET_ALL}: {self.name} is going to search {boat.name}.")
        time.sleep(5)
        if boat.merchandise == "Cocaine":
            print(f"{Fore.LIGHTRED_EX}POLICE{Style.RESET_ALL}: {self.name} found something illegal in {boat.name}.")
            self.active = True

            return True
        else:
            print(f"{Fore.LIGHTRED_EX}POLICE{Style.RESET_ALL}: {self.name} found nothing.")
            self.active = True

            return False