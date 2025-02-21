import streamlit as st
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

def run_biased_timer_simulation(prob_list, num_samples=10000, max_weeks=200):
    """
    Simulate the discrete-time process with directional bias.
    
    Each event i has a base probability from prob_list.
    In each week, unoccurred events are attempted in order:
      - The leftmost unoccurred event has no penalty.
      - The next gets a 10% penalty, then 20%, and so on.
      - If an event’s penalty reaches 100%, it cannot occur that week.
    The simulation runs until all events have occurred or max_weeks is reached.
    """
    n = len(prob_list)
    all_T = np.zeros(num_samples, dtype=int)
    
    for trial in range(num_samples):
        occurred = [False] * n
        week = 0
        while week < max_weeks:
            week += 1
            
            # List of indices for events that haven't occurred yet.
            unoccurred_indices = [i for i, occ in enumerate(occurred) if not occ]
            if not unoccurred_indices:
                break
            
            # Process each unoccurred event in left-to-right order.
            for rank, event_index in enumerate(unoccurred_indices):
                # Apply a penalty: 0% for the first event, 10% for the second, etc.
                penalty_fraction = 0.1 * rank
                if penalty_fraction >= 1.0:
                    continue  # 100% penalty; cannot occur this week.
                
                base_p = prob_list[event_index]
                effective_p = base_p * (1.0 - penalty_fraction)
                
                # Bernoulli trial for the event.
                if np.random.rand() < effective_p:
                    occurred[event_index] = True
            
            if all(occurred):
                break
        
        all_T[trial] = week
    
    return all_T


def main():
    st.title("Biological Timer Simulation with Directional Bias")
    st.write("Specify the number of events and adjust each event's base weekly probability (0.01 to 0.21).")

    # User input: Number of events.
    n = st.number_input("Number of events:", min_value=1, max_value=20, value=5, step=1)
    
    st.write("Set the base weekly probability for each event:")
    prob_list = []
    # Create a slider for each event.
    for i in range(1, int(n) + 1):
        p = st.slider(f"Event {i} probability:", min_value=0.01, max_value=0.21, value=0.1, step=0.01)
        prob_list.append(p)
    
    # Additional simulation parameters.
    num_samples = st.number_input("Number of simulation trials:", min_value=1000, max_value=100000, value=10000, step=1000)
    max_weeks = st.number_input("Max weeks to simulate:", min_value=50, max_value=1000, value=200, step=50)

    # Run the simulation when the button is clicked.
    if st.button("Run Simulation"):
        all_T = run_biased_timer_simulation(prob_list, num_samples, max_weeks)
        
        # Create a histogram of the activation times.
        fig, ax = plt.subplots(figsize=(8, 4))
        bins = range(1, np.max(all_T) + 2)
        ax.hist(all_T, bins=bins, density=True, alpha=0.6, align='left', rwidth=0.8)
        ax.set_xlabel("Weeks")
        ax.set_ylabel("Probability")
        ax.set_title("Time Until All Events Occur with Directional Bias")
        st.pyplot(fig)
        
if __name__ == "__main__":
    main()
