import streamlit as st
import pandas as pd
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
col1, col2, col3 = st.columns(3)
with col1:
    st.write(' ')
with col2:
    st.image("https://images.squarespace-cdn.com/content/v1/611645b4405ecc34f75902d4/1630940958363-48IAK69A1MB56BOGE5I7/P07+Secondary+Logo.png?format=2500w", width = 100)
with col3:
    st.write(' ')

st.title("Po7 1:1 Round Robin Meeting Scheduler")
st.markdown("Creates a custom 1:1 meeting schedule in between group meetings. App uses a round robin format, enabling each person to meet with each other in the most efficient manner")

# Input fields
with st.form("input_form"):
    people_input = st.text_input("List members' names separated by commas (up to 9 people)", "DW, TL, GN, AC, MH, SW")
    group_meeting_interval = st.slider("Group meeting interval (example: group meets every 8 weeks)", min_value=1, max_value=12, value=8, step=1)
    meetings_per_person = st.slider("Number of 1:1 meetings to schedule for each person between group meetings", value=3, min_value=1, max_value=group_meeting_interval-1)
    num_intervals = 2
    allow_meetings_during_group = st.toggle("Allow 1:1 meetings during weeks the group meets", value=False)
    repetition = st.toggle("Allow repeated pairings during an interval", value=False)
    submitted = st.form_submit_button("Generate a 1:1 Meeeting schedule", type="primary")
    

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
            st.dataframe(df_schedule)
            
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

