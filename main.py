import pandas as pd

from validation import validate_marks
from marks import calculate_marks, calculate_grade, calculate_result
from pdf import create_marksheet

students = pd.read_csv("input/students.csv")

if not validate_marks(students):
    print("Invalid marks found!")
    exit()

# calculate total and percentage
students = calculate_marks(students)

# calculate grade
students["grade"] = students["percentage"].apply(calculate_grade)

# calculate pass or fail
students["result"] = students.apply(calculate_result, axis=1)

# display final result
print(students)

# create PDF for each student
for _, student in students.iterrows():
    create_marksheet(student)