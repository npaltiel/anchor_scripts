import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

# --- FILE PATHS ---
raw_path = r"C:\Users\nochu\OneDrive - Anchor Home Health care\Documents\Underutilization Report\Files\Authorizations_Under_Utilized.csv"
report_path_prev = r"C:\Users\nochu\OneDrive - Anchor Home Health care\Documents\Underutilization Report\Underutilized Weekly Reports\Underutilization Report - 12-03-2025.xlsx"
report_path_out = r"C:\Users\nochu\OneDrive - Anchor Home Health care\Documents\Underutilization Report\Underutilized Weekly Reports\Underutilization Report - Test.xlsx"
hist_path = r"C:\Users\nochu\OneDrive - Anchor Home Health care\Documents\Underutilization Report\Files\Historical Table.xlsx"

# ============================================================
# 1. READ & PREP RAW DATA
# ============================================================

raw_df = pd.read_csv(raw_path, skiprows=3)

raw_df.columns = [
    "Auth Type",
    "Row Num",
    "AdmissionID",
    "Patient Name",
    "Auth Period",
    "ScheduledTime",
    "Contract",
    "Coordinator",
    "Auth Number",
    "Report Notes",
    "Visit Date",
    "Authorized Hours",
    "Assigned Hours",
    "Discipline",
    "Service Code",
    "NurseAssigned",
    "PatientStatus",
    "ProgramCode"
]

raw_df = raw_df[raw_df["Auth Type"] == "Daily"]

raw_df["Visit Date"] = pd.to_datetime(raw_df["Visit Date"], errors="coerce")
raw_df["Assigned Hours"] = pd.to_numeric(raw_df["Assigned Hours"], errors="coerce").fillna(0)

# Determine "week date" = max Visit Date
run_date = raw_df["Visit Date"].max().date()

# 1. Coordinator Only
raw_df["Coordinator Only"] = raw_df["Coordinator"].astype(str).str.split(",", n=1).str[0]

# 2. Team
tmp = raw_df["Coordinator Only"].astype(str).str.replace("PCA ", "", regex=False)
tmp2 = tmp.str.split(" ", n=1).str[0]
raw_df["Team"] = tmp2.str.split("-", n=1).str[0]

# 3. Underutilized
raw_df["Amount Underutilized"] = raw_df["Authorized Hours"] - raw_df["Assigned Hours"]

# 4. Overall daily
raw_df["Amount Underutilized Overall daily"] = (
    raw_df.groupby(["AdmissionID", "Visit Date"])["Amount Underutilized"].transform("sum")
)

# 5. Day of the Week
raw_df["Day of the Week"] = raw_df["Visit Date"].dt.day_name()

# 6. Consistency count
raw_df["Consistent"] = (
    raw_df.groupby(["AdmissionID", "Day of the Week", "Contract"])["Visit Date"].transform(lambda x: x.nunique())
)

# 7. Minimum Underutilized
raw_df["Amount Consistently Underutilized"] = (
    raw_df.groupby(["AdmissionID", "Day of the Week", "Contract"])["Amount Underutilized Overall daily"].transform(
        "min")
)

# 8. Recused?
recused_list = [
    "PCA T3 Hold or Refusing",
    "PCA T3 Pending Onboarding CG",
    "PCA T6 pending CG",
    "PA - New admissions"
]
raw_df["Recused?"] = raw_df["Coordinator Only"].isin(recused_list)

# ============================================================
# 2. READ PRIOR TEAM TABS & APPLY FALLBACK LOGIC
# ============================================================

team_tabs = ["T1", "T2", "T3", "T4", "T5", "T6", "PA"]
frames = []

for tab in team_tabs:
    df_prev = pd.read_excel(report_path_prev, sheet_name=tab, skiprows=2)
    frames.append(df_prev)

teams_df = pd.concat(frames, ignore_index=True)
teams_df = teams_df.dropna(subset=["AdmissionID"])

# Clean blanks
teams_df["Notes"] = teams_df["Notes"].replace("", pd.NA)
teams_df["Approved"] = teams_df["Approved"].replace("", pd.NA)

teams_df["New Notes"] = teams_df["Notes"].fillna(teams_df["Previous Notes"])
teams_df["New Approved"] = teams_df["Approved"].fillna(teams_df["Previously Approved"])

# Force boolean
teams_df["New Approved"] = teams_df["New Approved"].astype(bool)

# Approved hours
teams_df["New Approved Hours"] = teams_df.apply(
    lambda row: row["Minimum Underutilized"] if bool(row["New Approved"]) else 0,
    axis=1
)

# Replace older values
teams_df["Previously Approved Hours"] = teams_df["New Approved Hours"].fillna(
    teams_df["Previously Approved Hours"]
)

teams_df = teams_df.drop(columns=["Previous Notes", "New Approved Hours", "Notes", "Approved", "Previously Approved"])
teams_df = teams_df.rename(columns={"New Notes": "Previous Notes", "New Approved": "Previously Approved"})

# ============================================================
# 3. READ HISTORY, NORMALIZE, APPEND NEW SNAPSHOT
# ============================================================

