import streamlit as st
from itertools import combinations
import random

# Function to generate meetings
def generate_meetings(people, group_meeting_interval, available_weeks, meetings_per_person, no_repetition, num_intervals):
    if available_weeks > group_meeting_interval or meetings_per_person > group_meeting_interval:
        raise ValueError("Available weeks and meetings per person must be less than or equal to the group meeting interval.")
    if meetings_per_person < 1:
        raise ValueError("Meetings per person must be at least 1.")
    
    all_pairings = list(combinations(people, 2))
    total_meetings_needed = meetings_per_person * len(people) // 2
    if no_repetition and total_meetings_needed > len(all_pairings):
        raise ValueError("The requirement for no repetition cannot be met with the given parameters.")
    
    schedule = {}
    
    for interval in range(1, num_intervals + 1):
        interval_schedule = [("Week 0", "Group Meeting")]
        used_pairs = set()
        possible_weeks = list(range(2, available_weeks + 2))
        
        while possible_weeks and len(interval_schedule) - 1 < total_meetings_needed:
            week = random.choice(possible_weeks)
            possible_weeks.remove(week)
            possible_pairs = [pair for pair in all_pairings if pair not in used_pairs]
            if not possible_pairs:
                break
            pair = random.choice(possible_pairs)
            used_pairs.add(pair)
            interval_schedule.append((f"Week {week}", f"{pair[0]} & {pair[1]}"))
        
        schedule[f"Interval {interval}"] = interval_schedule
    
    return schedule

# Streamlit app
st.title("Po7 Round Robin Meeting Schedule")

# Input fields
with st.form("input_form"):
    people_input = st.text_input("Enter names of people separated by commas (up to 7 people)", "DW, TL, GN, AC, MH, SW")
    group_meeting_interval = st.number_input("Group Meeting Interval (weeks)", value=8, min_value=1)
    available_weeks = st.number_input("Available Weeks for Meetings", value=6, min_value=1, max_value=group_meeting_interval)
    meetings_per_person = st.number_input("Meetings per Person in Each Interval", value=3, min_value=1, max_value=group_meeting_interval)
    no_repetition = st.checkbox("No Repetition of Pairings", value=True)
    num_intervals = st.number_input("Number of Intervals to Project", value=2, min_value=1)
    submitted = st.form_submit_button("Generate Schedule")

if submitted:
    people = [p.strip() for p in people_input.split(",") if p.strip()]
    if len(people) > 7:
        st.error("Please enter up to 7 people.")
    else:
        try:
            schedule = generate_meetings(people, group_meeting_interval, available_weeks, meetings_per_person, no_repetition, num_intervals)
            st.subheader("Schedule:")
            for interval, meetings in schedule.items():
                st.markdown(f"**{interval}:**")
                for week, meeting in meetings:
                    st.write(f"{week}: {meeting}")
        except ValueError as e:
            st.error(e)
