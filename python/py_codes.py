import sqlite3
import pandas as pd

conn = sqlite3.connect('inspection.db')

requests = pd.read_sql("SELECT * FROM Requests", conn)
stage1 = pd.read_sql("SELECT * FROM InspectionStage1", conn)
stage2 = pd.read_sql("SELECT * FROM InspectionStage2", conn)

conn.close()

# Convert date columns to actual datetime objects
requests['Date'] = pd.to_datetime(requests['Date'])
stage1['StartDate'] = pd.to_datetime(stage1['StartDate'])
stage1['EndDate'] = pd.to_datetime(stage1['EndDate'])
stage2['StartDate'] = pd.to_datetime(stage2['StartDate'])
stage2['EndDate'] = pd.to_datetime(stage2['EndDate'])

print("Requests:", requests.shape)
print("Stage1:", stage1.shape)
print("Stage2:", stage2.shape)
print(requests.head())
print(stage1.head())
print(stage2.head())

# --- Join Requests with Stage1 (left join, since not every request has a stage1 row) ---
df = requests.merge(
    stage1,
    left_on='RequestID',
    right_on='RequestID',
    how='left',
    suffixes=('_Req', '_S1')
)

# --- Join in Stage2 (left join on InspectionID) ---
df = df.merge(
    stage2,
    left_on='InspectionID',
    right_on='InspectionID',
    how='left',
    suffixes=('', '_S2')
)

# --- Rename columns for clarity after the merges ---
df = df.rename(columns={
    'Status_Req': 'RequestStatus',
    'Status_S1': 'Stage1Status',
    'Status': 'Stage2Status',
    'StartDate': 'Stage1StartDate',
    'EndDate': 'Stage1EndDate',
    'StartDate_S2': 'Stage2StartDate',
    'EndDate_S2': 'Stage2EndDate',
    'InspectedBy': 'Stage1InspectedBy',      # was mislabeled as Stage2 before
    'InspectedBy_S2': 'Stage2InspectedBy',   # was left unrenamed before
    'Remarks': 'Stage1Remarks',              # was mislabeled as Stage2 before
    'Remarks_S2': 'Stage2Remarks'            # was left unrenamed before
})

# --- Compute durations (in days) ---
df['Stage1Duration'] = (df['Stage1EndDate'] - df['Stage1StartDate']).dt.days
df['Stage2Duration'] = (df['Stage2EndDate'] - df['Stage2StartDate']).dt.days

# --- Total turnaround: request date to final closure date ---
# Final closure = Stage2EndDate if it exists, else Stage1EndDate
df['FinalCloseDate'] = df['Stage2EndDate'].combine_first(df['Stage1EndDate'])
df['TotalTurnaroundDays'] = (df['FinalCloseDate'] - df['Date']).dt.days

print(df.shape)
print(df[['RequestID', 'RequestStatus', 'Stage1Status', 'Stage2Status',
          'Stage1Duration', 'Stage2Duration', 'TotalTurnaroundDays']].head(10))

print(df.columns.tolist())
print(df[['Stage1Duration', 'Stage2Duration', 'TotalTurnaroundDays']].describe())

# First-pass yield: % of requests that passed Stage1 and never needed Stage2
closed = df[df['Stage1Status'].notna()]  # only requests that actually got inspected
first_pass = closed[
    (closed['Stage1Status'] == 'Pass') & (closed['Stage2Required'] == 'No')
]
first_pass_yield = len(first_pass) / len(closed) * 100
print(f"First-pass yield: {first_pass_yield:.1f}%")
print(df.describe())

# --- Average turnaround time by Cell ---
turnaround_by_cell = (
    df[df['TotalTurnaroundDays'].notna()]
    .groupby('Cell')['TotalTurnaroundDays']
    .agg(['mean', 'count'])
    .rename(columns={'mean': 'AvgTurnaroundDays', 'count': 'ClosedRequests'})
    .sort_values('AvgTurnaroundDays', ascending=False)
)
print(turnaround_by_cell)

# --- Inspector workload (Stage1) ---
inspector_workload = (
    df[df['Stage1InspectedBy'].notna()]
    .groupby('Stage1InspectedBy')
    .agg(
        InspectionsHandled=('InspectionID', 'count'),
        AvgStage1Duration=('Stage1Duration', 'mean'),
        FailRate=('Stage1Status', lambda x: (x == 'Fail').mean() * 100)
    )
    .sort_values('InspectionsHandled', ascending=False)
)
print(inspector_workload)

# --- Recurring defect patterns: which RequestCategory fails most often ---
defect_patterns = (
    df[df['Stage1Status'].notna()]
    .groupby('RequestCategory')
    .agg(
        TotalInspected=('InspectionID', 'count'),
        Failures=('Stage1Status', lambda x: (x == 'Fail').sum())
    )
)
defect_patterns['FailRate%'] = (defect_patterns['Failures'] / defect_patterns['TotalInspected'] * 100).round(1)
defect_patterns = defect_patterns.sort_values('FailRate%', ascending=False)
print(defect_patterns)

# --- Requester vs inspector Stage2 mismatch rate ---
mismatch = df[df['Stage1Status'].notna()].copy()
mismatch['Match'] = mismatch['Stage2FlagRequested'] == mismatch['Stage2Required']
mismatch_rate = (~mismatch['Match']).mean() * 100
print(f"\nRequester/Inspector Stage2 mismatch rate: {mismatch_rate:.1f}%")

# Breakdown of mismatch direction
print(pd.crosstab(mismatch['Stage2FlagRequested'], mismatch['Stage2Required'],
                   rownames=['Requester Flagged'], colnames=['Inspector Confirmed']))

priority_mismatch = df[df['Stage1Status'].notna()].groupby('Priority').apply(
    lambda g: (g['Stage2FlagRequested'] != g['Stage2Required']).mean() * 100
)
print(priority_mismatch)

flag_rate_by_priority = df[df['Stage1Status'].notna()].groupby('Priority')['Stage2FlagRequested'].apply(
    lambda x: (x == 'Yes').mean() * 100
)
print(flag_rate_by_priority)

import os

output_dir = r'C:\Users\z0050910\Inspection_Workflow\powerbi\powerbi_exports'
os.makedirs(output_dir, exist_ok=True)

# --- 1. Main joined table — Power BI's primary data source ---
df.to_csv(f'{output_dir}/inspection_master.csv', index=False)

# --- 2. Turnaround time by cell ---
turnaround_by_cell.to_csv(f'{output_dir}/turnaround_by_cell.csv')

# --- 3. Inspector workload ---
inspector_workload.to_csv(f'{output_dir}/inspector_workload.csv')

# --- 4. Recurring defect patterns ---
defect_patterns.to_csv(f'{output_dir}/defect_patterns.csv')

# --- 5. Priority vs Stage2 mismatch summary ---
priority_summary = pd.DataFrame({
    'FlagRate_RequesterSaidYes%': flag_rate_by_priority,
    'MismatchRate%': priority_mismatch
})
priority_summary.to_csv(f'{output_dir}/priority_stage2_summary.csv')

# --- 6. Single-value KPIs (first-pass yield etc.) as a small reference table ---
kpi_summary = pd.DataFrame({
    'Metric': ['First-Pass Yield %', 'Overall Stage2 Mismatch Rate %'],
    'Value': [round(first_pass_yield, 1), round(mismatch_rate, 1)]
})
kpi_summary.to_csv(f'{output_dir}/kpi_summary.csv', index=False)

print(f"Exported 6 files to {output_dir}/")
print(os.listdir(output_dir))