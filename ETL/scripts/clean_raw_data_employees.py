import pandas as pd
import oracledb

# This script is in charge cleaning the raw data employees -> src_employees CSV that we will use to create timesheets

# --- Step 1: Load the source_raw_employees without the "Role" column
raw_df = pd.read_csv("../files/raw_employees.csv")
raw_df = raw_df.drop(columns=["Role"])
print("Raw Employees:", raw_df.shape)

# --- Step 2: Retrieve only the data part (without the meeting general info) from the 2 csv
def load_attendance(path):
    df = pd.read_csv(path, encoding="utf-16", sep="\t", skiprows=10)
    df = df.rename(columns={df.columns[0]: "FullName", df.columns[4]: "Email"})
    return df[["FullName", "Email"]].dropna()

attendance1 = load_attendance("../files/etl_meeting_1.csv")
attendance2 = load_attendance("../files/etl_meeting_2.csv")

# --- Step 3: Combine both attendance meetings and drop duplicates (achieve employee only once)
attendees = pd.concat([attendance1, attendance2]).drop_duplicates(subset="Email")  # drop on duplicate email
print("Total unique attendees with emails:", attendees.shape)

# --- Step 4: Keep only employees who were in at least one meeting (we are interested only in those)
merged_df = raw_df.merge(attendees, on="FullName", how="inner")
print("Filtered employees who attended:", merged_df.shape)

# --- Step 5: Split the full name into first and last name then drop fullName column
merged_df[["First_Name", "Last_Name"]] = merged_df["FullName"].str.extract(r"^(.*)\s+(\S+)$")
final_df = merged_df.drop(columns=["FullName"])

# --- Step 6: rearrange columns for the final structure (like in target table source_employees)
final_df = final_df[["First_Name", "Last_Name", "Email", "Title", "Location", "City"]]
final_df = final_df.drop(columns=["City"])
final_df.head()

# --- Step 7: Export cleaned employees to a CSV file
final_df.to_csv("../files/src_employees.csv", index=False)
print("Cleaned data exported to src_employees.csv")

