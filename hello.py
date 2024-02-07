import streamlit as st
import pandas as pd
from itertools import combinations
import random


# Function to generate 1:1 meetings
def generate_meetings(people, group_meeting_interval, meetings_per_person, allow_meetings_during_group, repetition, num_intervals):
    if meetings_per_person > group_meeting_interval:
        raise ValueError("Meetings per person must be less than or equal to the group session interval.")
    if meetings_per_person < 1:
        raise ValueError("Meetings per person must be at least 1.")
    
    all_pairings = list(combinations(people, 2))
    schedule = {}
    
    for interval in range(1, num_intervals + 1):
        interval_schedule = []
        if not allow_meetings_during_group:
            interval_schedule.append(("Week 1", "Group Session"))
        
        used_pairs = set()
        available_weeks = list(range(2, group_meeting_interval + 1)) if not allow_meetings_during_group else list(range(1, group_meeting_interval + 1))
        
        # Determine the number of meetings to schedule each week to spread them evenly
        total_meetings = meetings_per_person * len(people) // 2
        meetings_per_week = max(1, total_meetings // len(available_weeks))
        
        for week in available_weeks:
            week_meetings_scheduled = 0
            while week_meetings_scheduled < meetings_per_week and len(used_pairs) < len(all_pairings):
                if repetition:
                    pair = random.choice(all_pairings)
                else:
                    possible_pairs = [pair for pair in all_pairings if pair not in used_pairs]
                    if not possible_pairs:  # If no more unique pairings are available, break
                        break
                    pair = random.choice(possible_pairs)
                    used_pairs.add(pair)
                
                interval_schedule.append((f"Week {week}", f"{pair[0]} & {pair[1]} meet"))
                week_meetings_scheduled += 1
                
                # Check if we've scheduled enough meetings for this interval
                if len(used_pairs) >= total_meetings:
                    break
        
        schedule[f"Interval {interval}"] = interval_schedule
    
    return schedule


def schedule_to_dataframe(schedule):
    # Flatten the schedule to a list of dicts for easy conversion to DataFrame
    data = []
    for interval, meetings in schedule.items():
        for week, meeting in meetings:
            data.append({"Interval": interval, "Week": week, "Meeting": meeting})
    return pd.DataFrame(data)

# Function to convert schedule to CSV and allow download
def convert_df_to_csv(df):
    return df.to_csv().encode('utf-8')



# Streamlit app
col1, col2, col3 = st.columns([3,3,2])
with col1:
    st.write('   ')
with col2:
    st.image("https://images.squarespace-cdn.com/content/v1/611645b4405ecc34f75902d4/1630940958363-48IAK69A1MB56BOGE5I7/P07+Secondary+Logo.png?format=2500w", width = 100)
with col3:
    st.write('   ')
st.markdown("### Po7 1:1 Round Robin Meeting Scheduler")

st.markdown("Creates a custom 1:1 meeting schedule in between group sessions. The goal is ensure everyone meets with everyone else while distributing meetings evenly in a way that takes into account people's preferences for meeting frequency. App uses a round robin format, enabling each person to meet with each other in the most efficient manner.")

# Input fields
with st.form("input_form"):
    people_input = st.text_input("List members' names or initials separated by commas (up to 9 people)", "DW, TL, GN, AC, MH, SW")
    group_meeting_interval = st.slider("Frequency of Group sessions (example: group meets every 8 weeks)", min_value=1, max_value=12, value=8, step=1)
    meetings_per_person = st.slider("Number of 1:1 meetings to schedule for each person between group sessions", value=3, min_value=1, max_value=group_meeting_interval-1)
    num_intervals = 2
    allow_meetings_during_group = st.toggle("Allow 1:1 meetings during week of a group session", value=False)
    repetition = st.toggle("Allow multiple 1:1 meetings between the same individuals between group sessions", value=False)
    submitted = st.form_submit_button("Generate a 1:1 meeting schedule", type="primary")
    

if submitted:
    people = [p.strip() for p in people_input.split(",") if p.strip()]
    if len(people) > 9:
        st.error("Please enter up to 9 people.")
    else:
        try:
            # Call generate_meetings to create the schedule
            schedule = generate_meetings(people, group_meeting_interval, meetings_per_person, allow_meetings_during_group, repetition, num_intervals)
            
            # Convert the generated schedule to a DataFrame
            df_schedule = schedule_to_dataframe(schedule)
            st.subheader("Schedule:")
            st.dataframe(df_schedule, hide_index=True)
            
            # Download button
            csv = convert_df_to_csv(df_schedule)
            st.download_button(
                label="Download Meeting Schedule as CSV",
                data=csv,
                file_name='meeting_schedule.csv',
                mime='text/csv',
            )
        except ValueError as e:
            st.error(e)

