import streamlit as st
from itertools import combinations
import random

# Function to generate 1:1 meetings
def generate_meetings(people, group_meeting_interval, meetings_per_person, allow_meetings_during_group, repetition, num_intervals):
    if meetings_per_person > group_meeting_interval:
        raise ValueError("Meetings per person must be less than or equal to the group meeting interval.")
    if meetings_per_person < 1:
        raise ValueError("Meetings per person must be at least 1.")
    
    all_pairings = list(combinations(people, 2))
    schedule = {}
    
    for interval in range(1, num_intervals + 1):
        interval_schedule = [("Week 0", "Group Meeting")]
        used_pairs = set()
        weeks_to_schedule = range(1, group_meeting_interval + 1) if allow_meetings_during_group else range(2, group_meeting_interval)
        
        for week in weeks_to_schedule:
            if len(interval_schedule) - 1 >= meetings_per_person * len(people) // 2:
                break  # Scheduled enough 1:1 meetings for this interval
            if repetition or not used_pairs:
                pair = random.choice(all_pairings)
            else:
                possible_pairs = [pair for pair in all_pairings if pair not in used_pairs]
                if not possible_pairs:
                    continue  # No more unique pairings available, skip to next week
                pair = random.choice(possible_pairs)
                used_pairs.add(pair)
            interval_schedule.append((f"Week {week}", f"{pair[0]} & {pair[1]} 1:1 Meeting"))
        
        schedule[f"Interval {interval}"] = interval_schedule
    
    return schedule

# Streamlit app
st.title("Po7 Round Robin Meeting Schedule")

# Input fields
with st.form("input_form"):
    people_input = st.text_input("Enter names of people separated by commas (up to 7 people)", "DW, TL, GN, AC, MH, SW")
    group_meeting_interval = st.slider("Group meeting interval (example: group meets every 8 weeks)", min_value=1, max_value=12, value=8, step=1)
    meetings_per_person = st.number_input("1:1 meetings per person per interval", value=3, min_value=1, max_value=group_meeting_interval-1)
    num_intervals = st.number_input("Number of intervals to schedule", value=2, min_value=1)
    allow_meetings_during_group = st.toggle("Allow 1:1 meetings during weeks the group meets", value=False)
    repetition = st.toggle("Allow repeated pairings during an interval", value=False)
    submitted = st.form_submit_button("Generate a 1:1 Meeeting schedule", type="primary")
    

if submitted:
    people = [p.strip() for p in people_input.split(",") if p.strip()]
    if len(people) > 7:
        st.error("Please enter up to 7 people.")
    else:
        try:
            schedule = generate_meetings(people, group_meeting_interval, meetings_per_person, allow_meetings_during_group, repetition, num_intervals)
            st.subheader("Schedule:")
            for interval, meetings in schedule.items():
                st.markdown(f"**{interval}:**")
                for week, meeting in meetings:
                    st.write(f"{week}: {meeting}")
        except ValueError as e:
            st.error(e)

