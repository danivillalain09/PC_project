import time
from colorama import Fore, Style
import concurrent.futures
from Control import Control
from Boat import Boats
from Worker import Worker
from Container import Container
from Crane import Crane
import traceback


def run_simulation(connection, number_of_boats, number_of_docks, number_of_cranes, number_of_transporters):
    try:
        number_of_workers = int(number_of_cranes + number_of_transporters)
        sql = connection
        start = time.time()
        starting_number = sql.get_starting_number()
        print("The strating number is", starting_number)
        print("The number of boats is", number_of_boats)
        print("The number of docks is", number_of_docks)
        print("The number of cranes is", number_of_cranes)
        print("The number of transporters is", number_of_transporters)
        print("The number of workers is", number_of_workers)

        control = Control(number_of_boats, number_of_docks, sql, start)
        sql.add_columns(Boats(1, control, sql, 0), Container(0, 0, "E", "S", "C"),
                        Worker(0, control, "Crane"), Crane("Crane"))

        with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_cranes) as executor:
            worker_list = [Worker(i + 1, control, "Crane") for i in range(number_of_cranes)]
            for index, worker_list in enumerate(worker_list):
                executor.submit(worker_list.simulation)

            with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_transporters) as executor:
                worker_list = [Worker(i, control, "Transporter") for i in
                               range(number_of_cranes + 1, number_of_workers + 1)]
                for index, worker_list in enumerate(worker_list):
                    executor.submit(worker_list.simulation)

                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    executor.submit(control.simulation)

                    print("----------------------------------------------------------------------")
                    print(f"{Fore.CYAN}WELCOME TO THE PROGRAM SIMULATION!{Style.RESET_ALL}\n"
                          f"Here you will create a database of boat arrivals to an specific port. Let's start!")
                    print("----------------------------------------------------------------------")

                    if number_of_boats >= 40:
                        number_of_threads = number_of_boats / 2
                    elif number_of_boats > 60:
                        number_of_threads = number_of_boats / 3
                    else:
                        number_of_threads = number_of_boats

                    with concurrent.futures.ThreadPoolExecutor(max_workers=int(number_of_threads)) as executor:
                        boat_list = [Boats(i, control, sql, start) for i in
                                     range(starting_number, starting_number + number_of_boats)]
                        for index, boat in enumerate(boat_list):
                            executor.submit(boat.simulation)


    except Exception:
        traceback.print_exc()