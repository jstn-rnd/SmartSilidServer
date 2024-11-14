from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Q
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet
from .models import UserLog, RFID


def parse_date(date_str):
    """ Parse date string in 'YYYY-MM-DD' format and return a date object. """
    return timezone.datetime.strptime(date_str, '%Y-%m-%d').date()

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def generate_faculty_report_excel(request):

#     user_logs = UserLog.objects.filter(faculty__isnull=False).select_related('faculty', 'computer')
#     report_data = []
#     for log in user_logs:
#         rfid = RFID.objects.filter(faculty=log.faculty).first()
#         report_data.append({
#             "Faculty Username": log.faculty.username,
#             "Faculty Name": f"{log.faculty.first_name} {log.faculty.last_name}",
#             "Computer Name": log.computer.computer_name if log.computer else None,
#             "Log on Date": log.date,
#             "Log on Time": log.logonTime,
#             "Log off Time": log.logoffTime,
#         })
    
#     # Create a pandas DataFrame
#     df = pd.DataFrame(report_data)
#     response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     response['Content-Disposition'] = 'attachment; filename=faculty_report.xlsx'

#     # Convert the DataFrame to Excel and write it to the response
#     with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
#         df.to_excel(writer, index=False, sheet_name='Faculty Report')
#         workbook  = writer.book
#         worksheet = writer.sheets['Faculty Report']

#         # Adjust column width based on max length of content
#         for idx, col in enumerate(df.columns):
#             max_len = df[col].astype(str).map(len).max()  
#             max_len = max(max_len, len(col))  
#             worksheet.set_column(idx, idx, max_len + 2)  
#         worksheet.set_column('E:E', 12, workbook.add_format({'num_format': 'yyyy-mm-dd'}))

