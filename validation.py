import pandas as pd


REQUIRED_COLUMNS = [
    "student_id", "name", "guardian_name", "class", "section",
    "roll_no", "dob", "registration_no", "attendance",
    "bengali", "mathematics", "english", "science"
]

SUBJECTS = ["bengali", "mathematics", "english", "science"]

TEXT_COLUMNS = [
    "student_id", "name", "guardian_name", "class", "section",
    "roll_no", "dob", "registration_no"
]


def validate_marks(students):
    # Check that every required column exists.
    missing = [
        column for column in REQUIRED_COLUMNS
        if column not in students.columns
    ]

    if missing:
        print("Missing columns:", ", ".join(missing))
        return False

    if students.empty:
        print("No student records found.")
        return False

    # Clean text fields and check required values.
    for column in TEXT_COLUMNS:
        students[column] = (
            students[column].fillna("").astype(str).str.strip()
        )

        if (students[column] == "").any():
            print(f"Missing information in '{column}'.")
            return False

    # IDs must be unique after trimming whitespace.
    if students["student_id"].duplicated().any():
        print("Duplicate student IDs found.")
        return False

    # Validate dates.
    dates = pd.to_datetime(students["dob"], errors="coerce")
    if dates.isna().any():
        print("Invalid date of birth. Use YYYY-MM-DD.")
        return False

    students["dob"] = dates.dt.strftime("%Y-%m-%d")

    # Convert and validate marks.
    for subject in SUBJECTS:
        students[subject] = pd.to_numeric(
            students[subject], errors="coerce"
        )

        if students[subject].isna().any():
            print(f"Missing or invalid marks in '{subject}'.")
            return False

        if (
            (students[subject] < 0)
            | (students[subject] > 100)
        ).any():
            print(f"'{subject}' marks must be between 0 and 100.")
            return False

    # Validate attendance percentage.
    students["attendance"] = pd.to_numeric(
        students["attendance"], errors="coerce"
    )

    if (
        students["attendance"].isna().any()
        or (students["attendance"] < 0).any()
        or (students["attendance"] > 100).any()
    ):
        print("Attendance must be between 0 and 100.")
        return False

    return True