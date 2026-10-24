
SUBJECTS = ["bengali", "mathematics", "english", "science"]


def calculate_marks(students):
    students["total"] = students[SUBJECTS].sum(axis=1)
    students["percentage"] = students["total"] / len(SUBJECTS)
    return students


def calculate_grade(percentage):
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    else:
        return "F"


def calculate_result(row):
    if all(row[subject] >= 40 for subject in SUBJECTS):
        return "PASS"
    return "FAIL"