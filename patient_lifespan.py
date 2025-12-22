# ==========================================================
# Patient Survival Analysis with KM, RMST, Raw Lifespan and Segment Breakdowns
# ==========================================================

import pandas as pd
from lifelines import KaplanMeierFitter
from lifelines.utils import restricted_mean_survival_time
from datetime import datetime

# === 1. Load Data ===
df_patients = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\List of Patients.csv"
)
df_patients_lehigh = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\List of Patients Lehigh.csv"
)
df_patients_lehigh['Medicaid Number'] = df_patients_lehigh['Medicaid Number'].astype(str)

df_contracts = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Contract Lookup.csv"
)

# Visit reports
visit_labels = ["2023", "Jan_June", "May_Nov", "MidAug_MidMar",
                "MidNov_MidJune", "MidFeb25_MidSep", "MidApr25_MidNov"]
dfs = [
          pd.read_csv(
              f"C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_{label}.csv"
          )
          for label in visit_labels
      ] + [
          pd.read_csv(
              "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_Lehigh.csv",
              dtype={'MedicaidNo': 'S10'}
          )
      ]

# === 2. Combine & Clean Visits ===
dfs[-1]['MedicaidNo'] = dfs[-1]['MedicaidNo'].astype(str)
dfs[-1]['ContractName'] = ['PA'] * len(dfs[-1])

visits_df = pd.concat(dfs, ignore_index=True)
visits_df = visits_df.drop_duplicates(subset=['VisitID'])
visits_df = visits_df[(visits_df['MissedVisit'] == 'No') & (visits_df['Billed'] == 'Yes')].copy()
visits_df['VisitDate'] = pd.to_datetime(visits_df['VisitDate'], errors='coerce')

# Clean patient name and admission ID
split_df = visits_df['PatientName'].str.split('(', expand=True)
visits_df['PatientName'] = split_df[0].str.strip()
visits_df['AdmissionID'] = split_df[1].str.replace(')', '') if split_df.shape[1] > 1 else None

# Add office and basic info
df_patients['Office'] = df_patients['Admission ID - Office'].str[:3]
df_patients_lehigh['Office'] = 'OHZ'
df_patients_lehigh['County'] = 'PA'
df_patients_lehigh['Gender'] = 'Unknown'

# Merge visits with contract and patient info
visits_df = visits_df.merge(df_contracts, on='ContractName', how='left')
visits_df['ContractType'] = visits_df['ContractType'].fillna('Unknown')

visits_df = visits_df.merge(df_patients, left_on='AdmissionID', right_on='Admission ID - Office', how='left')
visits_df = visits_df.merge(
    df_patients_lehigh, left_on='MedicaidNo', right_on='Medicaid Number', how='left',
    suffixes=('', '_lehigh')
)

# Normalize County names (case-insensitive, remove whitespace)
visits_df['County'] = visits_df['County'].str.strip().str.title()
visits_df['County_lehigh'] = visits_df['County_lehigh'].str.strip().str.title()

# Merge combined demographic fields
visits_df['Date of Birth'] = pd.to_datetime(
    visits_df['DOB'].combine_first(visits_df['Date of Birth']),
    errors='coerce'
)
visits_df['MedicaidNo'] = (
    visits_df['MedicaidNo'].replace(r'\\.0$', '', regex=True).str.lstrip('0')
)
visits_df['Office'] = visits_df['Office'].combine_first(visits_df['Office_lehigh'])
visits_df['County'] = visits_df['County'].combine_first(visits_df['County_lehigh'])
visits_df['County'] = visits_df['County'].str.strip().str.title()
visits_df['Gender'] = visits_df['Gender'].combine_first(visits_df['Gender_lehigh'])

# Create a unique patient ID
visits_df['UniqueID'] = visits_df.apply(
    lambda row: (
        row['MedicaidNo']
        if pd.notna(row['MedicaidNo']) and row['MedicaidNo'] != 0 and row['ContractType'] not in ['CHHA', 'Private Pay']
        else f"{row['PatientName']}_{row['Date of Birth']}"
    ),
    axis=1
)

