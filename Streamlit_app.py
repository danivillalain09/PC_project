import streamlit as st
import mysql.connector
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

    #if erase_database:
        #st.session_state["reset_database"] = True
    #else:
        #st.session_state["reset_database"] = False

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
        st.session_state["page_view"] -= 1
        st.experimental_rerun()


def loading_page():
    st.header("This is the loading page.")
    st.write("Please wait patiently to see the results.")

    # Connect to the database
    st.session_state["connection"] = Connection(st.session_state["password"], st.session_state["database"], st.session_state["reset_database"])
    simulation = run_simulation(st.session_state["connection"], st.session_state["num_boats"], st.session_state["num_ports"], st.session_state["num_cranes"], st.session_state["num_transporters"])

    st.write("The simulation has finished.")

    st.session_state["page_view"] += 1
    st.experimental_rerun()


def insights_page():
    st.header("This is the insights page.")
    st.write("The results are:")
    st.dataframe(st.session_state["connection"].print_insight1())


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

main()