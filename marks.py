#import pandas as pd
#from validation import validate_marks
#from pdf import create_marksheet

def calculate_marks(students):
    students["total"] = (
        students["math"]
        + students["english"]
        + students["science"]
    )

    students["percentage"] = students["total"] / 3

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
    if (
        row["math"] >= 40
        and row["english"] >= 40
        and row["science"] >= 40
    ):
        return "PASS"
    else:
        return "FAIL"