# === 3. Identify Episodes (Handle Return Patients) ===

# Sort by patient and date
visits_df = visits_df.sort_values(['UniqueID', 'VisitDate']).copy()

# Calculate days since last visit per patient
visits_df['DaysSinceLast'] = visits_df.groupby('UniqueID')['VisitDate'].diff().dt.days

# Define a gap threshold for new episodes (90 days is typical)
gap_threshold = 90

# Mark new episodes
visits_df['NewEpisodeFlag'] = (visits_df['DaysSinceLast'] > gap_threshold) | (visits_df['DaysSinceLast'].isna())

# Assign Episode IDs
visits_df['EpisodeID'] = visits_df.groupby('UniqueID')['NewEpisodeFlag'].cumsum()

# Create a combined unique episode key
visits_df['UniqueEpisodeID'] = visits_df['UniqueID'].astype(str) + "_E" + visits_df['EpisodeID'].astype(str)

# === 4. Patient-Level Aggregation by Episode ===
patients = visits_df.groupby(['UniqueEpisodeID', 'UniqueID', 'Status']).agg(
    FirstVisitDate=('VisitDate', 'min'),
    LastVisitDate=('VisitDate', 'max')
).reset_index()

# Determine active/inactive episodes
patients['IsActive'] = patients['Status'] == 'Active'
today = pd.to_datetime("today")

patients['EndDate'] = patients['LastVisitDate']
patients.loc[patients['IsActive'], 'EndDate'] = today
patients['DurationDays'] = (patients['EndDate'] - patients['FirstVisitDate']).dt.days
patients['event'] = (~patients['IsActive']).astype(int)

# Add temporal fields
patients['StartQuarter'] = patients['FirstVisitDate'].dt.to_period('Q').astype(str)
patients['StartYear'] = patients['FirstVisitDate'].dt.year

# Attach demographics
contracts_sorted = visits_df.sort_values(by=['UniqueEpisodeID', 'VisitDate'])
first = contracts_sorted.groupby('UniqueEpisodeID').first().reset_index()
last = contracts_sorted.groupby('UniqueEpisodeID').last().reset_index()

patients = patients.merge(
    first[['UniqueEpisodeID', 'ContractType', 'Office', 'County', 'Gender', 'Date of Birth', 'Branch', 'Team']],
    on='UniqueEpisodeID', how='left')
patients = patients.rename(columns={'ContractType': 'StartContractType', 'Office': 'StartOffice'})

# === Calculate Age at Admission ===
patients['AgeAtStart'] = (
        (patients['FirstVisitDate'] - pd.to_datetime(patients['Date of Birth'], errors='coerce')).dt.days / 365.25
)
# Define age bins and labels
bins = [0, 3, 20, 40, 60, 80, float('inf')]
labels = ['0-3', '3-20', '20-40', '40-60', '60-80', '80+']

# Categorize age groups (handle missing)
patients['AgeBracket'] = pd.cut(
    patients['AgeAtStart'],
    bins=bins,
    labels=labels,
    right=False
)
patients['AgeBracket'] = patients['AgeBracket'].cat.add_categories(['Unknown']).fillna('Unknown')

patients = patients.merge(last[['UniqueEpisodeID', 'ContractType', 'Office']],
                          on='UniqueEpisodeID', how='left')
patients = patients.rename(columns={'ContractType': 'EndContractType', 'Office': 'EndOffice'})

# === 5. Setup Kaplan-Meier ===
folder_path = "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Lifetime Expectancy\\"
benchmarks = [30, 60, 90, 180, 365, 730]
kmf = KaplanMeierFitter()
patients.to_csv(folder_path + "lifespan_summary_new.csv", index=False)

# === 6. Calculate t for RMST ===
kmf.fit(patients['DurationDays'], patients['event'])
max_uncensored = patients.loc[patients["event"] == 1, "DurationDays"].max()
quantile_cutoff = patients["DurationDays"].quantile(0.95)
t = int(min(max_uncensored, quantile_cutoff, 1095))