#     return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_faculty_report_pdf(request):
    # Get query parameters for start_date, end_date
    start_date_str = request.query_params.get('start_date')
    end_date_str = request.query_params.get('end_date')

    if not start_date_str or not end_date_str:
        return HttpResponse("Both start_date and end_date are required.", status=400)

    # Parse the start and end dates
    start_date = parse_date(start_date_str)
    end_date = parse_date(end_date_str)

    # Create a buffer to hold the PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Headers for the table
    headers = ["Faculty Username", "Faculty Name", "Computer", "Log on Date", "Log on Time", "Log off Time"]
    data = [headers]

    # Filter UserLogs for faculty within the given date range
    user_logs = UserLog.objects.filter(
        faculty__isnull=False,  # Only include faculty logs
        date__range=[start_date, end_date]  # Filter by the date range
    ).select_related('faculty', 'computer')

    # Prepare data for the report
    for log in user_logs:
        rfid = RFID.objects.filter(faculty=log.faculty).first()
        row = [
            log.faculty.username,
            f"{log.faculty.first_name} {log.faculty.last_name}",
            log.computer.computer_name if log.computer else 'N/A',
            log.date,
            log.logonTime,
            log.logoffTime if log.logoffTime else 'Not yet Logged off'
        ]
        data.append(row)

    # Create the title and include date range
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']

    # Format date range to display in the title
    date_range_str = f"From {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}"

    # Title and date range paragraph
    title = Paragraph(f"Faculty Computer Log Report", title_style)
    date_range_paragraph = Paragraph(f"<strong>Date Range:</strong> {date_range_str}", styles['Normal'])

    # Add a space before the table
    space = Spacer(1, 20)  # Empty paragraph for space
    space2 = Spacer(1, 10)  # Extra empty paragraph for more space

    # Create the table
    table = Table(data)

    # Apply table styles
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#75bdc3')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#e0f2ff')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))

    # Build the PDF with title, date range, and space before the table
    doc.build([title, date_range_paragraph, space, space2, table])

    # Return the PDF as response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=faculty_report.pdf'

    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_student_report_pdf(request):
    # Get query parameters for start_date, end_date, and section
    start_date_str = request.query_params.get('start_date')
    end_date_str = request.query_params.get('end_date')
    section = request.query_params.get('section', '')  # Default to empty string if not specified

    if not start_date_str or not end_date_str:
        return HttpResponse("Both start_date and end_date are required.", status=400)

    # Parse the start and end dates
    start_date = parse_date(start_date_str)
    end_date = parse_date(end_date_str)

    # Create a buffer to hold the PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Headers for the table
    headers = ["Student Username", "Student Name", "Section", "Computer", "Logon Date", "Logon Time", "Logoff Time"]
    data = [headers]

    # Base filter for UserLogs by date range
    filters = {
        'student__isnull': False,  # Only include student logs
        'date__range': [start_date, end_date],  # Filter by date range
    }

    # If section is specified, filter by section; if not, include all sections
    if section:
        filters['student__section__name'] = section  # Filter by section name

    # Query UserLogs with the dynamic filters
    student_logs = UserLog.objects.filter(**filters).select_related('student', 'computer', 'student__section')

    # Prepare data for the report
    for log in student_logs:
        row = [
            log.student.username,
            f"{log.student.first_name} {log.student.last_name}",
            log.student.section.name if log.student.section else 'N/A',  # Include section info
            log.computer.computer_name if log.computer else 'N/A',
            log.date,
            log.logonTime,
            log.logoffTime if log.logoffTime else 'N/A'
        ]
        data.append(row)

    # Create the title and include the section information
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']

    # Title including section
    title = Paragraph(f"Student Computer Log Report<br/>Section: {section.capitalize() if section else 'All Sections'}", title_style)

    # Format date range to display in the title
    date_range_str = f"From {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}"

    # Add a paragraph with the date range
    date_range_paragraph = Paragraph(f"<strong>Date Range:</strong> {date_range_str}", styles['Normal'])

    # Add some space (empty paragraphs) before the table
    space = Spacer(1, 20)  # Empty paragraph for space
    space2 = Spacer(1, 10)  # Extra empty paragraph for more space

    # Add title, date range, and space before table
    table = Table(data)

    # Apply table styles
    table.setStyle(TableStyle([ 
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#75bdc3')),  
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), 
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#e0f2ff')), 
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'), 
        ('FONTSIZE', (0, 1), (-1, -1), 10),  
    ]))

    # Build the PDF with title, date range, and the table
    doc.build([title, date_range_paragraph, space, space2, table])

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=student_report_{start_date}_{end_date}.pdf'

    return response

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def generate_student_report_excel(request):
#     period = request.query_params.get('period', 'daily')  # Default to daily if not specified
#     start_date, end_date = get_date_range(period)

#     # Query UserLogs for students within the specified date range
#     student_logs = UserLog.objects.filter(student__isnull=False, date__range=[start_date, end_date]).select_related('student', 'computer', 'student__section')

#     # Prepare data for the report
#     report_data = []
#     for log in student_logs:
#         report_data.append({
#             "Student Username": log.student.username,
#             "Student Name": f"{log.student.first_name} {log.student.last_name}",
#             "Section": log.student.section.name if log.student.section else 'N/A',
#             "Computer Name": log.computer.computer_name if log.computer else None,
#             "Logon Date": log.date,
#             "Logon Time": log.logonTime,
#             "Logoff Time": log.logoffTime,
#         })

#     # Create a pandas DataFrame
#     df = pd.DataFrame(report_data)
#     response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     response['Content-Disposition'] = f'attachment; filename=student_report_{period}.xlsx'

#     # Convert the DataFrame to Excel and write it to the response
#     with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
#         df.to_excel(writer, index=False, sheet_name='Student Report')
#         workbook  = writer.book
#         worksheet = writer.sheets['Student Report']

#         # Adjust column width based on max length of content
#         for idx, col in enumerate(df.columns):
#             max_len = df[col].astype(str).map(len).max()
#             max_len = max(max_len, len(col))
#             worksheet.set_column(idx, idx, max_len + 2)

#         worksheet.set_column('D:D', 12, workbook.add_format({'num_format': 'hh:mm:ss AM/PM'}))
#         worksheet.set_column('E:E', 12, workbook.add_format({'num_format': 'hh:mm:ss AM/PM'}))

#     return response
