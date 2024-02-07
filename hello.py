import streamlit as st
import pandas as pd
from itertools import combinations
import random
from datetime import datetime, timedelta



def start_of_week(date):
    return date - timedelta(days=date.weekday() + 1)  # Adjusted for week starting on Sunday


# Function to generate 1:1 meetings
def generate_meetings(people, group_meeting_interval, meetings_per_person, allow_meetings_during_group, repetition, num_intervals, start_date):
    if meetings_per_person > group_meeting_interval:
        raise ValueError("Meetings per person must be less than or equal to the group session interval.")
    if meetings_per_person < 1:
        raise ValueError("Meetings per person must be at least 1.")
    
    all_pairings = list(combinations(people, 2))
    schedule = {}
    current_start_date = start_of_week(start_date)  # Find the start of the week for the given start date
    
    for interval in range(1, num_intervals + 1):
        interval_schedule = []
        if not allow_meetings_during_group:
            week_of = current_start_date.strftime("Week of %b %d, %Y")
            interval_schedule.append((week_of, "--GROUP SESSION--"))
        
        used_pairs = set()
        available_weeks = list(range(2, group_meeting_interval + 1)) if not allow_meetings_during_group else list(range(1, group_meeting_interval + 1))
        
        # Determine the number of meetings to schedule each week to spread them evenly
        total_meetings = meetings_per_person * len(people) // 2
        meetings_per_week = max(1, total_meetings // len(available_weeks))
        
        for week in available_weeks:
            week_meetings_scheduled = 0
            week_of = (current_start_date + timedelta(weeks=week-1)).strftime("Week of %b %d, %Y")
            while week_meetings_scheduled < meetings_per_week and len(used_pairs) < len(all_pairings):
                if repetition:
                    pair = random.choice(all_pairings)
                else:
                    possible_pairs = [pair for pair in all_pairings if pair not in used_pairs]
                    if not possible_pairs:
                        break
                    pair = random.choice(possible_pairs)
                    used_pairs.add(pair)
                
                interval_schedule.append((week_of, f"{pair[0]} & {pair[1]} meet"))
                week_meetings_scheduled += 1
                
                if len(used_pairs) >= total_meetings:
                    break
        
        schedule[f"Interval {interval}"] = interval_schedule
        current_start_date += timedelta(weeks=group_meeting_interval)  # Move to the next interval start date
    
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
st.markdown("### Po7 Matchmaking Meeting Tool")

st.markdown("Create a custom schedule of 1:1 meetings for Po7 groups. The goal is ensure everyone meets with everyone else while distributing meetings evenly in a way that takes into account people's preferences for meeting frequency. App uses a round robin format, enabling every person to meet individually with everyone else (at least once) in the most efficient manner.")

# Input fields
with st.form("input_form"):
    people_input = st.text_input("List members' names or initials separated by commas (up to 9 people)", "DW, TL, GN, AC, MH, SW")
    group_meeting_date = st.date_input("Select the start date for the first group meeting", datetime.today())
    group_meeting_interval = st.slider("Frequency of Group sessions (example: group meets every 8 weeks)", min_value=1, max_value=12, value=8, step=1)
    meetings_per_person = st.slider("Maximum number of 1:1 meetings per person between group sessions. (Note: In order to meet with everyone at least once, set this to the number of other members)", value=7, min_value=1, max_value=group_meeting_interval-1)
    num_intervals = 2
    repetition = st.toggle("Allow multiple 1:1 meetings between the same individuals between group sessions", value=False)
    allow_meetings_during_group = st.toggle("Allow 1:1 meetings on the week of a group session", value=False)
    submitted = st.form_submit_button("Generate a 1:1 meeting schedule", type="primary")
    

if submitted:
    people = [p.strip() for p in people_input.split(",") if p.strip()]
    if len(people) > 9:
        st.error("Please enter up to 9 people.")
    else:
        try:
            # Call generate_meetings to create the schedule
            schedule = generate_meetings(people, group_meeting_interval, meetings_per_person, allow_meetings_during_group, repetition, num_intervals, group_meeting_date)
            
            # Convert the generated schedule to a DataFrame
            df_schedule = schedule_to_dataframe(schedule)
            columns_to_display = [col for col in df_schedule.columns if col != "Interval"]
            display_df = df_schedule[columns_to_display]
            st.subheader("Meeting Schedule:")
            st.dataframe(display_df, hide_index=True)
            
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

