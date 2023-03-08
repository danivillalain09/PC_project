import streamlit as st
import mysql.connector


# Define the login page
def login_page():
    st.title("Welcome to the login page!")
    st.write("Please enter your credentials below to log in.")

    # Add input fields for username and password
    input_password = st.text_input("Password for mysql connection:", type="password")

    # Add a checkbox to input a new database name
    new_database_name = st.checkbox("Create a new database (default: project)")
    # If the box is checked, add an input field to input the new database name
    if new_database_name:
        database_name = st.text_input("New database name:")
    else:
        database_name = "project"

    # Add a submit button
    submit_button = st.button("Log in")

    # Check if the username and password are correct when the submit button is pressed
    if submit_button:
        # Try to connect to the database
        try:
            cnx = mysql.connector.connect(password=input_password, host="127.0.0.1", database=database_name)
            cnx.close()
            connection_failed = False

        except mysql.connector.errors.ProgrammingError:
            connection_failed = True

        if not connection_failed:
            # st.success("Logged in!")
            # Set the logged_in state to True after a successful login
            st.session_state["page_view"] = 2
            st.experimental_rerun()
        else:
            st.error("Incorrect sql password or database name. Please try again.")

    return input_password, database_name


# Define the main content of the app
def insights_page():
    st.title("Boat Port Simulation Results")
    st.image("/Users/danivillalain/Desktop/Projects_github/Pictures/port_picture.jpeg", use_column_width=True)
    st.markdown("---")

    # Sidebar for input parameters
    st.sidebar.title("Input Parameters")
    num_boats = st.sidebar.number_input("Number of boats:", min_value=1, max_value=100, value=10, step=1)
    num_ports = st.sidebar.number_input("Number of ports:", min_value=1, max_value=10, value=2, step=1)
    num_cranes = st.sidebar.number_input("Number of cranes:", min_value=1, max_value=7, value=1, step=1)
    num_transporters = st.sidebar.number_input("Number of transporters:", min_value=1, max_value=7, value=1, step=1)

    st.sidebar.submit_button = st.button("Submit input parameters")

    if st.sidebar.submit_button:
        st.session_state["page_view"] = 3
        st.experimental_rerun()


def result_page():
    st.write("This is the result page")


# Run the app
if __name__ == "__main__":
    # Initialize the logged_in state to False if it hasn't been created yet
    st.session_state.setdefault("page_view", 1)
    password = ""
    database = ""

    # Check if the user is logged in
    if st.session_state["page_view"] == 1:
        password, database = login_page()
        print(password, database)
    elif st.session_state["page_view"] == 2:
        insights_page()
    elif st.session_state["page_view"] == 3:
        result_page()