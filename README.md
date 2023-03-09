# Boat Port Simulation 
Welcome to the Boat Port Simulation project! 

## Explanation 
The Operating Systems and Parallel Computing project aimed to simulate a real-life situation and provide insights into the performance of the simulation. 
To achieve this goal, several techniques and assumptions were employed.

Firstly, a mediator design pattern was utilized to simulate a real-life case. 
This design pattern ensured that the control station had permission to manage the other instances in the simulation. 
Additionally, the simulation consisted of different independent agents that worked in parallel. 
These agents included boats, the control station, and workers. 
Furthermore, transporters and cranes were controlled by the workers, making them dependent on the workers.
To track the movements of each agent in the simulation, the control station recorded their activities in a database.
This database was used to generate reports at the end of the simulation.

The simulation's performance was analyzed by creating a Streamlit webpage that provided instant insights and personalized the simulation for various cases*.

## How to run the simulation 
To run the simulation the following steps have to be followed: 
1. Clone the repository.
2. Install the requirements using the command `pip install`.
    Here is a lis of all the libraries to install:
   - Streamlit 
   - Matplotlib 
   - Colorama 
   - Mysql-connector-python
   - Faker 
   - plotly.express 
   - Time 
   - Concurrent.futures 
   - Datetime 
   - Copy
3. Run the file streamlit_app.py using the command `streamlit run streamlit_app.py`.
4. The simulation will start and the webpage will open in your browser.
5. Then, follow the guidelines on the streamlit. 
6. The simulation will run and the results will be displayed on the webpage.