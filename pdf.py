import io
import os
import re
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


PAGE_W, PAGE_H = A4
RED = colors.HexColor("#9E2028")
WATERMARK_RED = colors.HexColor("#D9A0A0")
GREEN = colors.HexColor("#28764A")
BLUE = colors.HexColor("#245A91")
BLACK = colors.HexColor("#222222")
GREY = colors.HexColor("#777777")
BORDER = colors.HexColor("#555555")
HEADER_FILL = colors.HexColor("#F1F1F1")

SUBJECTS = [
    ("english", "ENGLISH"),
    ("bengali", "BENGALI"),
    ("mathematics", "MATHEMATICS"),
    ("drawing_rhymes", "DRAWING & RHYMES"),
]

TERMS = [
    ("term1", "1ST TERM"),
    ("term2", "2ND TERM"),
    ("final", "FINAL EXAMINATION"),
]


def safe_filename(value):
    value = re.sub(r"[^A-Za-z0-9_-]+", "_", str(value)).strip("_")
    return value or "student"


def draw_watermark(pdf, school_name):
    """Draw a repeating light-red school-name watermark over the page."""
    label = (str(school_name).strip().upper() or "SCHOOL NAME")
    pdf.saveState()
    pdf.setFillColor(WATERMARK_RED, alpha=0.38)
    pdf.setFont("Helvetica-Bold", 8)

    step_x = 145
    step_y = 42

    for row, y in enumerate(range(35, int(PAGE_H), step_y)):
        offset = 0 if row % 2 == 0 else 35
        for x in range(-100 + offset, int(PAGE_W) + 100, step_x):
            pdf.drawString(x, y, label)

    pdf.restoreState()


def draw_text(pdf, x, y, value, size=8, bold=False, color=BLACK,
              align="left"):
    pdf.setFillColor(color)
    pdf.setFont("Helvetica-Bold" if bold else "Helvetica", size)

    value = "" if value is None else str(value)

    if align == "center":
        pdf.drawCentredString(x, y, value)
    elif align == "right":
        pdf.drawRightString(x, y, value)
    else:
        pdf.drawString(x, y, value)


def draw_cell(pdf, x, y, w, h, value="", size=6.5, bold=False,
              align="center", fill=None, color=BLACK):
    """Draw a table cell; keep the background transparent for the watermark."""
    if fill is not None:
        pdf.setFillColor(fill)
        pdf.rect(x, y, w, h, fill=1, stroke=0)

    pdf.setStrokeColor(BORDER)
    pdf.setLineWidth(0.45)
    pdf.rect(x, y, w, h, fill=0, stroke=1)

    value = "" if value is None else str(value)
    max_width = max(2, w - 4)
    font = "Helvetica-Bold" if bold else "Helvetica"

    while size > 4.5 and stringWidth(value, font, size) > max_width:
        size -= 0.25

    pdf.setFillColor(color)
    pdf.setFont(font, size)

    if align == "left":
        pdf.drawString(x + 3, y + (h - size) / 2 + 1, value)
    else:
        pdf.drawCentredString(x + w / 2, y + (h - size) / 2 + 1, value)


def draw_image_box(pdf, image_bytes, x, y, w, h, placeholder):
    pdf.setStrokeColor(BORDER)
    pdf.setLineWidth(0.8)
    pdf.rect(x, y, w, h, fill=0, stroke=1)

    if image_bytes:
        try:
            img = ImageReader(io.BytesIO(image_bytes))
            pdf.drawImage(
                img, x + 3, y + 3, w - 6, h - 6,
                preserveAspectRatio=True, anchor="c", mask="auto"
            )
            return
        except Exception:
            pass

    draw_text(
        pdf, x + w / 2, y + h / 2 - 3,
        placeholder, 7, color=GREY, align="center"
    )


