# Copyright (c) 2023, Riverstone and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe.utils import today, get_first_day, nowdate, strip_html, getdate
from itertools import groupby
from datetime import timedelta

class DailyWorkStatusReport(Document):
    pass

@frappe.whitelist()
def calculate_total_hours(ws_doc):
    ws_doc_list = json.loads(ws_doc)
    total_hours, total_minutes = 0, 0
    for hours in ws_doc_list:
        hours_value = hours.get("hours", "00:00:00")
        hours, minutes, seconds = map(int, hours_value.split(':'))
        if seconds > 0:
            minutes += 1
        total_hours += hours
        total_minutes += minutes
        total_hours += total_minutes // 60
        total_minutes %= 60
    total_work_hours = str(total_hours) + " " + "hrs" + " " + str(total_minutes)+ " " + "mins"
    return total_work_hours

def sent_email_for_dwsr_not_filled_employee():
    current_date = today()
    first_day_of_month = get_first_day(nowdate())
    project_governance_settings = frappe.get_doc("Project Governance Settings")
    # To get employees details
    employees = frappe.get_all("Employee", {'status': 'Active'}, ['name', 'employee_name', 'user_id', 'holiday_list', 'designation'])
    email_content = f"Hi Team, <br><br> The employees listed below have not submitted their daily work status report for the specified dates:"
    dates = ""
    for employee in employees:
        if employee.designation not in [project_governance_settings.employee_designation]:
            holiday_list = employee.get('holiday_list')
            # To get the daily work status report data filled by the employee
            dwsr_filled_employees = frappe.get_all('Daily Work Status Report', {
                'employee': employee.name,
                'date': ['between', (first_day_of_month, current_date)]
            }, 'date')
            date_range = {getdate(first_day_of_month) + timedelta(days=i) for i in range((getdate(current_date) - getdate(first_day_of_month)).days)}
            dates_from_dwsr = {getdate(date['date']) for date in dwsr_filled_employees}
            missing_dates = date_range - dates_from_dwsr
            missing_dates_list = [date.strftime("%Y-%m-%d") for date in missing_dates]
            # To get the holiday list details
            holiday_dates = [date['holiday_date'].strftime("%Y-%m-%d") for date in frappe.get_all('Holiday', {
                'parent': holiday_list,
                'holiday_date': ["between", (first_day_of_month, current_date)]
            }, 'holiday_date')]
            not_holiday_for_employee = [date for date in missing_dates_list if date not in holiday_dates]
            # To get the attendance details with absent and on leave status by the employee
            attendance_dates = [date['attendance_date'].strftime("%Y-%m-%d") for date in frappe.get_all('Attendance', {
                'employee': employee.name,
                'attendance_date': ['between', (first_day_of_month, current_date)],
                'status': ['in', ("Absent", "On Leave")]
            }, 'attendance_date')]
            dwsr_missing_dates = [date for date in not_holiday_for_employee if date not in attendance_dates]
            sorted_missing_dates = sorted(dwsr_missing_dates)
            dates = ", ".join(sorted_missing_dates)
            if dates:
                email_content += f"<b><br><br>{employee.employee_name}</b> - {dates}"
    if dates:
        email_subject = strip_html("Daily Work Status Report Submission Missed")
        frappe.sendmail(recipients = project_governance_settings.sw_group_email, subject = email_subject, content = email_content)
    return

def send_group_email_for_daily_work_status_report():
    today = frappe.utils.nowdate()

    dwsr_details = frappe.db.sql(
        f"""
        SELECT
            dwsr.employee, dwsr.date, dwsr.role_played,
            wsd.project, wsd.ticket, wsd.ticket_subject, wsd.task_type, wsd.ticket_status,
            wsd.feature_description, wsd.bug_description, p.custom_rit_group_email_id
        FROM 
            `tabDaily Work Status Report` AS dwsr
        INNER JOIN 
            `tabWork Status Details` AS wsd ON dwsr.name = wsd.parent
        LEFT JOIN 
            `tabProject` AS p ON wsd.project = p.name
        WHERE 
            date(dwsr.date) = '{today}'
        ORDER BY 
            wsd.project ASC
        """, as_dict=1)

    project_groups = {}

    for dwsr in dwsr_details:
        project = dwsr['project']
        project_groups.setdefault(project, []).append(dwsr)

    for project, entries in project_groups.items():
        email_content = f"Hi Team <br> The following is the work status report for {today}"
        subject = f"Work status for {project} {entries[0].date}"
        recipients = entries[0].custom_rit_group_email_id

        for entry in entries:
            email_content += f"<b><mark><br><br>{frappe.get_value('Employee', entry.employee, 'employee_name')}</mark></b>"
            sorted_by_type = sorted([entry], key=lambda x: x["task_type"])
            grouped_by_type = groupby(sorted_by_type, key=lambda x: x["task_type"])

            for type_, items in grouped_by_type:
                email_content += f" <br><b>{type_}(s) :</b>"
                for item in items:
                    if item["ticket"]:
                        email_content += f"<br><a href='{item['ticket']}'>{item['ticket']}</a> - {item['ticket_subject']} - <b>{item['ticket_status']}</b>"

                    if item["feature_description"] and type_ == "Feature" and item['role_played'] == "Development":
                        feature_description = item["feature_description"].replace("\n", "<br>")
                        email_content += f" <br>{feature_description}<br>"

                    elif item["bug_description"] and type_ == "Bug" and item['role_played'] == "Development":
                        bug_description = item["bug_description"].replace("\n", "<br>")
                        email_content += f" <br>{bug_description}<br>"

                    elif item["description"]:
                        description = item["description"].replace("\n", "<br>")
                        email_content += f" <br>{description}<br>"
                    else:
                        email_content += f" <br>"

        frappe.sendmail(recipients = recipients, subject = subject, content = email_content)
    return






