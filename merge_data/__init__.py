# from moodle_scraper.moodle import Moodle
from merge_data.moodle_scraper import getherData
from merge_data.google_calendar.g_calendar import GCalendar
from common.utils import Utils
import json

class MergeData:
    def __init__(self, google_token, userId, pwd):
        self.userId = userId
        self.pwd = pwd
        self.gCalendar = GCalendar(google_token)
        self.utils = Utils()
        self.calendar_id = ''
        self.creds = None
        self.moodle_data = None
        self.event_id = []
        self.gHW_names = []
        self.gHW_descriptions = []

    def getGoogleInfo(self):
        '''
        get google calendar id
        '''
        self.gCalendar.get_credentials()
        self.calendar_id, self.newEventList = self.gCalendar.get_calendar_id()


    def packData(self):
        '''
        get data from moodle
        '''
        self.moodle_data = getherData(self.userId, self.pwd)

        '''
        get data from google calendar
        '''
        self.gHW_names, self.gHW_descriptions, self.event_id = self.gCalendar.get_exsisting_HW(self.calendar_id)
        self.checkGHWname = [name.replace('✅', '') for name in self.gHW_names]

    def processingHW(self):
        for i in range(len(self.moodle_data['assessmentName'])):
            if self.moodle_data['assessmentDueDate'][i] == '':
                print(self.moodle_data['assessmentDueDate'][i], 'has no due date')
                continue
            hWname = self.moodle_data['assessmentName'][i]
            checkHWname = self.moodle_data['assessmentName'][i].replace('✅', '')

            reminder = self.utils.setReminder(hWname)

            if checkHWname not in self.checkGHWname:
                try:
                    self.gCalendar.synkHW(self.calendar_id, self.moodle_data, i, reminder)
                except Exception as e:
                    print(hWname + ' has an error : ', e)
                finally:
                    continue

            # if not self.newEventList and not self.utils.checkDate(self.moodle_data, i):
            #     continue
            index = self.utils.findIndex(checkHWname, self.checkGHWname)
            #TODO: check if the due date is different
            if self.utils.sameDescription(self.moodle_data, self.gHW_descriptions, i):
                print('executing update_HW')
                try:
                    self.gCalendar.synkHW(self.calendar_id, self.moodle_data, i, reminder, self.event_id[index])
                except Exception as e:
                    print(hWname + ' has an error : ', e)


    def storeJsonFile(self):
        with open('archive/data.json', 'w') as f:
            json.dump(self.moodle_data, f, indent=4, ensure_ascii=False)


    def run(self):
        self.getGoogleInfo()
        self.packData()
        self.processingHW()
        # self.storeJsonFile()