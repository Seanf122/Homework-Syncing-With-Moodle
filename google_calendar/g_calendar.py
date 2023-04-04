from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GCalendar:
    def __init__(self):
        # If modifying these scopes, delete the file token.json.
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.creds = self.get_credentials()
        self.service = build('calendar', 'v3', credentials=self.creds)
        # self.token_file = 'google_calendar/g_calendar_token.json'
        

    def get_credentials(self, token_file = 'google_calendar/g_calendar_token.json'):
        creds = None
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'google_calendar/credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)

            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        return creds


    def create_HW(self, calendar_id, moodle_data, index, reminder=True):
        try:
            event = {
            'summary': moodle_data['assessmentName'][index],
            'description': moodle_data['assessmentDetail'][index],
            'location': moodle_data['assessmentUrl'][index], 
            'start': {
                'date': moodle_data['assessmentDueDate'][index],
                # 'dateTime': moodle_data['assessmentDueTime'][index],
                'timeZone': 'UTC+8',
            },
            'end': {
                'date': moodle_data['assessmentDueDate'][index],
                # 'dateTime': moodle_data['assessmentDueTime'][index],
                'timeZone': 'UTC+8',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                {'method': 'popup', 'minutes': 24 * 60 * 2 + 120},
                ],
            },  
            }
            if not reminder:
                event.pop('reminders')

            event = self.service.events().insert(calendarId=calendar_id, body=event).execute()
            print('Event created: %s' % (event.get('htmlLink')))

        except HttpError as error:
            print('An error occurred: %s' % error)


    def update_HW(self, calendar_id, moodle_data, index, reminder, event_id=''):
        try:
            event = {
            'summary': moodle_data['assessmentName'][index],
            'description': moodle_data['assessmentDetail'][index],
            'location': moodle_data['assessmentUrl'][index], 
            'start': {
                'date': moodle_data['assessmentDueDate'][index],
                'dateTime': moodle_data['assessmentDueTime'][index],
                'timeZone': 'UTC+8',
            },
            'end': {
                'date': moodle_data['assessmentDueDate'][index],
                'dateTime': moodle_data['assessmentDueTime'][index],
                'timeZone': 'UTC+8',
            },
            }
            if reminder:
                event['reminders'] = {
                'useDefault': False,
                'overrides': [
                {'method': 'popup', 'minutes': 24 * 60 * 2 + 120},
                ],
            }

            event = self.service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
            print('Event updated: %s' % (event.get('htmlLink')))

        except HttpError as error:
            print('An error occurred: %s' % error)


    def create_summary(self):
        calendar = {
        'summary': 'HW',
        'timeZone': 'UTC+8', 
        'colorId': 'Mango', 
        "description": 'This is a calendar synking all the homeworks on Moodle.\n it will be updated every 6 hours.' 
    }
        created_calendar = self.service.calendars().insert(body=calendar).execute()
        print ('the created calendar ID is = ', created_calendar['id'])


    def get_calendar_id(self):
        page_token = None
        while True:
            calendar_list = self.service.calendarList().list(pageToken=page_token).execute()
            for i, calendar_list_entry in enumerate(calendar_list['items']):
                print ('calendar_list_entry = ', calendar_list_entry['summary'])
                if calendar_list_entry['summary'] == 'HW':
                    return calendar_list_entry['id']
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                self.create_summary()


    # def get_event_id(creds, calendar_id):
    #     service = build('calendar', 'v3', credentials=creds)
    #     events_result = service.events().list(calendarId=calendar_id, maxResults=2500, singleEvents=True, orderBy='startTime').execute()
    #     events = events_result.get('items', [])
    #     for event in events:
    #         print(event['id'])
    #         print(event['description'])


    def split_descriptions(descriptions):
        for i in range(len(descriptions)):
            descriptions[i] = descriptions[i].split('\n', 1)[0]


    def get_exsisting_HW(self, calendar_id):
        try:

            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            curr_semester = datetime.datetime(2022, 2, 14).isoformat() + 'Z'
            print('Getting the upcoming 100 events')
            events_result = self.service.events().list(calendarId=calendar_id, timeMin=curr_semester,
                                                maxResults=100, singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                print('No upcoming events found.')
                return '', '', ''
            summary = []
            descriptions = []
            event_id = []
            for event in events:
                #print(event['summary'])
                summary.append(event['summary'])
                descriptions.append(event['description'])
                event_id.append(event['id'])
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(start, event['summary'], '\n', event['description'])
            return summary, descriptions, event_id

        except HttpError as error:
            print('An error occurred: %s' % error)




def main():
    '''
    for testing
    '''
    gCalendar = GCalendar()
    gCalendar.get_credentials()
    calendar_id = gCalendar.get_calendar_id()
    # create_HW(creds, '國文小考測驗', '2023-04-01', calendar_id, 'Test')
    items = gCalendar.get_exsisting_HW(calendar_id)                        #can't use one line for loop


if __name__ == '__main__':
    main()

