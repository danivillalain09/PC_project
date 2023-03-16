import streamlit as st
import mysql.connector
import plotly.express as px
import pandas as pd
from SqlConnection import Connection
from Simulation import run_simulation


# Define the login page
def login_page():
    st.title("Welcome to the login page!")
    st.write("Please enter your credentials below to log in.")

    # Add input fields for username and password
    st.session_state["password"] = st.text_input("Password for mysql connection:", type="password")

    # Add a checkbox to input a new database name
    new_database_name = st.checkbox("Create a new database (default: project)")
    # If the box is checked, add an input field to input the new database name
    if new_database_name:
        st.session_state["database"] = st.text_input("New database name:")
    else:
        st.session_state["database"] = "project"

    # Add a submit button
    submit_button = st.button("Log in")

    # Check if the username and password are correct when the submit button is pressed
    if submit_button:
        # Try to connect to the database
        try:
            cnx = mysql.connector.connect(password=st.session_state["password"], host="127.0.0.1", database=st.session_state["database"])
            cnx.close()
            connection_failed = False

        except mysql.connector.errors.ProgrammingError:
            connection_failed = True

        if not connection_failed:
            # st.success("Logged in!")
            # Set the logged_in state to True after a successful login
            st.session_state["page_view"] += 1
            st.experimental_rerun()
        else:
            st.error("Incorrect sql password or database name. Please try again.")


# Define the main content of the app
def presentation_page():
    st.title("Boat Port Simulation Results")
    st.image("Pictures/port_picture.jpeg", use_column_width=True)
    st.markdown("---")

    # Sidebar for input parameters
    st.sidebar.title("Input Parameters")
    st.session_state["num_boats"] = st.sidebar.number_input("Number of boats:", min_value=1, max_value=100, value=10, step=1)
    st.session_state["num_ports"] = st.sidebar.number_input("Number of ports:", min_value=1, max_value=10, value=2, step=1)
    st.session_state["num_cranes"] = st.sidebar.number_input("Number of cranes:", min_value=1, max_value=7, value=1, step=1)
    st.session_state["num_transporters"] = st.sidebar.number_input("Number of transporters:", min_value=1, max_value=7, value=1, step=1)
    erase_database = st.sidebar.checkbox("Do you want to reset the database?")

    if erase_database:
        st.session_state["reset_database"] = True
    else:
        st.session_state["reset_database"] = False

    st.sidebar.submit_button = st.button("Submit input parameters")

    if st.sidebar.submit_button:
        st.session_state["page_view"] += 1
        st.experimental_rerun()


def pre_processing_page():
    st.header("This is the loading page.")
    st.write("The input parameters are:")
    st.write("Number of boats:", st.session_state["num_boats"])
    st.write("Number of ports:", st.session_state["num_ports"])
    st.write("Number of cranes:", st.session_state["num_cranes"])
    st.write("Number of transporters:", st.session_state["num_transporters"])

    #Aqui se corre la simulación y se obtienen los resultados en la base de datos.
    cpad1, col1, col2, pad2 = st.columns((10, 5, 8, 10))

    with col1:
        button_return = st.button("<- Return")
    with col2:
        button_advance = st.button("Run simulation ->")

    # Después hay otra página en la que se ven las insights.
    if button_advance:
        st.session_state["page_view"] += 1
        st.experimental_rerun()
    elif button_return:
        if not st.session_state["rerun"]:
            st.session_state["page_view"] -= 1
            st.experimental_rerun()
        else:
            st.session_state["page_view"] = 6
            st.experimental_rerun()


def loading_page():
    st.header("This is the loading page.")
    st.write("Please wait patiently to see the results.")

    # Connect to the database
    st.session_state["connection"] = Connection(st.session_state["password"], st.session_state["database"], st.session_state["reset_database"])
    run_simulation(st.session_state["connection"], st.session_state["num_boats"], st.session_state["num_ports"], st.session_state["num_cranes"], st.session_state["num_transporters"])

    st.write("The simulation has finished.")

    st.session_state["page_view"] += 1
    st.experimental_rerun()


