import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)

# --- Reference values ---
cells = ['Assembly', 'Machining', 'Welding', 'Painting', 'Packaging', 'Testing']
machines = {c: [f"{c[:3].upper()}-{i:02d}" for i in range(1, 6)] for c in cells}
categories = ['Mechanical', 'Electrical', 'Safety', 'Quality', 'Preventive']
req_types = ['Breakdown', 'Scheduled', 'Complaint', 'Audit Finding',
             'Calibration', 'Upgrade', 'Warranty Check']
priorities = ['High', 'Medium', 'Low']
inspectors = ['Ravi Kumar', 'Sri Priya', 'Muhammed Anand', 'Vara Lakshmi',
              'Akhil Sharma', 'Narsiman Reddy', 'Kadar Iyer', 'Dev Mehta']
incharges = ['Akiran Suresh', 'Kamala Devi', 'Tugluq Raj', 'Nanda Bala',
             'Sri Varun', 'Pellakuru Nithya', 'Raj Aravind', 'Janani Meena']
machine_n = ['Motorola' , 'Nokia', 'Gleason', 'Dories','Pfauter','Doraemon','Ninja']

N_REQUESTS = 750
start_date = datetime(2025, 1, 1)
DATE_SPAN_DAYS = 600
reference_date = start_date + timedelta(days=DATE_SPAN_DAYS) 

def get_stage2_flag_requested(priority):
    if priority == 'High':
        return random.choices(['Yes', 'No'], weights=[0.65, 0.35])[0]
    elif priority == 'Medium':
        return random.choices(['Yes', 'No'], weights=[0.45, 0.55])[0]
    else:  # Low
        return random.choices(['Yes', 'No'], weights=[0.25, 0.75])[0]


def assign_status(req_date, reference_date):
    days_old = (reference_date - req_date).days

    if days_old <= 3:
        return random.choices(['Open', 'In Progress'], weights=[0.85, 0.15])[0]
    elif days_old <= 14:
        return random.choices(
            ['Open', 'In Progress', 'Completed', 'Hold', 'Rejected'],
            weights=[0.20, 0.35, 0.30, 0.10, 0.05]
        )[0]
    else:
        return random.choices(
            ['In Progress', 'Hold', 'Completed', 'Rejected'],
            weights=[0.05, 0.05, 0.75, 0.15]
        )[0]


requests, stage1_rows, stage2_rows = [], [], []
inspection_id_counter = 1
stage2_id_counter = 1

for i in range(1, N_REQUESTS + 1):
    cell = random.choice(cells)
    machine = random.choice(machines[cell])
    req_date = start_date + timedelta(days=random.randint(0, DATE_SPAN_DAYS))
    outcome = assign_status(req_date, reference_date)
    priority_choice = random.choice(priorities)

    requests.append({
        'RequestID': i,
        'Date': req_date.strftime('%Y-%m-%d'),
        'Cell': cell,
        'MachineNumber': machine,
        'MachineName': random.choice(machine_n),
        'RequestCategory': random.choice(categories),
        'RequestType': random.choice(req_types),
        'Priority': priority_choice,
        'MachineStatus': random.choice(['Idle', 'Working', 'Waiting']),
        'ReasonForInspection': random.choice([
            'Unusual noise', 'Vibration detected', 'Scheduled check',
            'Output defect reported', 'Safety guard issue']),
        'MachineIncharge': random.choice(incharges),
        'Stage2FlagRequested': get_stage2_flag_requested(priority_choice),
        'Status': outcome
    })

    if outcome in ('Open',):
        continue
    if outcome == 'In Progress' and random.random() < 0.4:
        # some "In Progress" requests haven't even started stage1 yet
        continue

    s1_start = req_date + timedelta(days=random.randint(0, 3))
    s1_end = s1_start + timedelta(days=random.randint(0, 2))
    this_inspection_id = inspection_id_counter
    inspection_id_counter += 1

    if outcome == 'In Progress':
        s1_status = random.choice(['Pass', 'Fail'])
        s1_stage2_required = 'Yes'

    elif outcome == 'Hold':
        s1_status = 'Fail'
        s1_stage2_required = 'No'

    elif outcome == 'Completed':
        needs_stage2 = random.random() < 0.3
        s1_stage2_required = 'Yes' if needs_stage2 else 'No'
        s1_status = random.choice(['Pass', 'Fail']) if needs_stage2 else 'Pass'

    elif outcome == 'Rejected':
        needs_stage2 = random.random() < 0.5
        s1_stage2_required = 'Yes' if needs_stage2 else 'No'
        s1_status = 'Fail'

    stage1_rows.append({
        'InspectionID': this_inspection_id,
        'RequestID': i,
        'StartDate': s1_start.strftime('%Y-%m-%d'),
        'EndDate': s1_end.strftime('%Y-%m-%d'),
        'Status': s1_status,
        'InspectedBy': random.choice(inspectors),
        'Remarks': random.choice(['OK after check', 'Minor issue fixed', 'Needs follow-up', 'Confirmed defect']),
        'Stage2Required': s1_stage2_required
    })

    if outcome in ('Completed', 'Rejected') and s1_stage2_required == 'Yes':
        s2_start = s1_end + timedelta(days=random.randint(1, 3))
        s2_end = s2_start + timedelta(days=random.randint(0, 2))
        stage2_rows.append({
            'Stage2ID': stage2_id_counter,
            'InspectionID': this_inspection_id,
            'StartDate': s2_start.strftime('%Y-%m-%d'),
            'EndDate': s2_end.strftime('%Y-%m-%d'),
            'Status': 'Pass' if outcome == 'Completed' else 'Fail',
            'InspectedBy': random.choice(inspectors),
            'Remarks': random.choice(['Root cause confirmed', 'Part replaced', 'Escalated to vendor'])
        })
        stage2_id_counter += 1

req_df = pd.DataFrame(requests)
stage1_df = pd.DataFrame(stage1_rows)
stage2_df = pd.DataFrame(stage2_rows)

conn = sqlite3.connect('inspection.db')
req_df.to_sql('Requests', conn, if_exists='append', index=False)
stage1_df.to_sql('InspectionStage1', conn, if_exists='append', index=False)
stage2_df.to_sql('InspectionStage2', conn, if_exists='append', index=False)
conn.close()

print(f"Loaded {len(req_df)} requests, {len(stage1_df)} stage1 inspections, {len(stage2_df)} stage2 inspections.")