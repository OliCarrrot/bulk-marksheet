#from reportlab.pdfgen import canvas
#pdf = canvas.Canvas("test.pdf")
#pdf.drawString(100, 750, "Bulk Marksheet System")
#df.drawString(100, 720, "PDF ganeration working")
#pdf.save()

#print("PDF created successful")

from reportlab.pdfgen import canvas

def create_marksheet(student):
    filename = f"output/{student['student_id']}_marksheet.pdf"

    pdf = canvas.Canvas(filename)

    # Title
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawCentredString(300, 780, "BULK MARKSHEET SYSTEM")

    # Student information
    pdf.setFont("Helvetica", 12)
    pdf.drawString(80, 730, f"Student ID: {student['student_id']}")
    pdf.drawString(80, 705, f"Name: {student['name']}")

    # Marks section
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(80, 660, "Subject Marks")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 630, f"Math: {student['math']}")
    pdf.drawString(100, 605, f"English: {student['english']}")
    pdf.drawString(100, 580, f"Science: {student['science']}")

    # Result section
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(80, 530, "Result")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 500, f"Total: {student['total']}")
    pdf.drawString(100, 475, f"Percentage: {student['percentage']:.2f}%")
    pdf.drawString(100, 450, f"Grade: {student['grade']}")
    pdf.drawString(100, 425, f"Result: {student['result']}")

    pdf.save()