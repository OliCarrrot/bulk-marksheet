def validate_marks(students):
    subjects = ["math", "english", "science"]

    for subject in subjects:
        if (students[subject] < 0).any() or (students[subject] > 100).any():
            return False

    return True