# === 7. Helper Functions ===
def clean_keys(d):
    """Replace None with empty strings."""
    return {k: ('' if v is None else v) for k, v in d.items()}


def parse_segment_label(label):
    keys = {
        'StartYear': None, 'StartQuarter': None, 'StartOffice': None, 'EndOffice': None,
        'StartContract': None, 'EndContract': None, 'County': None, 'Gender': None, 'Age': None,
        'SegmentType': label
    }
    if label == 'Overall':
        return clean_keys(keys)

    parts = label.split('_')
    i = 0
    while i < len(parts):
        if parts[i] in keys:
            key = parts[i]
            i += 1
            if i < len(parts):
                keys[key] = parts[i]
        i += 1
    return clean_keys(keys)


def export_survival_benchmarks(group_df, segment_info):
    results = []
    if len(group_df) < 5:
        return results
    kmf.fit(group_df['DurationDays'], group_df['event'])
    max_duration = group_df['DurationDays'].max()
    for day in benchmarks:
        km_val = float(kmf.predict(day)) if day <= max_duration else 0
        raw_val = (group_df['DurationDays'] >= day).sum() / len(group_df)
        results.append(
            {**segment_info, "Day": day, "Method": "KM_Predict", "SurvivalRate": km_val, "CohortSize": len(group_df)})
        results.append(
            {**segment_info, "Day": day, "Method": "Raw", "SurvivalRate": raw_val, "CohortSize": len(group_df)})
    return results


def export_rmst(group_df, segment_info, t):
    if len(group_df) < 5:
        return []
    kmf.fit(group_df['DurationDays'], group_df['event'])
    rmst = restricted_mean_survival_time(kmf, t)
    raw_mean = group_df["DurationDays"].mean()
    raw_median = group_df["DurationDays"].median()
    try:
        km_median = kmf.median_survival_time_
    except Exception:
        km_median = float('nan')
    return [{
        **segment_info,
        "RestrictedMeanSurvivalTime": rmst,
        "RawAverageLifespan": raw_mean,
        "RawMedianLifespan": raw_median,
        "KMMedianSurvivalTime": km_median,
        "CohortSize": len(group_df)
    }]


def generate_survival_curves(group_df, label):
    if len(group_df) < 5:
        return pd.DataFrame()
    kmf.fit(group_df['DurationDays'], group_df['event'])
    timeline = kmf.survival_function_.reset_index()
    timeline.columns = ['Day', 'SurvivalProbability_KM']
    raw_df = pd.DataFrame({'Day': range(0, int(group_df['DurationDays'].max()) + 1)})
    raw_df['SurvivalProbability_Raw'] = raw_df['Day'].apply(
        lambda d: (group_df['DurationDays'] >= d).sum() / len(group_df)
    )
    merged = pd.merge(timeline, raw_df, on='Day', how='outer').sort_values(by='Day')
    merged['Segment'] = label
    return merged


