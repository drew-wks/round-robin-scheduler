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




    """
    Creates a schedule for 1:1 meetings between participants over a specified interval.

    This function generates a schedule that ensures each participant meets with every other participant, adhering to the specified maximum number of meetings per person per week. It accounts for whether meetings can be scheduled during the week of a group session.

    Parameters:
    - people (list): A list of strings representing the names of the participants.
    - group_session_frequency (int): The frequency of group sessions, indicating the number of weeks between each group session.
    - max_meetings_pp_pw (int): The maximum number of 1:1 meetings each person can have per week.
    - allow_meetings_on_group_weeks (bool): Flag indicating if 1:1 meetings can be scheduled during the week of a group session.
    - repetition (bool): Flag indicating if participants can have multiple meetings with the same person before having met everyone else.

    Returns:
    - dict: A dictionary where each key is an integer representing a week number within the interval, and each value is a list of strings describing the meetings scheduled for that week.

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


def create_schedule(people, group_session_frequency, max_meetings_pp_pw, allow_meetings_on_group_weeks, repetition):
    all_pairings = list(combinations(people, 2))
    schedule = {}
    # Initialize a counter for each person's weekly meetings
    weekly_meetings_counter = {week: {person: 0 for person in people} for week in range(1, group_session_frequency + 1)}

    available_weeks = calculate_available_weeks(group_session_frequency, allow_meetings_on_group_weeks)

    for week in available_weeks:
        schedule[week] = []
        possible_meetings = [pair for pair in all_pairings if weekly_meetings_counter[week][pair[0]] < max_meetings_pp_pw and weekly_meetings_counter[week][pair[1]] < max_meetings_pp_pw]

        while possible_meetings:
            if repetition:
                # Allow selecting any pair if repetition is allowed
                pair = random.choice(possible_meetings)
            else:
                # Prefer pairs that have not met yet if no repetition
                pair = possible_meetings.pop(0)

            schedule[week].append(f"{pair[0]} & {pair[1]} meet")
            # Update the weekly meetings counter for both participants
            weekly_meetings_counter[week][pair[0]] += 1
            weekly_meetings_counter[week][pair[1]] += 1

            # Update possible_meetings based on the new counter
            possible_meetings = [pair for pair in possible_meetings if weekly_meetings_counter[week][pair[0]] < max_meetings_pp_pw and weekly_meetings_counter[week][pair[1]] < max_meetings_pp_pw]

    return schedule



def add_dates_to_schedule(schedule, group_meeting_date):
    """
    Enriches the schedule with the start date of each week.

    Example output
    full_schedule = {
        1: {
            'week_of': datetime.datetime(2024, 3, 4),
            'meetings': ['A & B meet', 'C & D meet']
        },
        2: {
            'week_of': datetime.datetime(2024, 3, 11),
            'meetings': ['A & C meet', 'B & D meet']
        },
        3: {
            'week_of': datetime.datetime(2024, 3, 18),
            'meetings': ['A & D meet', 'B & C meet']
        }
    }
    """
    full_schedule = {}
    start_date = group_meeting_date - timedelta(days=group_meeting_date.weekday() + 1)
    if 1 in schedule:    # Prepend "Group Session" to the list of meetings for week 1
        schedule[1].insert(0, 'GROUP SESSION')
    else: # If no meetings in week 1, create an entry for the "Group Meeting"
        schedule[1] = ['GROUP SESSION']
    for week_num, meetings in schedule.items():
        week_of = start_date + timedelta(weeks=week_num - 1)
        full_schedule[week_num] = {
            'week_of': week_of,
            'meetings': meetings
        }
    return full_schedule



def schedule_to_df(full_schedule, people):
    # Initialize the DataFrame columns with 'Week of', 'Meeting', and one for each participant
    columns = ['Week of', 'Meeting'] + people
    data = []
    
    # Iterate through each week in the full schedule
    for week_num, info in full_schedule.items():
        week_of = info['week_of']  # Keep as datetime for sorting
        
        # Iterate through each meeting in the week
        for meeting in info['meetings']:
            # Start with a row template that includes the week and meeting details
            row = {'Week of': week_of, 'Meeting': meeting}
            
            # Initialize participant columns with empty strings
            for person in people:
                row[person] = ''
            
            # Check if the meeting involves specific people and mark accordingly
            participants = meeting.split(' & ')
            for participant in participants:
                # Remove potential trailing identifiers like " meet"
                participant_name = participant.replace(" meet", "").strip()
                if participant_name in people:
                    row[participant_name] = 'X'  # Mark participation
            
            data.append(row)
    
    # Create the DataFrame from the compiled data
    df = pd.DataFrame(data, columns=columns)
    
    if not df.empty:
        # Sort the DataFrame by 'Week of'
        df.sort_values(by='Week of', inplace=True)
        
        # Convert 'Week of' to a more readable string format
        df['Week of'] = df['Week of'].apply(lambda x: x.strftime('%b %d, %Y'))
    
    return df




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
st.markdown("### Po7 Meeting Tool")

st.markdown("Create a custom schedule of 1:1 meetings for Po7 groups. The goal is ensure everyone meets with everyone else while distributing meetings evenly in a way that takes into account people's preferences for meeting frequency. App uses a round robin format, enabling every person to meet individually with everyone else (at least once) in the most efficient manner.")

# Input fields
with st.form("input_form"):
    people_input = st.text_input("List members' names or initials separated by commas (up to 9 people)", "DW, TL, GN, AC, MH, SW")
    group_meeting_date = st.date_input("Select the start date for the first group meeting", datetime.today())
    group_session_frequency = st.slider("Frequency of Group sessions (example: group meets every 8 weeks)", min_value=1, max_value=12, value=8, step=1)
    max_meetings_pp_pw = st.number_input("Maximum number of 1:1 meetings per person per week.", value=1.0, min_value=0.5, max_value=2.0, step=0.5)
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
            schedule = create_schedule(people, group_session_frequency, max_meetings_pp_pw, allow_meetings_on_group_weeks, repetition)
            full_schedule = add_dates_to_schedule(schedule, group_meeting_date)
            df_schedule = schedule_to_df(full_schedule, people)  # Adjusted call
            if not df_schedule.empty:
                st.subheader("Meeting Schedule:")
                row_height = 35
                extra_height = 38  # Extra space for header and padding
                dataframe_height = row_height * len(df_schedule) + extra_height
                st.dataframe(df_schedule, hide_index=True, height=dataframe_height, use_container_width=True)
                
                csv = convert_df_to_csv(df_schedule)
                st.download_button(
                    label="Download Meeting Schedule",
                    data=csv,
                    file_name='Po7_meeting_schedule.csv',
                    mime='text/csv',
                )
            else:
                st.error("The schedule DataFrame is empty.")
        except ValueError as e:
            st.error(e)


