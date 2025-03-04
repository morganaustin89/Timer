import os
os.environ["MPLBACKEND"] = "Agg"
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import streamlit as st
import numpy as np
import math

def run_biased_timer_simulation(prob_list, num_samples=10000, max_weeks=200):
    """
    Simulate the discrete-time process with daily resolution.
    
    Each pause has a base weekly mutation frequency (input between 0.01 and 0.21).
    We convert that to a daily probability using:
        daily_prob = 1 - (1 - weekly_prob)^(1/7)
    Then, each day, unoccurred pauses are attempted in order:
      - The leftmost unoccurred pause gets no penalty.
      - The next gets a 10% penalty, then 20%, etc.
      - If a pause’s penalty reaches 100%, it cannot occur that day.
    The simulation runs day‐by‐day until all pauses have occurred or until max_weeks*7 days.
    The output is the number of weeks (rounded up) at which activation occurs.
    """
    n = len(prob_list)
    all_time_weeks = np.zeros(num_samples, dtype=int)
    max_days = max_weeks * 7

    for trial in range(num_samples):
        occurred = [False] * n
        day = 0
        while day < max_days:
            day += 1
            # List of indices for pauses that haven't occurred yet.
            unoccurred_indices = [i for i, occ in enumerate(occurred) if not occ]
            if not unoccurred_indices:
                break
            # Process each unoccurred pause in left-to-right order.
            for rank, pause_index in enumerate(unoccurred_indices):
                penalty_fraction = 0.1 * rank  # 0% for first, 10% for second, etc.
                if penalty_fraction >= 1.0:
                    continue  # 100% penalty; cannot occur this day.
                base_weekly = prob_list[pause_index]
                # Convert weekly frequency to daily probability:
                base_daily = 1 - (1 - base_weekly)**(1/7)
                effective_daily = base_daily * (1 - penalty_fraction)
                if np.random.rand() < effective_daily:
                    occurred[pause_index] = True
            if all(occurred):
                break
        # Convert days to weeks (rounding up)
        weeks = math.ceil(day / 7)
        all_time_weeks[trial] = weeks
    return all_time_weeks

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
        all_time_weeks = run_biased_timer_simulation(prob_list, num_samples, max_weeks)
        
        # Calculate the week numbers for 25%, 50%, and 75% activation.
        week_25 = int(np.percentile(all_time_weeks, 25))
        week_50 = int(np.percentile(all_time_weeks, 50))
        week_75 = int(np.percentile(all_time_weeks, 75))
        
        st.write(f"25% Activation by Week {week_25}")
        st.write(f"50% Activation by Week {week_50}")
        st.write(f"75% Activation by Week {week_75}")
        
        # Create a histogram.
        fig, ax = plt.subplots(figsize=(8, 4))
        bins = range(1, np.max(all_time_weeks) + 2)
        ax.hist(all_time_weeks, bins=bins, density=True, alpha=0.6, align='left', rwidth=0.8)
        ax.set_xlabel("Weeks")
        ax.set_ylabel("Probability")
        ax.set_title("Weekly Activation Count")
        
        # Add a vertical red dashed line at the 50% activation week.
        ax.axvline(x=week_50, color='red', linestyle='dashed', linewidth=2, label="50% Activation")
        ax.legend()
        
        st.pyplot(fig)
    
    # -------------------------------
    # Video/Image Section (at the very bottom)
    # -------------------------------
    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("ErosionPicture.png", use_container_width=True)
    with col2:
        st.markdown("### Fuse Burn Demo")
        st.write("Scroll down to see the Fuse Burn Demo video below.")

    try:
        with open("Fuse_Burn_Demo2.mp4", "rb") as video_file:
            video_bytes = video_file.read()
        st.video(video_bytes)
    except Exception as e:
        st.error(f"Error loading video: {e}")

if __name__ == "__main__":
    main()