def number_to_words(number):
    ones = [
        "ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE",
        "SIX", "SEVEN", "EIGHT", "NINE", "TEN", "ELEVEN",
        "TWELVE", "THIRTEEN", "FOURTEEN", "FIFTEEN",
        "SIXTEEN", "SEVENTEEN", "EIGHTEEN", "NINETEEN",
    ]
    tens = [
        "", "", "TWENTY", "THIRTY", "FORTY", "FIFTY",
        "SIXTY", "SEVENTY", "EIGHTY", "NINETY",
    ]

    if number < 0:
        return "MINUS " + number_to_words(-number)
    if number < 20:
        return ones[number]
    if number < 100:
        return tens[number // 10] + (
            " " + ones[number % 10] if number % 10 else ""
        )
    if number < 1000:
        return ones[number // 100] + " HUNDRED" + (
            " " + number_to_words(number % 100) if number % 100 else ""
        )
    if number < 1000000:
        return number_to_words(number // 1000) + " THOUSAND" + (
            " " + number_to_words(number % 1000) if number % 1000 else ""
        )
    return str(number)


def mark_value(student, subject, term, field):
    """Read fields such as english_term1_written from a student row."""
    key = f"{subject}_{term}_{field}"
    value = student.get(key, 0)

    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def fmt_mark(value):
    return f"{value:g}"