try:
    hist_df = pd.read_excel(hist_path)
except FileNotFoundError:
    hist_df = pd.DataFrame()

# Normalize history date and boolean
if "Date" in hist_df.columns:
    hist_df["Date"] = pd.to_datetime(hist_df["Date"], errors="coerce").dt.date
if "Previously Approved" in hist_df.columns:
    hist_df["Previously Approved"] = hist_df["Previously Approved"].astype(bool)

# Build snapshot to append
teams_df["Date"] = run_date

hist_append = teams_df[[
    "Date",
    "Coordinator",
    "AdmissionID",
    "Patient Name",
    "Day of the Week",
    "Minimum Underutilized",
    "Previously Approved",
    "Previously Approved Hours",
    "Previous Notes"
]]

# Append and normalize
updated_history = pd.concat([hist_df, hist_append], ignore_index=True)
updated_history["Date"] = pd.to_datetime(updated_history["Date"], errors="coerce").dt.date
updated_history["Previously Approved"] = updated_history["Previously Approved"].astype(bool)

updated_history.to_excel(hist_path, index=False)

# ============================================================
# 4. BUILD LATEST SNAPSHOT FROM HISTORY, MERGE INTO RAW
# ============================================================

hist_latest = (
    updated_history
    .sort_values("Date", ascending=False)
    .drop_duplicates(subset=["AdmissionID", "Day of the Week"], keep="first")
)

raw_df = raw_df.merge(
    hist_latest[[
        "AdmissionID",
        "Day of the Week",
        "Previous Notes",
        "Previously Approved",
        "Previously Approved Hours"
    ]],
    on=["AdmissionID", "Day of the Week"],
    how="left"
)

raw_df["Previously Approved"] = raw_df["Previously Approved"].fillna(False).astype(bool)
raw_df["Previously Approved Hours"] = raw_df["Previously Approved Hours"].fillna(0)


# ============================================================
# 5. BUILD TEAM TABLES
# ============================================================

def build_team_table(df, team):
    out = df[
        (df["Consistent"] == 3) &
        (df["Team"] == team) &
        (df["Recused?"] == False) &
        (df["Amount Consistently Underutilized"] > df["Previously Approved Hours"])
        ][[
        "Coordinator Only",
        "AdmissionID",
        "Patient Name",
        "Day of the Week",
        "Amount Consistently Underutilized",
        "Previous Notes",
        "Previously Approved",
        "Previously Approved Hours"
    ]]

    out = out.rename(columns={
        "Coordinator Only": "Coordinator",
        "Amount Consistently Underutilized": "Minimum Underutilized"
    })

    out["Previously Approved"] = out["Previously Approved"].astype(bool)
    return out.drop_duplicates().sort_values(["Coordinator", "AdmissionID"])


T1 = build_team_table(raw_df, "T1")
T2 = build_team_table(raw_df, "T2")
T3 = build_team_table(raw_df, "T3")
T4 = build_team_table(raw_df, "T4")
T5 = build_team_table(raw_df, "T5")
T6 = build_team_table(raw_df, "T6")
PA = build_team_table(raw_df, "PA")

all_teams = pd.concat([T1, T2, T3, T4, T5, T6, PA], ignore_index=True)


# ============================================================
# 6. WRITE UNDERUTILIZATION REPORT - TEST.XLSX
# ============================================================

def write_sheet_with_format(writer, df, sheet):
    df.to_excel(writer, sheet_name=sheet, index=False, startrow=2)


def autosize_columns(ws):
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        header = ws[f"{col_letter}3"].value

        max_len = 0
        for cell in col:
            if cell.value is not None:
                max_len = max(max_len, len(str(cell.value)))

        if header in ("Previous Notes", "Notes", "Report Notes"):
            ws.column_dimensions[col_letter].width = max(25, max_len + 5)
        else:
            ws.column_dimensions[col_letter].width = max_len + 3


def add_boolean_validation(ws, col_letter, start, end):
    if end < start:
        return
    dv = DataValidation(type="list", formula1='"TRUE,FALSE"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"{col_letter}{start}:{col_letter}{end}")


with pd.ExcelWriter(report_path_out, engine="openpyxl", mode="w") as writer:
    for name, frame in {
        "Raw Data": raw_df,
        "T1": T1,
        "T2": T2,
        "T3": T3,
        "T4": T4,
        "T5": T5,
        "T6": T6,
        "PA": PA
    }.items():

        frame = frame.copy()

        # Add Notes/Approved only on team tabs
        if name not in ("Raw Data", "All Teams"):
            frame["Notes"] = ""
            frame["Approved"] = ""

        write_sheet_with_format(writer, frame, name)

# Post-format
wb = load_workbook(report_path_out)

for sheet in wb.sheetnames:
    ws = wb[sheet]
    autosize_columns(ws)

    if sheet not in ("Raw Data", "All Teams"):
        approved_col = None
        for cell in ws[3]:
            if cell.value == "Approved":
                approved_col = cell.column_letter
                break
        if approved_col:
            add_boolean_validation(ws, approved_col, 4, ws.max_row)

wb.save(report_path_out)

print(raw_df.head())
