# coding=utf-8

import logging
import os

import httplib2
from apiclient import discovery
from googleapiclient.discovery import Resource
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# suppress warnings from googleapi about file_cache
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

try:
    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
# SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

# this id is extracted from the link to a spreadshit of interest:
# https://docs.google.com/spreadsheets/d/1-LhCdj8BiY5BM9t21f5hwBJnyNi_KVPcgQC7bG25CU8/edit
todo_spreadsheet_id = {'d&j': '1-LhCdj8BiY5BM9t21f5hwBJnyNi_KVPcgQC7bG25CU8',
                       'dad': ''}
# https://docs.google.com/spreadsheets/d/1tpiEu-Ou2cVi-382xIwEhLu6BAUOVmH8n8co0At1X8w/edit
# https://docs.google.com/spreadsheets/d/1qW7__jgRA0J2-2InfZp3v4mn0Nh-zxGb4anl5JP72a4/edit
money_spreadsheet_id = {'d&j': '1tpiEu-Ou2cVi-382xIwEhLu6BAUOVmH8n8co0At1X8w',
                        'dad': '1qW7__jgRA0J2-2InfZp3v4mn0Nh-zxGb4anl5JP72a4'}
# https://docs.google.com/spreadsheets/d/1zgXcb0T7TEaLu0ilcmvuU6fmX_FFoduy_n4HCvo6ekI/edit
diary_spreadsheet_id = '1zgXcb0T7TEaLu0ilcmvuU6fmX_FFoduy_n4HCvo6ekI'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_spreadsheet_service() -> Resource:
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    return service


def get_id(user_group):
    service = get_spreadsheet_service()
    range_name = 'TODO!F1'
    result_read = service.spreadsheets().values().get(
        spreadsheetId=todo_spreadsheet_id.get(user_group), range=range_name).execute()
    id_list = result_read.get('values', [])
    return int(id_list[0][0])


def add_task(user_group, task_name, due_date="", category="", link=""):
    if category == "":
        category = "Дела"

    service = get_spreadsheet_service()

    task_id = get_id(user_group)

    newvalues = [
        ["", due_date, category, link, task_name, task_id + 1]
    ]
    body = {
        'values': newvalues
    }
    range_name = 'TODO!A1:F'
    value_input_option = 'USER_ENTERED'
    result_write = service.spreadsheets().values().append(
        spreadsheetId=todo_spreadsheet_id.get(user_group), range=range_name,
        valueInputOption=value_input_option, body=body).execute()
    return result_write


def task_list(user_group):
    service = get_spreadsheet_service()
    range_name = 'TODO!A1:F'

    result_read = service.spreadsheets().values().get(
        spreadsheetId=todo_spreadsheet_id.get(user_group), range=range_name).execute()
    return result_read.get('values', [])


def find_task_addr_by_id(tasks: list, task_id: int) -> [int, None]:
    for row in range(3, len(tasks)):
        if int(tasks[row][5]) == task_id:
            return row + 1
    return None


def finish_task(user_group, task_id):
    service = get_spreadsheet_service()

    tasks = task_list(user_group)
    row_address = find_task_addr_by_id(tasks, task_id)

    if row_address is None:
        raise ValueError("Task is not found")

    # check if it not set done
    if tasks[row_address - 1][0] != "":
        return False

    newvalues = [
        ["*"]
    ]
    body = {
        'values': newvalues
    }
    range_name = 'TODO!A{}'.format(row_address)
    value_input_option = 'USER_ENTERED'

    result_write = service.spreadsheets().values().update(
        spreadsheetId=todo_spreadsheet_id.get(user_group), range=range_name,
        valueInputOption=value_input_option, body=body).execute()
    return result_write


def delete_task(user_group, task_id):
    service = get_spreadsheet_service()

    tasks = task_list(user_group)
    row_address = find_task_addr_by_id(tasks, task_id)

    if row_address is None:
        raise ValueError("Task is not found")

    body = {
        "requests": [
            {
                "deleteDimension": {
                    "range": {
                        "startIndex": row_address - 1,
                        "endIndex": row_address,
                        "dimension": "ROWS",
                        "sheetId": 1386834576
                    }
                }
            }
        ]
    }

    result_write = service.spreadsheets().batchUpdate(
        spreadsheetId=todo_spreadsheet_id.get(user_group),
        body=body).execute()
    return result_write


def get_categories(user_group):
    service = get_spreadsheet_service()
    range_name = 'categories!A:A'

    result_read = service.spreadsheets().values().get(
        spreadsheetId=money_spreadsheet_id.get(user_group), range=range_name).execute()

    return [i[0] for i in result_read.get('values', [])]  # flattening


def diary(text, date):
    service = get_spreadsheet_service()
    newvalues = [
        [date, text]
    ]
    body = {
        'values': newvalues
    }
    range_name = 'Sheet1!A1:B'
    value_input_option = 'USER_ENTERED'

    result_write = service.spreadsheets().values().append(
        spreadsheetId=diary_spreadsheet_id,
        range=range_name,
        valueInputOption=value_input_option,
        body=body).execute()
    return result_write


def money(user_group, expense_name, amount, category, date):
    if category == "":
        category = "I don't know"

    service = get_spreadsheet_service()
    newvalues = [
        [date, category, amount, expense_name]
    ]
    body = {
        'values': newvalues
    }
    range_name = 'money_flow!A1:D'
    value_input_option = 'USER_ENTERED'

    result_write = service.spreadsheets().values().append(
        spreadsheetId=money_spreadsheet_id.get(user_group), range=range_name,
        valueInputOption=value_input_option, body=body).execute()
    row = result_write.get("updates").get('updatedRange')
    logging.info("Added an expense '{expense_name}' to the range '{row}'".format(expense_name=expense_name, row=row))
    return row


def money_list(user_group):
    service = get_spreadsheet_service()
    range_name = 'money_flow!A2:D'

    result_read = service.spreadsheets().values().get(
        spreadsheetId=money_spreadsheet_id.get(user_group), range=range_name).execute()
    return result_read.get('values', [])


def edit_expense(user_group, row_address, date, category, value, aim):
    service = get_spreadsheet_service()

    if row_address is None:
        raise ValueError("Expense is not found")

    newvalues = [
        [date, category, value, aim]
    ]
    body = {
        'values': newvalues
    }
    range_name = 'money_flow!A{}:D{}'.format(row_address, row_address)
    value_input_option = 'USER_ENTERED'

    result_write = service.spreadsheets().values().update(
        spreadsheetId=money_spreadsheet_id.get(user_group), range=range_name,
        valueInputOption=value_input_option, body=body).execute()
    return result_write


def get_sheet_id_by_title(user_group: str, title: str) -> [int, None]:
    """ Retrieves sheet id by title of a sheet

    for a correct we obtain an id:
    >>> get_sheet_id_by_title('d&j', 'TODO')
    1386834576

    For incorrect we obtain None:
    >>> get_sheet_id_by_title('d&j', 'sjdhff')
    None
    """

    service = get_spreadsheet_service()

    result_write = service.spreadsheets().get(
        spreadsheetId=todo_spreadsheet_id.get(user_group)).execute()

    for sheet in result_write.get('sheets'):
        if sheet.get('properties').get('title') == title:
            return int(sheet.get('properties').get('sheetId'))
    return None


# if __name__ == '__main__':
#     # money_list('d&j')
#     # a = delete_row('d&j', 'TODO!A75:E75')
#     # print(a)
#
#     service = get_spreadsheet_service()
#
#     a = get_sheet_id_by_title('d&j', 'TODO')
#
#     print(a)