# === 8. Define Segments (Full Set) ===
segments = [
    ('Overall', patients),
    *[(f"StartYear_{y}", g) for y, g in patients.groupby('StartYear')],
    *[(f"StartQuarter_{q}", g) for q, g in patients.groupby('StartQuarter')],
    *[(f"StartContract_{c}", g) for c, g in patients.groupby('StartContractType')],
    *[(f"EndContract_{c}", g) for c, g in patients.groupby('EndContractType')],
    *[(f"StartOffice_{o}", g) for o, g in patients.groupby('StartOffice')],
    *[(f"EndOffice_{o}", g) for o, g in patients.groupby('EndOffice')],
    *[(f"StartYear_{y}_StartContract_{c}", g) for (y, c), g in patients.groupby(['StartYear', 'StartContractType'])],
    *[(f"StartYear_{y}_EndContract_{c}", g) for (y, c), g in patients.groupby(['StartYear', 'EndContractType'])],
    *[(f"StartYear_{y}_StartOffice_{o}", g) for (y, o), g in patients.groupby(['StartYear', 'StartOffice'])],
    *[(f"StartYear_{y}_EndOffice_{o}", g) for (y, o), g in patients.groupby(['StartYear', 'EndOffice'])],
    # *[(f"StartQuarter_{q}_StartContract_{c}", g) for (q, c), g in
    #   patients.groupby(['StartQuarter', 'StartContractType'])],
    # *[(f"StartQuarter_{q}_EndContract_{c}", g) for (q, c), g in patients.groupby(['StartQuarter', 'EndContractType'])],
    # *[(f"StartQuarter_{q}_StartOffice_{o}", g) for (q, o), g in patients.groupby(['StartQuarter', 'StartOffice'])],
    # *[(f"StartQuarter_{q}_EndOffice_{o}", g) for (q, o), g in patients.groupby(['StartQuarter', 'EndOffice'])],
    *[(f"County_{c}", g) for c, g in patients.groupby('County')],
    *[(f"StartYear_{y}_County_{c}", g) for (y, c), g in patients.groupby(['StartYear', 'County'])],
    # *[(f"StartQuarter_{q}_County_{c}", g) for (q, c), g in patients.groupby(['StartQuarter', 'County'])],
    *[(f"Gender_{gdr}", g) for gdr, g in patients.groupby('Gender')],
    *[(f"StartYear_{y}_Gender_{gdr}", g) for (y, gdr), g in patients.groupby(['StartYear', 'Gender'])],
    # *[(f"StartQuarter_{q}_Gender_{gdr}", g) for (q, gdr), g in patients.groupby(['StartQuarter', 'Gender'])],
    *[(f"Age_{a}", g) for a, g in patients.groupby('AgeBracket')],
    *[(f"StartYear_{y}_Age_{a}", g) for (y, a), g in patients.groupby(['StartYear', 'AgeBracket'])],
    # *[(f"StartQuarter_{q}_Age_{a}", g) for (q, a), g in patients.groupby(['StartQuarter', 'AgeBracket'])],
]

# === 9. Run Analysis ===
records, rmst_records, curve_records = [], [], []
for label, group in segments:
    segment_info = parse_segment_label(label)
    records.extend(export_survival_benchmarks(group, segment_info))
    rmst_records.extend(export_rmst(group, segment_info, t))
    curves = generate_survival_curves(group, label)
    if not curves.empty:
        curves = curves.assign(**segment_info)
        curve_records.append(curves)

pd.DataFrame(records).to_csv(folder_path + "survival_benchmarks_all_segments.csv", index=False)
pd.DataFrame(rmst_records).to_csv(folder_path + "average_stats_by_segment.csv", index=False)
if curve_records:
    pd.concat(curve_records).to_csv(folder_path + "survival_curves_by_segment.csv", index=False)

# === 10. Predictive Survival Model (AFT) ===
import numpy as np
from lifelines import WeibullAFTFitter, LogNormalAFTFitter, LogLogisticAFTFitter

# 10.1 Prepare data for modeling (keep ONLY the needed covariates)
model_df = patients.copy()

# Basic hygiene
model_df = model_df[model_df['DurationDays'].notna() & model_df['event'].notna()].copy()
model_df = model_df[model_df['DurationDays'] > 0].copy()

# Make sure covariates exist and are usable
# Fill missing AgeAtStart with median; normalize text cats
model_df['AgeAtStart'] = model_df['AgeAtStart'].fillna(model_df['AgeAtStart'].median())

# (optional) normalize gender/contract spelling to avoid sparse/duplicate levels
model_df['Gender'] = model_df['Gender'].fillna('Unknown').astype(str).str.strip().str.title()
model_df['StartContractType'] = model_df['StartContractType'].fillna('Unknown').astype(str).str.strip()

# Build a minimal modeling frame
mod_min = model_df[['DurationDays', 'event', 'AgeAtStart', 'Gender', 'StartContractType']].copy()
mod_min = pd.get_dummies(mod_min, columns=['Gender', 'StartContractType'], drop_first=True)

# Must have both event classes
if mod_min['event'].nunique() < 2:
    raise RuntimeError("AFT needs both censored (0) and event (1) rows; currently found only one class.")

