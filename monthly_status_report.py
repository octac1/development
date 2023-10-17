# Copyright (c) 2023, Riverstone and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document

@frappe.whitelist()
def get_employees_list(project):
    project_users = frappe.get_all('Project User', filters={'parent': project}, fields=['user'])
    return project_users

@frappe.whitelist()
def get_accomplishments(doc):
    doc_dict = json.loads(doc)
    month = doc_dict.get('month')
    project = doc_dict.get('project')
    query = f"""SELECT DISTINCT wsd.ticket_subject, wsd.project
    FROM `tabDaily Work Status Report` AS dws
    JOIN `tabWork Status Details` AS wsd
    ON dws.name = wsd.parent AND wsd.ticket_subject IS NOT NULL
    AND dws.month = '{month}' AND wsd.project = '{project}'"""

    accomplishment_lists = frappe.db.sql(query, as_dict = True)
    subjects = [row['ticket_subject'] for row in accomplishment_lists]
    return subjects

@frappe.whitelist()
def get_testing_task_details(doc):
    doc_dict = json.loads(doc)
    month = doc_dict.get('month')
    project = doc_dict.get('project')
    bug_counts = f"""SELECT dws.employee, SUM(wsd.bugs_found) AS issues_found
    FROM `tabDaily Work Status Report` AS dws
    JOIN `tabWork Status Details` AS wsd ON dws.name = wsd.parent
    WHERE dws.role_played = "Testing"
    AND dws.month = '{month}' AND wsd.project = '{project}'
    GROUP BY dws.employee"""

    automation_counts = f"""SELECT dws.employee, SUM(wsd.automation_scenarios) AS automation_count
    FROM `tabDaily Work Status Report` AS dws
    JOIN `tabWork Status Details` AS wsd ON dws.name = wsd.parent
    WHERE dws.role_played = "Testing"
    AND dws.month = '{month}' AND wsd.project = '{project}'
    GROUP BY dws.employee"""

    testcase_counts = f"""SELECT dws.employee, SUM(wsd.testcase_written) AS testcase_count
    FROM `tabDaily Work Status Report` AS dws
    JOIN `tabWork Status Details` AS wsd ON dws.name = wsd.parent
    WHERE dws.role_played = "Testing"
    AND dws.month = '{month}' AND wsd.project = '{project}'
    GROUP BY dws.employee"""

    bug_counts_list = frappe.db.sql(bug_counts, as_dict = True)
    automation_counts_list = frappe.db.sql(automation_counts, as_dict = True)
    testcase_counts_list = frappe.db.sql(testcase_counts, as_dict = True)
    testers_task_count = {}
    for bug in bug_counts_list:
        employee = bug['employee']
        issues_found = bug['issues_found']
        if employee in testers_task_count:
            testers_task_count[employee]['issues_found'] = issues_found
        else:
            testers_task_count[employee] = {'issues_found': issues_found}

    for automation in automation_counts_list:
        employee = automation['employee']
        automation_count = automation['automation_count']
        if employee in testers_task_count:
            testers_task_count[employee]['automation_count'] = automation_count
        else:
            testers_task_count[employee] = {'automation_count': automation_count}

    for item in testcase_counts_list:
        employee = item['employee']
        testcase_count = item['testcase_count']
        if employee in testers_task_count:
            testers_task_count[employee]['testcase_count'] = testcase_count
        else:
            testers_task_count[employee] = {'testcase_count': testcase_count}

    testers_task_lists = [{'employee': employee, **data} for employee, data in testers_task_count.items()]
    return testers_task_lists

@frappe.whitelist()
def get_development_task_details(doc):
    doc_dict = json.loads(doc)
    month = doc_dict.get('month')
    project = doc_dict.get('project')
    task_count = f"""SELECT dws.employee,
       SUM(CASE WHEN wsd.task_type = 'Bug' THEN 1 ELSE 0 END) AS bug_Count,
       SUM(CASE WHEN wsd.task_type = 'Feature' THEN 1 ELSE 0 END) AS feature_Count
       FROM `tabDaily Work Status Report` AS dws
       JOIN `tabWork Status Details` AS wsd ON dws.name = wsd.parent
       WHERE dws.role_played = "Development"
       AND dws.month = '{month}' AND wsd.project = '{project}'
       GROUP BY dws.employee"""

    tasks_count_list = frappe.db.sql(task_count, as_dict = True)
    developer_task_details = {}
    for task in tasks_count_list:
        developer_task_details[task.employee] = {
            "employee": task.employee,
            "bug_count": task.bug_Count,
            "feature_count": task.feature_Count
        }
    return developer_task_details
class MonthlyStatusReport(Document):
	pass
