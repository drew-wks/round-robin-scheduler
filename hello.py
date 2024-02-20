import streamlit as st
import pandas as pd
from itertools import combinations
import random
from datetime import datetime, timedelta



def start_of_week(date):
    '''Calculate the start date of the week for a given date, assuming the week starts on Sunday.'''

    return date - timedelta(days=date.weekday() + 1)  

def calculate_available_weeks(group_session_frequency, allow_meetings_on_group_weeks):
    """
    Calculate the available weeks for scheduling meetings

    Parameters:
    - group_session_frequency (int): The frequency of group sessions.
    - allow_meetings_on_group_weeks (bool): Flag indicating if meetings can be scheduled on group session weeks.

    Returns:
    - list: A list of integers representing the available weeks for scheduling meetings.
    """
    if allow_meetings_on_group_weeks:
        return list(range(1, group_session_frequency + 1))
    else:
        return list(range(2, group_session_frequency + 1))


def start_of_week(date):
    '''Calculate the start date of the week for a given date, assuming the week starts on Sunday.'''
    return date - timedelta(days=date.weekday() + 1)



def create_schedule(people, group_session_frequency, max_meetings_pp_pw, allow_meetings_on_group_weeks, repetition):
    """
    Creates a schedule for 1:1 meetings between participants over a specified interval.

    This function generates a schedule that ensures each participant meets with every other participant,
    adhering to the specified maximum number of meetings per person per week. It accounts for whether
    meetings can be scheduled during the week of a group session.

    Parameters:
    - people (list): A list of strings representing the names of the participants.
    - group_session_frequency (int): The frequency of group sessions, indicating the number of weeks
      between each group session.
    - max_meetings_pp_pw (int): The maximum number of 1:1 meetings each person can have per week.
    - allow_meetings_on_group_weeks (bool): Flag indicating if 1:1 meetings can be scheduled during
      the week of a group session.
    - repetition (bool): Flag indicating if participants can have multiple meetings with the same person
      before having met everyone else.

    Returns:
    - dict: A dictionary where each key is an integer representing a week number within the interval,
      and each value is a list of strings describing the meetings scheduled for that week.

    Example (meetings not allowed during group week (week 1)):

    {
        2: ['A & B meet', 'C & D meet'],
        3: ['A & C meet', 'B & D meet'],
        4: ['A & D meet', 'B & C meet']
    }

    Example (meetings allowed during group week):

    {
        1: ['A & B meet'],
        2: ['C & D meet'],
        3: ['A & C meet'],
        4: ['B & D meet']
    }
    """
    if max_meetings_pp_pw > group_session_frequency:
        st.error("Meetings per person must be less than or equal to the group session interval.")
    if max_meetings_pp_pw < 1:
        st.error("Meetings per person must be at least 1.")
    
    all_pairings = list(combinations(people, 2))
    
    if allow_meetings_on_group_weeks:
        available_weeks = list(range(1, group_session_frequency + 1))
    else:
        available_weeks = list(range(2, group_session_frequency + 1))
    
    schedule = {week: [] for week in available_weeks}
    
    used_pairs = set()
    total_meetings = max_meetings_pp_pw * len(people) // 2
    meetings_per_week = max(1, total_meetings // len(available_weeks))
    
    for week in available_weeks:
        week_meetings_scheduled = 0
        while week_meetings_scheduled < meetings_per_week and len(used_pairs) < len(all_pairings):
            if repetition:
                pair = random.choice(all_pairings)
            else:
                possible_pairs = [pair for pair in all_pairings if pair not in used_pairs]
                if not possible_pairs:
                    break
                pair = random.choice(possible_pairs)
                used_pairs.add(pair)
            
            schedule[week].append(f"{pair[0]} & {pair[1]} meet")
            week_meetings_scheduled += 1
            
            if len(used_pairs) >= total_meetings:
                break
    return schedule
    


def schedule_to_df(schedule, allow_meetings_on_group_weeks):
    data = []
    
    for week, meetings in schedule.items():
        for meeting in meetings:
            data.append({'Week': week, 'Meeting': meeting})
            
    df = pd.DataFrame(data)
    df.sort_values(by='Week', inplace=True)
    group_session_row = pd.DataFrame({'Week': 1, 'Meeting': "--GROUP SESSION--"}, index=[0])
    df.index = df.index + 1  # Shift the index to make space for the new row at the beginning
    df = pd.concat([group_session_row, df], ignore_index=True)
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
            schedule = create_schedule(people, group_session_frequency, max_meeting_pp_pw, allow_meetings_on_group_weeks, repetition, num_intervals, group_meeting_date)
            
            # Convert the generated schedule to a DataFrame with additional columns for each person
            df_schedule = schedule_to_df(schedule, people)
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