# Drop any constant columns (can happen for rare dummies)
const_cols = [c for c in mod_min.columns if c not in ['DurationDays', 'event'] and mod_min[c].nunique() <= 1]
if const_cols:
    mod_min = mod_min.drop(columns=const_cols)

# Keep only numeric columns
numeric_cols = mod_min.select_dtypes(include=[np.number]).columns.tolist()
mod_min = mod_min[numeric_cols]

duration_col = 'DurationDays'
event_col = 'event'
feature_cols = [c for c in mod_min.columns if c not in (duration_col, event_col)]

# 10.2 Fit candidate AFT models and select best by AIC
candidates = [
    ('Weibull', WeibullAFTFitter()),
    ('LogNormal', LogNormalAFTFitter()),
    ('LogLogistic', LogLogisticAFTFitter()),
]

fits = []
for name, model in candidates:
    try:
        # Fit on the minimal, numeric-only frame
        model.fit(mod_min[[duration_col, event_col] + feature_cols],
                  duration_col=duration_col, event_col=event_col)
        fits.append((name, model, model.AIC_))
    except Exception as e:
        print(f"{name} failed: {e}")

if not fits:
    raise RuntimeError("No AFT model could be fit. After restricting to numeric features, "
                       "there may still be data or collinearity issues. Check printed errors above.")

best_name, best_model, best_aic = sorted(fits, key=lambda x: x[2])[0]
print(f"Selected AFT: {best_name} (AIC={best_aic:.1f})")

# 10.3 Helper to build a design row aligned to the model's training columns
model_feature_cols = feature_cols  # freeze training-time feature order


def _make_design_row(age, gender, contract):
    """
    Create a 1-row DataFrame with the exact dummy columns used in training.
    Unknown categories are left at 0.0 (i.e., reference level).
    """
    base = {col: 0.0 for col in model_feature_cols}
    # continuous
    if 'AgeAtStart' in base:
        base['AgeAtStart'] = float(age)

    # dummies (set to 1 if that dummy existed at training time)
    gcol = f'Gender_{str(gender).strip().title()}'
    ccol = f'StartContractType_{str(contract).strip()}'
    if gcol in base:
        base[gcol] = 1.0
    if ccol in base:
        base[ccol] = 1.0

    return pd.DataFrame([base], columns=model_feature_cols)


# 10.4 Predict survival probability at a specific day
def predict_survival(age, gender, contract, day):
    """
    Returns S(day | age, gender, contract) using the selected AFT model.
    If a category level wasn't present at training, it's treated as the reference (all 0 dummies).
    """
    X = _make_design_row(age, gender, contract)
    sf = best_model.predict_survival_function(X, times=np.array([float(day)], dtype=float))
    return float(sf.iloc[0, 0])


# 10.5 Example: your query
prob_day39 = predict_survival(age=33, gender='Male', contract='MLTC', day=39)
print(f"Predicted survival probability at day 39 (33yo Male MLTC): {prob_day39:.3f}")

# 10.6 (Optional) Export a prediction grid for Power BI
benchmarks = [30, 39, 60, 90, 180, 365, 730]
genders = sorted(model_df['Gender'].dropna().unique().tolist())
contracts = sorted(model_df['StartContractType'].dropna().unique().tolist())

age_points = [2, 10, 30, 50, 70, 90]  # midpoints for your brackets
pred_records = []
for a in age_points:
    for g in genders:
        for c in contracts:
            X = _make_design_row(a, g, c)
            sf = best_model.predict_survival_function(X, times=np.array(benchmarks, dtype=float))
            for t_idx, day in enumerate(benchmarks):
                pred_records.append({
                    'Age': a,
                    'Gender': g,
                    'StartContractType': c,
                    'Day': day,
                    'PredictedSurvival_AFT': float(sf.iloc[t_idx, 0]),
                    'AFT_Family': best_name
                })

pred_df = pd.DataFrame(pred_records)
pred_df.to_csv(folder_path + "aft_predicted_survival_grid.csv", index=False)
print("AFT predictions exported:", folder_path + "aft_predicted_survival_grid.csv")
