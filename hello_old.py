import streamlit as st
import pandas as pd
from itertools import combinations
import random
from datetime import datetime, timedelta



def start_of_week(date):
    '''Calculate the start date of the week for a given date, assuming the week starts on Sunday.'''

    return date - timedelta(days=date.weekday() + 1)  


# Function to generate 1:1 meetings
def generate_meetings(people, group_session_frequency, max_meetings_pp_pw, allow_meetings_on_group_weeks, repetition, num_intervals, start_date):
    if max_meetings_pp_pw > group_session_frequency:
        st.error("Meetings per person must be less than or equal to the group session interval.")
    if max_meetings_pp_pw < 1:
        st.error("Meetings per person must be at least 1.")
    
    all_pairings = list(combinations(people, 2))
    schedule = {}
    current_start_date = start_of_week(start_date)  # Find the start of the week for the given start date
    
    for interval in range(1, num_intervals + 1):
        interval_schedule = []
        if not allow_meetings_on_group_weeks:
            week_of = current_start_date.strftime("%b %d, %Y")
            interval_schedule.append((week_of, "--GROUP SESSION--"))
        
        used_pairs = set()
        available_weeks = list(range(2, group_session_frequency + 1)) if not allow_meetings_on_group_weeks else list(range(1, group_session_frequency + 1))
        
        # Determine the number of meetings to schedule each week to spread them evenly
        total_meetings = max_meetings_pp_pw * len(people) // 2
        meetings_per_week = max(1, total_meetings // len(available_weeks))
        
        for week in available_weeks:
            week_meetings_scheduled = 0
            week_of = (current_start_date + timedelta(weeks=week-1)).strftime("%b %d, %Y")
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
        current_start_date += timedelta(weeks=group_session_frequency)  # Move to the next interval start date
    
    return schedule


def schedule_to_dataframe(schedule, people):
    # Initialize the DataFrame with additional columns for each person
    columns = ["Week of", "Meeting"] + people
    data = []
    
    for interval, meetings in schedule.items():
        for week, meeting in meetings:
            row = {"Week of": week, "Meeting": meeting}
            # Initialize person columns with empty strings or zeros
            for person in people:
                row[person] = ""  # or 0 if you prefer numeric indicators
            # Check if the meeting involves specific people and mark accordingly
            if "meet" in meeting:
                participants = meeting.replace(" meet", "").split(" & ")
                for participant in participants:
                    if participant in people:  # Ensure participant is in the people list
                        row[participant] = "X"  # or 1 for numeric indicators
            data.append(row)
    
    df = pd.DataFrame(data, columns=columns)
    
    # Optionally, add a totals row at the bottom
    totals = {"Week of": "Total", "Meeting": ""}
    for person in people:
        totals[person] = df[person].apply(lambda x: 1 if x == "X" else 0).sum()
    
    # Use pd.concat to append the totals row
    totals_df = pd.DataFrame([totals])  # Convert totals to a DataFrame
    df = pd.concat([df, totals_df], ignore_index=True)
    
    return df



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
st.markdown("### Po7 Meeting Matchmaking Tool")

st.markdown("Create a custom schedule of 1:1 meetings for Po7 groups. The goal is ensure everyone meets with everyone else while distributing meetings evenly in a way that takes into account people's preferences for meeting frequency. App uses a round robin format, enabling every person to meet individually with everyone else (at least once) in the most efficient manner.")

# Input fields
with st.form("input_form"):
    people_input = st.text_input("List members' names or initials separated by commas (up to 9 people)", "DW, TL, GN, AC, MH, SW")
    group_meeting_date = st.date_input("Select the start date for the first group meeting", datetime.today())
    group_session_frequency = st.slider("Frequency of Group sessions (example: group meets every 8 weeks)", min_value=1, max_value=12, value=8, step=1)
    max_meetings_pp_pw = st.slider("Maximum number of 1:1 meetings per person between group sessions. (Note: In order to meet with everyone at least once, set this to the number of other members)", value=7, min_value=1, max_value=group_session_frequency-1)
    num_intervals = 2
    repetition = st.toggle("Allow multiple 1:1 meetings between the same individuals between group sessions", value=False)
    allow_meetings_on_group_weeks = st.toggle("Allow 1:1 meetings on the week of a group session", value=False)
    submitted = st.form_submit_button("Generate a 1:1 meeting schedule", type="primary")
    

if submitted:
    people = [p.strip() for p in people_input.split(",") if p.strip()]
    if len(people) > 9:
        st.error("Please enter up to 9 people.")
    else:
        try:
            schedule = generate_meetings(people, group_session_frequency, max_meeting_pp_pw, allow_meetings_on_group_weeks, repetition, num_intervals, group_meeting_date)
            
            # Convert the generated schedule to a DataFrame with additional columns for each person
            df_schedule = schedule_to_dataframe(schedule, people)
            st.subheader("Meeting Schedule:")
            st.dataframe(df_schedule, hide_index=True, height=500)
            
            csv = convert_df_to_csv(df_schedule)
            st.download_button(
                label="Download Meeting Schedule",
                data=csv,
                file_name='Po7_meeting_schedule.csv',
                mime='text/csv',
            )
        except ValueError as e:
            st.error(e)

