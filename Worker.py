import random
from Crane import Crane
from Transporter import Transporter
from Container import Container
import time
import faker


class Worker:
    def __init__(self, name, mediator, job):
        fake = faker.Faker()
        self.name = fake.name()
        self.nationality = random.choice(['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czechia', 'Denmark',
                                          'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Ireland',
                                          'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands',
                                          'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden'])
        self.picture = random.choice(["https://cdn.pixabay.com/photo/2015/01/27/09/58/man-613601__480.jpg", "https://cdn.pixabay.com/photo/2019/12/16/14/46/black-man-4699505_960_720.jpg",
         "https://cdn.pixabay.com/photo/2021/05/04/13/29/portrait-6228705_960_720.jpg", "https://cdn.pixabay.com/photo/2021/05/04/13/29/man-6228711_960_720.jpg",
         "https://www.maxpixel.net/static/photo/1x/Person-Male-Face-Portrait-Human-Teenage-Man-Boy-6040022.jpg", "https://cdn.pixabay.com/photo/2021/04/05/12/38/man-6153295_1280.jpg",
         "https://cdn.pixabay.com/photo/2021/06/04/10/29/man-6309454_1280.jpg", "https://upload.wikimedia.org/wikipedia/commons/4/48/Outdoors-man-portrait_%28cropped%29.jpg",
        "https://cdn.pixabay.com/photo/2022/08/06/11/01/black-woman-7368402__340.jpg", "https://cdn.pixabay.com/photo/2020/02/16/07/24/girl-4852804_960_720.jpg",
              "https://cdn.pixabay.com/photo/2015/09/09/22/04/woman-933684_960_720.jpg", "https://cdn.pixabay.com/photo/2018/06/15/19/53/young-woman-3477557_960_720.jpg",
              "https://cdn.pixabay.com/photo/2016/11/29/03/35/girl-1867092_960_720.jpg"])
        self.age = random.randint(22, 45)
        self.address = fake.street_name()

        self.mediator = mediator
        self.job = job

        if self.job == "Crane":
            self.machine = Crane("Crane " + str(name))
        if self.job == "Transporter":
            self.machine = Transporter("Transporter " + str(name))

        self.active = True
        self.dock = None
        self.boat = None
        self.finished = False
        if self.job == "Crane":
            self.salary = 200
        elif self.job == "Transporter":
            self.salary = 250
        self.workday_time = 0
        self.working_time = 0
        self.breaks = 0
        self.time_in_break = 0
        self.number_containers = 0

    def simulation(self):
        self.mediator.active_workers_locker.acquire()
        self.mediator.workers.append(self)
        self.mediator.active_workers.append(self)
        self.mediator.active_workers_locker.release()
        print(f"- {self.name} has started working: \n"
              f"    Machine: {self.machine.name}")

        start = time.time()
        time_until_break = time.time()
        while self.active:
            if self.breaks <= 1 and time.time() - time_until_break > random.randint(30, 50) and not self.machine.active:
                break_time = time.time()
                self.breaks += 1
                self.mediator.active_workers_locker.acquire()
                self.mediator.active_workers.remove(self)
                self.mediator.active_workers_locker.release()
                #print(f"{Fore.LIGHTYELLOW_EX}- {self.name} has stopped working.{Style.RESET_ALL}")
                time.sleep(random.randint(5, 10))
                self.time_in_break += time.time() - break_time
                time_until_break = time.time()
                self.mediator.active_workers_locker.acquire()
                self.mediator.active_workers.append(self)
                self.mediator.active_workers_locker.release()

            if self.mediator.finished:
                self.workday_time += time.time() - start
                self.mediator.insert_sql(command="Employees", column=None, object=self, starting_time=self)
                self.mediator.insert_sql(command="Machines", object=self.machine, column=None, starting_time=None)
                self.active = False
                self.finished = True
                exit()

            time.sleep(1)

    def work(self, job, boat):
        # print(f"{Fore.LIGHTMAGENTA_EX}- {self.name} is working.{Style.RESET_ALL}")
        start_working = time.time()
        self.machine.active = True
        self.boat = boat
        self.dock = self.boat.dock

        if job == "Crane":
            self.mediator.docks[self.dock]["Crane"] = self.machine
            job_finished = self.machine.use_machine()
            while not job_finished:
                time.sleep(2)
            for i in range(boat.containers):
                number = f"{boat.name.split(' ')[1]:0>3}{i:0>3}"
                container = Container(str(number), random.randint(100, 500), boat.place_of_origin, "Storage X",
                                      boat.merchandise)
                self.mediator.docks[self.dock]["Containers"].append(container)
            self.number_containers += boat.containers
            self.mediator.docks[self.dock]["Crane"] = None

        elif job == "Transporter":
            self.mediator.docks[self.dock]["Transporter"] = self.machine
            containers = self.mediator.docks[self.dock]["Containers"][:random.randint(50, 800)]
            self.machine.transport(self.mediator, containers)
            self.number_containers += len(containers)
            self.mediator.docks[self.dock]["Containers"] = []
            self.mediator.docks[self.dock]["Transporter"] = None

        # print(f"{Fore.LIGHTMAGENTA_EX}- {self.name} finished transporting.{Style.RESET_ALL}")
        self.working_time += time.time() - start_working
        self.machine.active = False
        self.boat = None
        self.dock = None

        return True