def insights_page():
    st.header('_Insights_ :sunglasses:')
    df_boats = st.session_state["connection"].get_dataset("boats")
    df_boats_arrivals = st.session_state["connection"].get_dataset("boats_arrivals")
    df_employees = st.session_state["connection"].get_dataset("employees")

    st.write(
        "____________________________________________________________________________________________________________")
    st.subheader('**Boats**')
    st.write("In order to asses the efficiency of the port we can see the following insights: ")
    con_moved = df_boats["Containers"].sum()
    st.write(f"The total number of containers moved in the port is: {con_moved}.")
    mv_moved = df_boats["Value_in_market"].sum()
    st.write(f"The value of those containers where {mv_moved}€.")

    st.write(
        "____________________________________________________________________________________________________________")
    st.subheader('**Salary**')
    total_salary = df_employees["Salary"].mean()
    avg_work_time = df_employees["Workday_time"].mean()
    st.write(f"The average salary of the employees is: {total_salary}€.")
    st.write(f"Moreover, the average work schedule of the employees is: {avg_work_time}.")
    st.write(
        f"Therefore, with a simple calculation, the average cost on salaries per min: {round(total_salary / avg_work_time, 2)}.")
    st.write(
        "____________________________________________________________________________________________________________")
    st.subheader('**Worst Performance Employee**')
    st.write("Now, we can analyse the performance of the employees in the port.")
    df_employee_min = df_employees.sort_values(by='Working_time', ascending=True)
    df_employee_min = df_employee_min.reset_index(drop=True)
    name = df_employee_min.loc[0][0]
    picture = df_employee_min.loc[0][2]
    work_time = df_employee_min.loc[0][-3]
    total_time = df_employee_min.loc[0][-4]
    percentage_time = int((work_time / total_time) * 100)
    st.write(f"The employee that has worked the least is: {name}.")
    st.write(f"The {name} worked {work_time} mins out of a total {total_time} mins. ({percentage_time}%)")

    col1, col2, col3 = st.columns(3)
    col1.metric("Name", str(name))
    col2.metric("Work Time", str(work_time) + " mins")
    col3.metric("Percentage of total time", str(percentage_time) + "%")
    st.image(picture, width=200)
    st.write(
        "____________________________________________________________________________________________________________")
    st.subheader('**Best Performance Employee**')
    st.write("On the other hand, we can see the employee that has worked the most: ")
    df_employee_max = df_employees.sort_values(by='Working_time', ascending=False)
    df_employee_max = df_employee_max.reset_index(drop=True)

    name = df_employee_max.loc[0][0]
    picture = df_employee_max.loc[0][2]
    work_time = df_employee_max.loc[0][-3]
    total_time = df_employee_max.loc[0][-4]
    percentage_time = int((work_time / total_time) * 100)
    st.write(f"The employee that has worked the most is: {name}.")
    st.write(f"The {name} worked {work_time} mins out of a total {total_time} mins. ({percentage_time}%)")

    col1, col2, col3 = st.columns(3)
    col1.metric("Name", str(name))
    col2.metric("Work Time", str(work_time) + " mins")
    col3.metric("Percentage", str(percentage_time) + "%")
    st.image(picture, width=200)
    st.write(
        "____________________________________________________________________________________________________________")
    st.subheader('**Crane VS Transporter**')
    st.write("Another interesting insight is made by comparing the crane workers and the transporter workers. ")

    crane_df = df_employees[df_employees['Job'] == "Crane"]
    trans_df = df_employees[df_employees['Job'] == "Transporter"]
    st.write("For crane workers: ")
    st.write(f"The average age is {round(crane_df['Age'].mean())}.")
    st.write(f"The average salary is: {round(crane_df['Salary'].mean())}€.")
    st.write(f"The average schedule time is: {crane_df['Workday_time'].mean()}.")
    st.write(f"The average working time is: {crane_df['Working_time'].mean()}.")
    st.write(f"The average number of breaks is: {round(crane_df['Breaks'].mean())}.")
    st.write(f"And the average time spent in breaks is {round(crane_df['Time_in_break'].mean())}.")
    st.write("")
    st.write(
        "____________________________________________________________________________________________________________")
    st.subheader('**Crane VS Transporter**')
    st.write("On the other hand, for transporter workers: ")
    st.write(f"The average age is {round(trans_df['Age'].mean())}.")
    st.write(f"The average salary is: {round(trans_df['Salary'].mean())}€.")
    st.write(f"The average schedule time is: {trans_df['Workday_time'].mean()}.")
    st.write(f"The average working time is: {trans_df['Working_time'].mean()}.")
    st.write(f"The average number of breaks is: {round(trans_df['Breaks'].mean())}.")
    st.write(f"And the average time spent in breaks is {round(trans_df['Time_in_break'].mean())}.")

    st.write(
        "____________________________________________________________________________________________________________")
    st.subheader('**Revenue**')
    revenue = df_boats_arrivals["Amount_charged"].sum()
    revenue_boat = round(revenue / len(df_boats_arrivals))
    revenue_cont = round(revenue / con_moved)
    avg_rev_worker = round(con_moved / len(df_employees))
    st.write(f"The total revenue of the port is: {revenue}€.")
    st.write(f"The average revenue per boat is: {revenue_boat}€.")
    st.write(f"The average revenue per container is: {revenue_cont}€.")
    st.write(f"The average revenue per worker is: {avg_rev_worker}€.")
    st.write(
        "____________________________________________________________________________________________________________")
    st.subheader('**Boats Arrivals**')
    st.write(
        "Now, we can analyse the boats arrivals in the port. This is one of the most important metric we want to analyse."
        "With this time, we can better adjust how much we charge for the boats and how many containers we can move per day."
        "Moreover, we can see how efficient the port is working. In order to pass the queue, there needs to be space in the port and,"
        "for that, we need to move as fast as possible.")
    time_in_queue = round(df_boats_arrivals["Time_in_queue"].mean(), 2)
    st.write(f"The average time in queue is: {time_in_queue} mins.")

    st.write(
        "____________________________________________________________________________________________________________")
    st.subheader('**Graphics**')
    st.write("Now, we move on to analayse the values that the each of the boats have in the market. ")
    st.markdown('**Value of Boats**')
    st.write(
        "This is the distribution of the values of the boats that arrived to the port. The major insight of this chart is"
        "how much money the port has gained with each of the merchandise. For some people relying on just one merchandise "
        "might seem very risky. For others, it might be a good idea. What do you think?")

    df1 = df_boats.groupby('Merchandise')['Value_in_market'].sum()
    df2 = pd.DataFrame(df1)

    fig = px.bar(df2, x=df2.index, y="Value_in_market", title="Value of boats per merchandise")
    fig.update_xaxes(title_text='Merchandise')
    fig.update_yaxes(title_text='Number of Boats')
    st.plotly_chart(fig)

    cpad1, col1, col2, pad2 = st.columns((10, 5, 8, 10))

    with col1:
        button_return = st.button("<- Parameters")
    with col2:
        button_advance = st.button("Exit ->")

    # Después hay otra página en la que se ven las insights.
    if button_advance:
        st.session_state["page_view"] = 0
        st.experimental_rerun()
    elif button_return:
        st.session_state["page_view"] += 1
        st.session_state["reset_database"] = False
        st.session_state["rerun"] = True

        st.experimental_rerun()


