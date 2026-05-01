import pandas as pd
import random
from datetime import datetime, timedelta

# --- Configuration & Master Data ---
schools = [
    'School of Engineering', 
    'School of Law, Governance & Public Policy', 
    'School of Mathematics & Natural Sciences', 
    'School of Biosciences', 
    'School of Arts, Humanities & Social Sciences'
]
eng_branches = ['CSE', 'CSAI', 'ECE', 'VLSI', 'Mechanical and Aerospace', 'civil', 'Biotechnology']
venues = ['Auditorium', 'Main Ground', 'Block A - Seminar Hall', 'CS Lab 1', 'Sports Complex']

# --- 1. Schools & Branches ---
sb_data = []
# Add Schools (parent_id is None)
for i, school in enumerate(schools, 1):
    sb_data.append({'sb_id': i, 'name': school, 'parent_id': None, 'is_school': True})

# Add Engineering Branches (parent_id is 1 - School of Engineering)
for i, branch in enumerate(eng_branches, len(schools) + 1):
    sb_data.append({'sb_id': i, 'name': branch, 'parent_id': 1, 'is_school': False})

df_sb = pd.DataFrame(sb_data)

# --- 2. Venues ---
venue_data = [{'venue_id': i, 'venue_name': v, 'building_block': 'Block ' + v[0]} for i, v in enumerate(venues, 1)]
df_venues = pd.DataFrame(venue_data)

# --- 3 & 4. Main Events and Sub-Events ---
main_events = [
    {'id': 1, 'title': 'Tech Fest', 'org': 1, 'type': 'technical'},
    {'id': 2, 'title': 'Cultural Fest', 'org': None, 'type': 'cultural'}, # University-wide
    {'id': 3, 'title': 'Sports Day', 'org': None, 'type': 'sports'},
    {'id': 4, 'title': 'AI Workshop', 'org': 1, 'type': 'workshop'}
]

sub_event_map = {
    'Tech Fest': ['Hackathon', 'Web Development', 'Prompt to Product', 'Circuit Verse', 'RoboRush'],
    'Cultural Fest': ['IKS Online Hackathon', 'Treasure Hunt', 'Vastra Verse', 'Hardware Hackathon', 'Esports'],
    'Sports Day': ['Football', 'Throwball', 'Cricket', 'Table Tennis', 'Volleyball'],
    'AI Workshop': ['Hands-on Neural Networks']
}

me_list = []
se_list = []
se_id_counter = 1

for me in main_events:
    # Main Event Table 
    me_list.append({
        'main_event_id': me['id'],
        'title': me['title'],
        'organizing_school_id': me['org'],
        'start_date': '2026-03-10',
        'end_date': '2026-03-12'
    })
    
    # Sub Events Table [cite: 17, 20]
    for sub_name in sub_event_map[me['title']]:
        is_comp = False if me['type'] == 'workshop' else True
        se_list.append({
            'sub_event_id': se_id_counter,
            'main_event_id': me['id'],
            'sub_event_name': sub_name,
            'category': me['type'],
            'venue_id': random.choice(df_venues['venue_id']),
            'event_time': '2026-03-11 10:00:00',
            'organizing_school_id': me['org'],
            'is_competition': is_comp,
            'description': f'Exciting {sub_name} session.'
        })
        se_id_counter += 1

df_main_events = pd.DataFrame(me_list)
df_sub_events = pd.DataFrame(se_list)

# --- 5. Participants ---
participant_list = []
for i in range(1, 101): # 100 students [cite: 18]
    participant_list.append({
        'participant_id': i,
        'roll_number': f'2026BT{i:03d}',
        'full_name': f'Student {i}',
        'sb_id': random.choice(df_sb['sb_id']),
        'year_of_study': random.randint(1, 4),
        'is_internal': True
    })
df_participants = pd.DataFrame(participant_list)

# --- 6. Event Registrations ---
reg_list = []
reg_id = 1
for _, student in df_participants.iterrows():
    # Each student registers for 2 random sub-events [cite: 27]
    for se_id in random.sample(list(df_sub_events['sub_event_id']), 2):
        reg_list.append({
            'registration_id': reg_id,
            'sub_event_id': se_id,
            'participant_id': student['participant_id'],
            'registration_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        reg_id += 1
df_registrations = pd.DataFrame(reg_list)

# --- 7. Competition Results ---
results_list = []
res_id = 1
# Only for competitive events [cite: 19, 21]
comp_sub_events = df_sub_events[df_sub_events['is_competition'] == True]['sub_event_id']

for se_id in comp_sub_events:
    # Get students who registered for this event
    pot_winners = df_registrations[df_registrations['sub_event_id'] == se_id]['participant_id'].tolist()
    if pot_winners:
        winners = random.sample(pot_winners, min(len(pot_winners), 3))
        for rank, p_id in enumerate(winners, 1):
            results_list.append({
                'result_id': res_id,
                'sub_event_id': se_id,
                'participant_id': p_id,
                'rank_position': rank,
                'award_prize': f'Prize {rank}'
            })
            res_id += 1
df_results = pd.DataFrame(results_list)

# --- Save to CSV ---
df_sb.to_csv('schools_branches.csv', index=False)
df_venues.to_csv('venues.csv', index=False)
df_main_events.to_csv('main_events.csv', index=False)
df_sub_events.to_csv('sub_events.csv', index=False)
df_participants.to_csv('participants.csv', index=False)
df_registrations.to_csv('event_registrations.csv', index=False)
df_results.to_csv('competition_results.csv', index=False)

print("All CSV files generated successfully for each table.")