import os
import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

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
# https://docs.google.com/spreadsheets/d/1tpiEu-Ou2cVi-382xIwEhLu6BAUOVmH8n8co0At1X8w/edit
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


def get_spreadsheet_service():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    return service


def add_task(user_group, task_name, due_date="", category="", link=""):
    if category == "":
        category = "Дела"

    service = get_spreadsheet_service()
    newvalues = [
        ["", due_date, category, link, task_name]
    ]
    body = {
        'values': newvalues
    }
    range_name = 'TODO!A1:E'
    value_input_option = 'USER_ENTERED'
    result_write = service.spreadsheets().values().append(
        spreadsheetId=todo_spreadsheet_id.get(user_group), range=range_name,
        valueInputOption=value_input_option, body=body).execute()
    return result_write


def list_all():
    service = get_spreadsheet_service()
    range_name = 'TODO!A1:E'

    result_read = service.spreadsheets().values().get(
        spreadsheetId=todo_spreadsheet_id.get(user_group), range=range_name).execute()
    return result_read.get('values', [])


def get_categories():
    service = get_spreadsheet_service()
    range_name = 'categories!A1:A2'

    result_read = service.spreadsheets().values().get(
        spreadsheetId=todo_spreadsheet_id.get(user_group), range=range_name).execute()
    return result_read.get('values', [])


def main():
    """
    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """
    service = get_spreadsheet_service()

    newvalues = [
        ["Item", "Cost", "Stocked", "Ship Date"],
        ["Wheel", "$20.50", "4", "3/1/2016"],
        ["Door", "$15", "2", "3/15/2016"],
        ["Engine", "$100", "1", "30/20/2016"],
        ["Totals", "=SUM(B2:B4)", "=SUM(C2:C4)", "=MAX(D2:D4)"]
    ]

    body = {
        'values': newvalues
    }

    range_name = 'Sheet1!A1:D'
    value_input_option = 'USER_ENTERED'
    result_write = service.spreadsheets().values().append(
        spreadsheetId=todo_spreadsheet_id, range=range_name,
        valueInputOption=value_input_option, body=body).execute()
    print(result_write)

    result_read = service.spreadsheets().values().get(
        spreadsheetId=todo_spreadsheet_id, range=range_name).execute()
    values = result_read.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Here is the content of the table:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print(row)


if __name__ == '__main__':
    main()


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
    return result_write