def presentation_page_rerun():
    st.title("Boat Port Simulation Results")
    st.image("Pictures/port_picture.jpeg", use_column_width=True)
    st.markdown("---")

    # Sidebar for input parameters
    st.sidebar.title("Input Parameters")
    st.session_state["num_boats"] = st.sidebar.number_input("Number of boats:", min_value=1, max_value=100, value=10,
                                                            step=1)

    st.session_state["reset_database"] = False

    st.sidebar.submit_button = st.button("Submit input parameters")

    if st.sidebar.submit_button:
        st.session_state["page_view"] = 3
        st.experimental_rerun()


# Run the app
def main():
    # Initialize the session state variables.
    st.session_state.setdefault("page_view", 1)
    st.session_state.setdefault("password", False)
    st.session_state.setdefault("database", False)
    st.session_state.setdefault("num_boats", 0)
    st.session_state.setdefault("num_ports", 0)
    st.session_state.setdefault("num_cranes", 0)
    st.session_state.setdefault("num_transporters", 0)
    st.session_state.setdefault("reset_database", True)
    st.session_state.setdefault("rerun", False)

    # Check if the user is logged in
    if st.session_state["page_view"] == 1:
        login_page()
    elif st.session_state["page_view"] == 2:
        presentation_page()
    elif st.session_state["page_view"] == 3:
        pre_processing_page()
    elif st.session_state["page_view"] == 4:
        loading_page()
    elif st.session_state["page_view"] == 5:
        insights_page()
    elif st.session_state["page_view"] == 0:
        st.stop()
        exit()
    elif st.session_state["page_view"] == 6:
        presentation_page_rerun()
    else:
        st.write("Something went wrong")

main()