import os
os.environ["MPLBACKEND"] = "Agg"
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import streamlit as st
import numpy as np

def run_biased_timer_simulation(prob_list, num_samples=10000, max_weeks=200):
    """
    Simulate the discrete-time process with directional bias.
    
    Each pause has a base frequency (interpreted as the chance to occur in a week) from prob_list.
    In each week, unoccurred pauses are attempted in order:
      - The leftmost unoccurred pause has no penalty.
      - The next gets a 10% penalty, then 20%, and so on.
      - If a pause’s penalty reaches 100%, it cannot occur that week.
    The simulation runs until all pauses have occurred or max_weeks is reached.
    """
    n = len(prob_list)
    all_T = np.zeros(num_samples, dtype=int)
    
    for trial in range(num_samples):
        occurred = [False] * n
        week = 0
        while week < max_weeks:
            week += 1
            # Identify which pauses haven't occurred yet.
            unoccurred_indices = [i for i, occ in enumerate(occurred) if not occ]
            if not unoccurred_indices:
                break
            # Process each unoccurred pause in left-to-right order.
            for rank, pause_index in enumerate(unoccurred_indices):
                penalty_fraction = 0.1 * rank  # 0% for first, 10% for second, etc.
                if penalty_fraction >= 1.0:
                    continue  # 100% penalty; cannot occur this week.
                base_freq = prob_list[pause_index]
                effective_freq = base_freq * (1.0 - penalty_fraction)
                # Bernoulli trial: if random number is below effective frequency, mark as occurred.
                if np.random.rand() < effective_freq:
                    occurred[pause_index] = True
            if all(occurred):
                break
        all_T[trial] = week
    
    return all_T

def main():
    st.title("Biological Timer Simulation")
    st.write("Specify the number of pauses and adjust each pause's weekly mutation frequency (0.01 to 0.21).")
    
    # Number of pauses input.
    n = st.number_input("Number of pauses:", min_value=1, max_value=20, value=5, step=1)
    
    st.write("Set the base weekly mutation frequency for each pause:")
    prob_list = []
    for i in range(1, int(n) + 1):
        p = st.slider(f"Pause {i} Frequency:", min_value=0.01, max_value=0.21, value=0.1, step=0.01)
        prob_list.append(p)
    
    # Number of Cells input.
    num_samples = st.number_input("Number of Cells:", min_value=1000, max_value=100000, value=10000, step=1000)
    max_weeks = st.number_input("Max weeks to simulate:", min_value=50, max_value=1000, value=200, step=50)
    
    if st.button("Run Simulation"):
        all_T = run_biased_timer_simulation(prob_list, num_samples, max_weeks)
        
        # Calculate percentiles.
        week_25 = int(np.percentile(all_T, 25))
        week_50 = int(np.percentile(all_T, 50))
        week_75 = int(np.percentile(all_T, 75))
        
        # Display statistics.
        st.write(f"25% Activation by Week {week_25}")
        st.write(f"50% Activation by Week {week_50}")
        st.write(f"75% Activation by Week {week_75}")
        
        # Create histogram.
        fig, ax = plt.subplots(figsize=(8, 4))
        bins = range(1, np.max(all_T) + 2)
        ax.hist(all_T, bins=bins, density=True, alpha=0.6, align='left', rwidth=0.8)
        ax.set_xlabel("Weeks")
        ax.set_ylabel("Probability")
        # Set the plot title to "Weekly Activation Count"
        ax.set_title("Weekly Activation Count")
        
        # Highlight the 50% activation week with a red dashed vertical line.
        ax.axvline(x=week_50, color='red', linestyle='dashed', linewidth=2, label="50% Activation")
        ax.legend()
        
        st.pyplot(fig)

if __name__ == "__main__":
    main()
