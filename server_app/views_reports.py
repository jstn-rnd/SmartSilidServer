import pandas as pd
import openpyxl
from openpyxl.styles import Alignment, Font, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from django.http import HttpResponse
from datetime import date
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from .models import UserLog, RFID

def parse_date(date_str):
    """ Parse date string in 'YYYY-MM-DD' format and return a date object. """
    return timezone.datetime.strptime(date_str, '%Y-%m-%d').date()

def get_default_dates():
    """ Return default start and end dates if not provided in the query. """
    today = date.today()
    start_date = date(today.year, today.month, 1)  # Default to the 1st of the current month
    end_date = today  # Default to today's date
    return start_date, end_date

def set_column_widths(sheet, dataframe):
    """ Automatically adjust column widths based on the max length of the data in each column. """
    for idx, col in enumerate(dataframe.columns, 1):
        max_length = max(dataframe[col].astype(str).apply(len).max(), len(col))
        sheet.column_dimensions[openpyxl.utils.get_column_letter(idx)].width = max_length + 2  # Add some padding

def apply_borders(sheet):
    """ Apply borders to all cells in the sheet. """
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    for row in sheet.iter_rows():
        for cell in row:
            cell.border = thin_border

def format_headers(sheet):
    """ Format header row with bold font and centered alignment. """
    for cell in sheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center', vertical='center')

def format_dates(sheet, date_columns):
    """ Format date columns in the sheet. """
    for col in date_columns:
        for cell in sheet[col]:
            if isinstance(cell.value, date):
                cell.number_format = 'YYYY-MM-DD'  # Format as date
            elif isinstance(cell.value, str) and 'AM' in cell.value or 'PM' in cell.value:
                cell.alignment = Alignment(horizontal='center')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_faculty_report_excel(request):
    # Get query parameters for start_date, end_date
    start_date_str = request.query_params.get('start_date')
    end_date_str = request.query_params.get('end_date')

    # If no date is provided, use default dates
    if not start_date_str or not end_date_str:
        start_date, end_date = get_default_dates()
    else:
        # Parse the start and end dates
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)

    # Filter UserLogs for faculty within the given date range
    user_logs = UserLog.objects.filter(
        faculty__isnull=False,  # Only include faculty logs
        date__range=[start_date, end_date]  # Filter by the date range
    ).select_related('faculty', 'computer')

    user_logs = user_logs.order_by('-date', '-logonTime')  # Ordering by date and logonTime in descending order

    # Prepare data for the report
    data = []
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

    # Convert data to DataFrame
    df = pd.DataFrame(data, columns=["Faculty Username", "Faculty Name", "Computer", "Log on Date", "Log on Time", "Log off Time"])

    # Create an HTTP response with the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=faculty_report.xlsx'

    # Write the DataFrame to the Excel file
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Faculty Log Report')

        # Get the sheet
        sheet = writer.sheets['Faculty Log Report']
        
        # Set column widths
        set_column_widths(sheet, df)

        # Apply formatting to headers
        format_headers(sheet)

        # Apply borders to all cells
        apply_borders(sheet)

        # Format date columns (Log on Date and Log off Time)
        format_dates(sheet, date_columns=['D', 'F'])

    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_student_report_excel(request):
    # Get query parameters for start_date, end_date, and section
    start_date_str = request.query_params.get('start_date')
    end_date_str = request.query_params.get('end_date')
    section = request.query_params.get('section', '')  # Default to empty string if not specified

    # If no date is provided, use default dates
    if not start_date_str or not end_date_str:
        start_date, end_date = get_default_dates()
    else:
        # Parse the start and end dates
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)

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

    student_logs = student_logs.order_by('-date', '-logonTime')  # Ordering by date and logonTime in descending order

    # Prepare data for the report
    data = []
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

    # Convert data to DataFrame
    df = pd.DataFrame(data, columns=["Student Username", "Student Name", "Section", "Computer", "Logon Date", "Logon Time", "Logoff Time"])

    # Create an HTTP response with the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=student_report_{start_date}_{end_date}.xlsx'

    # Write the DataFrame to the Excel file
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Student Log Report')

        # Get the sheet
        sheet = writer.sheets['Student Log Report']
        
        # Set column widths
        set_column_widths(sheet, df)

        # Apply formatting to headers
        format_headers(sheet)

        # Apply borders to all cells
        apply_borders(sheet)

        # Format date columns (Log on Date and Log off Time)
        format_dates(sheet, date_columns=['E', 'F'])

    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_combined_report_excel(request):
    # Get query parameters for start_date, end_date, and section
    start_date_str = request.query_params.get('start_date')
    end_date_str = request.query_params.get('end_date')

    # If no date is provided, use default dates
    if not start_date_str or not end_date_str:
        start_date, end_date = get_default_dates()
    else:
        # Parse the start and end dates
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)

    # Filter both Faculty and Student logs within the given date range
    user_logs = UserLog.objects.filter(
        date__range=[start_date, end_date]  # Filter by date range
    ).select_related('faculty', 'student', 'computer')

    user_logs = user_logs.order_by('-date', '-logonTime')  # Ordering by date and logonTime in descending order

    # Prepare data for the combined report
    data = []
    for log in user_logs:
        if log.faculty:
            row = [
                log.faculty.username,
                f"{log.faculty.first_name} {log.faculty.last_name}",
                'Faculty',
                log.computer.computer_name if log.computer else 'N/A',
                log.date,
                log.logonTime,
                log.logoffTime if log.logoffTime else 'Not yet Logged off'
            ]
        elif log.student:
            row = [
                log.student.username,
                f"{log.student.first_name} {log.student.last_name}",
                'Student',
                log.computer.computer_name if log.computer else 'N/A',
                log.date,
                log.logonTime,
                log.logoffTime if log.logoffTime else 'Not yet Logged off'
            ]
        data.append(row)

    # Convert data to DataFrame
    df = pd.DataFrame(data, columns=["Username", "Name", "Role", "Computer", "Logon Date", "Logon Time", "Logoff Time"])

    # Create an HTTP response with the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=combined_report.xlsx'

    # Write the DataFrame to the Excel file
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Combined Log Report')

        # Get the sheet
        sheet = writer.sheets['Combined Log Report']
        
        # Set column widths
        set_column_widths(sheet, df)

        # Apply formatting to headers
        format_headers(sheet)

        # Apply borders to all cells
        apply_borders(sheet)

        # Format date columns (Log on Date and Log off Time)
        format_dates(sheet, date_columns=['E', 'F'])

    return response