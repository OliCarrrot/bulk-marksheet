import io
import os
import zipfile

import pandas as pd
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename

from validation import validate_marks
from marks import (
    calculate_marks,
    calculate_grade,
    calculate_result,
)
from pdf import create_marksheet


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024

OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.errorhandler(413)
def file_too_large(error):
    return render_template(
        "index.html",
        error="Upload too large. Keep the combined upload below 15 MB."
    ), 413


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    school_name = request.form.get("school_name", "").strip()
    school_address = request.form.get("school_address", "").strip()
    school_email = request.form.get("school_email", "").strip()
    school_phone = request.form.get("school_phone", "").strip()
    academic_year = request.form.get("academic_year", "").strip()

    if not all([
        school_name, school_address, school_email,
        school_phone, academic_year
    ]):
        return render_template(
            "index.html",
            error="Please complete all school details."
        )

    uploaded_file = request.files.get("file")

    if not uploaded_file or not uploaded_file.filename:
        return render_template(
            "index.html",
            error="Please select a student CSV or Excel file."
        )

    extension = os.path.splitext(uploaded_file.filename)[1].lower()

    try:
        if extension == ".csv":
            students = pd.read_csv(uploaded_file, dtype=str)
        elif extension == ".xlsx":
            students = pd.read_excel(
                uploaded_file, dtype=str, engine="openpyxl"
            )
        else:
            return render_template(
                "index.html",
                error="Upload a CSV or XLSX student file."
            )
    except (
        pd.errors.ParserError,
        pd.errors.EmptyDataError,
        ValueError,
        OSError,
    ):
        return render_template(
            "index.html",
            error="Could not read the file. Check its format and contents."
        )

    # Reject empty files and excessive record counts.
    if students.empty:
        return render_template(
            "index.html",
            error="The uploaded file contains no student records."
        )

    if len(students) > 500:
        return render_template(
            "index.html",
            error="Please upload no more than 500 student records at once."
        )

    # Validate the optional logo.
    logo_file = request.files.get("logo")
    logo_bytes = None

    if logo_file and logo_file.filename:
        logo_ext = os.path.splitext(logo_file.filename)[1].lower()

        if logo_ext not in {".png", ".jpg", ".jpeg"}:
            return render_template(
                "index.html",
                error="The school logo must be PNG or JPG."
            )

        logo_bytes = logo_file.read()

        if not logo_bytes:
            return render_template(
                "index.html",
                error="The selected logo file is empty."
            )

        if len(logo_bytes) > 5 * 1024 * 1024:
            return render_template(
                "index.html",
                error="The school logo must be under 5 MB."
            )

    # Validate student data before calculating results.
    if not validate_marks(students):
        return render_template(
            "index.html",
            error=(
                "Invalid student data. Check the required columns, "
                "student details, dates, marks, and attendance. "
                "See the terminal for more information."
            )
        )

    students = calculate_marks(students)
    students["grade"] = students["percentage"].apply(calculate_grade)
    students["result"] = students.apply(calculate_result, axis=1)

    zip_buffer = io.BytesIO()

    try:
        with zipfile.ZipFile(
            zip_buffer, "w", zipfile.ZIP_DEFLATED
        ) as zip_file:
            for _, student in students.iterrows():
                pdf_path = create_marksheet(
                    student,
                    school_name,
                    school_address,
                    school_email,
                    school_phone,
                    academic_year,
                    logo_bytes,
                )

                # Use only the generated PDF's basename in the ZIP.
                zip_file.write(
                    pdf_path,
                    arcname=secure_filename(os.path.basename(pdf_path))
                )

        zip_buffer.seek(0)

        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name="student_progress_reports.zip",
        )

    except (OSError, ValueError) as error:
        app.logger.exception("Marksheet generation failed")
        return render_template(
            "index.html",
            error=f"Could not generate the PDFs: {error}"
        ), 400


if __name__ == "__main__":
    app.run(debug=True)