def create_marksheet(
    student,
    school_name,
    school_address,
    school_email="",
    school_phone="",
    academic_year="",
    logo_bytes=None,
    photo_bytes=None,
    reopening_date="",
    issue_date=None,
):
    os.makedirs("output", exist_ok=True)

    student_id = safe_filename(student.get("student_id", "student"))
    filename = os.path.join("output", f"{student_id}_marksheet.pdf")

    pdf = canvas.Canvas(filename, pagesize=A4)

    # White paper and security watermark first, so all content is above it.
    pdf.setFillColor(colors.white)
    pdf.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    draw_watermark(pdf, school_name)

    # Formal double border.
    pdf.setStrokeColor(colors.HexColor("#999999"))
    pdf.setLineWidth(2)
    pdf.rect(25, 25, PAGE_W - 50, PAGE_H - 50, fill=0, stroke=1)
    pdf.setLineWidth(0.5)
    pdf.rect(31, 31, PAGE_W - 62, PAGE_H - 62, fill=0, stroke=1)

    left, right = 43, PAGE_W - 43
    content_w = right - left
    center = PAGE_W / 2

    # Header and optional matching logos.
    draw_image_box(pdf, logo_bytes, left + 3, 738, 62, 62, "SCHOOL LOGO")
    draw_image_box(pdf, logo_bytes, right - 65, 738, 62, 62, "SCHOOL LOGO")

    school_name = str(school_name or "School Name").strip()
    font_size = 23
    while (
        font_size > 13
        and stringWidth(school_name, "Times-Bold", font_size) > content_w - 145
    ):
        font_size -= 1

    # Elegant red heading with a fine white and black outline.
    pdf.saveState()
    pdf.setFont("Times-Bold", font_size)
    pdf.setFillColor(RED)
    pdf.setStrokeColor(colors.white)
    pdf.setLineWidth(2.5)
    pdf.drawCentredString(center, 778, school_name)
    pdf.setStrokeColor(BLACK)
    pdf.setLineWidth(0.35)
    pdf.drawCentredString(center, 778, school_name)
    pdf.restoreState()

    draw_text(pdf, center, 761, "STUDENT PROGRESS REPORT",
              10, True, align="center")
    draw_text(pdf, center, 747, academic_year,
              8, True, align="center")
    draw_text(pdf, center, 735, str(school_address)[:100],
              6.5, align="center")
    draw_text(
        pdf, center, 724,
        f"Email: {school_email}  |  Phone: {school_phone}"[:110],
        6.5, align="center"
    )

    # Student details grid; photo box at upper right.
    details_top = 710
    row_h = 23
    photo_w, photo_h = 70, 94
    photo_x, photo_y = right - photo_w, details_top - photo_h

    info_right = photo_x - 7
    info_w = info_right - left
    label_w = 78
    value_w = (info_w - 2 * label_w) / 2

    details = [
        ("STUDENT'S NAME", student.get("name", ""),
         "FATHER'S NAME", student.get("father_name", "")),
        ("CLASS", student.get("class", ""),
         "SECTION", student.get("section", "")),
        ("DATE OF BIRTH", student.get("dob", ""),
         "REGN. NO.", student.get("registration_no", "")),
        ("ROLL NO.", student.get("roll_no", ""),
         "ATTENDANCE", f"{student.get('attendance', '')}%"),
    ]

    for i, (lab1, val1, lab2, val2) in enumerate(details):
        y = details_top - (i + 1) * row_h
        x_positions = [
            left, left + label_w, left + label_w + value_w,
            left + label_w + value_w + label_w, info_right
        ]
        draw_cell(pdf, x_positions[0], y, label_w, row_h, lab1,
                  5.8, True, "left", HEADER_FILL)
        draw_cell(pdf, x_positions[1], y, value_w, row_h, val1,
                  6.2, False, "left")
        draw_cell(pdf, x_positions[2], y, label_w, row_h, lab2,
                  5.8, True, "left", HEADER_FILL)
        draw_cell(pdf, x_positions[3], y, value_w, row_h, val2,
                  6.2, False, "left")

    draw_image_box(pdf, photo_bytes, photo_x, photo_y,
                   photo_w, photo_h, "STUDENT PHOTO")

    # Academic marks table: 3 columns per term, 9 columns plus subject.
    table_top = 605
    subject_w = 103
    metric_w = (content_w - subject_w) / 9
    xs = [left, left + subject_w]

    for _ in range(9):
        xs.append(xs[-1] + metric_w)

    group_h = 19
    sub_h = 27
    row_h = 22

    draw_cell(pdf, left, table_top - group_h - sub_h,
              subject_w, group_h + sub_h, "SUBJECTS",
              7, True, fill=HEADER_FILL)

    for i, (_, term_label) in enumerate(TERMS):
        x = left + subject_w + i * 3 * metric_w
        draw_cell(pdf, x, table_top - group_h, 3 * metric_w,
                  group_h, term_label, 6.2, True, fill=HEADER_FILL)

        sublabels = ["WRITTEN", "MARKS\nOBTAINED", "TOTAL"]
        for j, sublabel in enumerate(sublabels):
            draw_cell(
                pdf, x + j * metric_w, table_top - group_h - sub_h,
                metric_w, sub_h, sublabel.replace("\n", " "),
                5.1, True, fill=HEADER_FILL
            )

    rows = []
    for subject, label in SUBJECTS:
        values = []
        for term, _ in TERMS:
            values.extend([
                mark_value(student, subject, term, "written"),
                mark_value(student, subject, term, "obtained"),
                mark_value(student, subject, term, "total"),
            ])
        rows.append((label, values))

    # Grand total, percentage and grade for each examination period.
    term_totals = []
    term_percentages = []
    term_grades = []

    for term, _ in TERMS:
        total = sum(
            mark_value(student, subject, term, "total")
            for subject, _ in SUBJECTS
        )
        # Each subject is assumed to have a total maximum of 100.
        maximum = 400
        percentage = (total / maximum * 100) if maximum else 0

        if percentage >= 90:
            grade = "AA"
        elif percentage >= 80:
            grade = "A+"
        elif percentage >= 70:
            grade = "A"
        elif percentage >= 60:
            grade = "B+"
        elif percentage >= 50:
            grade = "B"
        else:
            grade = "C"

        term_totals.append(total)
        term_percentages.append(percentage)
        term_grades.append(grade)

    y = table_top - group_h - sub_h

    for label, values in rows:
        y -= row_h
        draw_cell(pdf, left, y, subject_w, row_h, label,
                  6.2, True, "left")
        for j, value in enumerate(values):
            draw_cell(pdf, xs[j + 1], y, metric_w, row_h,
                      fmt_mark(value), 5.6)

    summary_rows = [
        ("GRAND TOTAL", [
            value for total in term_totals for value in (total, total, total)
        ]),
        ("PERCENTAGE", [
            value for p in term_percentages for value in (p, p, p)
        ]),
        ("OVERALL GRADE", [
            value for grade in term_grades for value in (grade, grade, grade)
        ]),
    ]

    for label, values in summary_rows:
        y -= row_h
        draw_cell(pdf, left, y, subject_w, row_h, label,
                  6.2, True, "left", HEADER_FILL)
        for j, value in enumerate(values):
            if label == "PERCENTAGE":
                value = f"{value:.1f}%"
            draw_cell(pdf, xs[j + 1], y, metric_w, row_h,
                      str(value), 5.4, True, fill=HEADER_FILL)

    # Overall result row.
    y -= 28
    draw_cell(pdf, left, y, 92, 22, "FINAL RESULT",
              6.5, True, "left", HEADER_FILL)
    final_total = term_totals[-1]
    final_percentage = term_percentages[-1]
    final_grade = term_grades[-1]
    final_result = (
        "PASS" if all(
            mark_value(student, subject, "final", "obtained") >= 40
            for subject, _ in SUBJECTS
        ) else "NEEDS IMPROVEMENT"
    )

    draw_cell(pdf, left + 92, y, 90, 22, f"{final_total:g}/400", 6.5, True)
    draw_cell(pdf, left + 182, y, 90, 22,
              f"{final_percentage:.1f}%", 6.5, True)
    draw_cell(pdf, left + 272, y, 65, 22, final_grade, 6.5, True)
    draw_cell(pdf, left + 337, y, content_w - 337, 22,
              final_result, 6.2, True)

    # Grading scale footer boxes.
    y -= 18
    draw_text(pdf, center, y, "GRADING SCALE", 8, True, align="center")
    y -= 15

    box_h = 63
    gap = 8
    box_w = (content_w - gap) / 2

    left_x = left
    right_x = left + box_w + gap

    grade_rows = [
        ("90–100", "AA", "Outstanding"),
        ("80–89", "A+", "Excellent"),
        ("70–79", "A", "Very Good"),
        ("60–69", "B+", "Good"),
        ("50–59", "B", "Satisfactory"),
        ("Below 50", "C", "Needs Improvement"),
    ]

    for bx, title in [(left_x, "SCHOLASTIC GRADES"),
                      (right_x, "PERFORMANCE INDICATOR")]:
        pdf.setStrokeColor(BORDER)
        pdf.rect(bx, y - box_h, box_w, box_h, fill=0, stroke=1)
        draw_text(pdf, bx + box_w / 2, y - 10, title,
                  6.2, True, align="center")

    row_h = 8
    for i, (range_text, grade, description) in enumerate(grade_rows):
        yy = y - 20 - i * row_h
        draw_text(pdf, left_x + 5, yy, range_text, 5.8)
        draw_text(pdf, left_x + 75, yy, grade, 5.8, True)
        draw_text(pdf, left_x + 110, yy, description, 5.8)

        draw_text(pdf, right_x + 5, yy, grade, 5.8, True)
        draw_text(pdf, right_x + 42, yy, description, 5.8)

    # Dates.
    dates_y = y - box_h - 18
    issue_date = issue_date or date.today().strftime("%d-%m-%Y")
    draw_text(pdf, left, dates_y, "School Will Re-Open On:", 7, True)
    draw_text(pdf, left + 105, dates_y, reopening_date or "____________", 7)
    draw_text(pdf, right - 125, dates_y, "Issue Date:", 7, True)
    draw_text(pdf, right - 65, dates_y, issue_date, 7)

    # Signatures.
    sig_y = 65
    pdf.setStrokeColor(BLACK)
    pdf.setLineWidth(0.7)
    pdf.line(left + 5, sig_y + 13, left + 145, sig_y + 13)
    pdf.line(right - 145, sig_y + 13, right - 5, sig_y + 13)

    draw_text(pdf, left + 75, sig_y, "Class Teacher's Signature",
              7, True, align="center")
    draw_text(pdf, right - 75, sig_y, "Headmistress Signature",
              7, True, align="center")

    pdf.save()
    return filename