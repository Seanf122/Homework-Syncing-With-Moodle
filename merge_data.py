from moodle_scraper.moodle import Moodle
from google_calendar.g_calendar import GCalendar #create_HW, update_HW, get_exsisting_HW, get_credentials, get_calendar_id
from utils import Utils #checkDate, setReminder, findIndex, sameDescription
import json

class MergeData:
    def __init__(self, moodle_creds_file, google_token_file):
        self.moodle = Moodle(moodle_creds_file)
        self.gCalendar = GCalendar(google_token_file)
        self.utils = Utils()
        self.calendar_id = ''
        self.creds = None
        self.moodle_data = None
        self.event_id = []
        self.gHW_names = []
        self.gHW_descriptions = []

    def getGoogleInfo(self):
        self.gCalendar.get_credentials()
        self.calendar_id, self.newEventList = self.gCalendar.get_calendar_id()


    def packData(self):
        moodle_data = self.moodle.get_data()
        moodle_data = self.moodle.data_process(moodle_data)
        self.moodle_data = moodle_data
        # with open('data.json', 'r') as f:
        #     moodle_data = json.load(f)
        #     self.moodle_data = moodle_data

        self.gHW_names, self.gHW_descriptions, self.event_id = self.gCalendar.get_exsisting_HW(self.calendar_id)
        self.checkGHWname = [name.replace('✅', '') for name in self.gHW_names]

    def processingHW(self):
        for i in range(len(self.moodle_data['assessmentName'])):
            hWname = self.moodle_data['assessmentName'][i]
            checkHWname = self.moodle_data['assessmentName'][i].replace('✅', '')

            reminder = self.utils.setReminder(hWname)

            if checkHWname not in self.checkGHWname:
                try:
                    self.gCalendar.create_HW(self.calendar_id, self.moodle_data, i, reminder)
                except Exception as e:
                    print(hWname + ' has a error : ', e)
                continue

            if not self.newEventList and not self.utils.checkDate(self.moodle_data, i):
                continue
            index = self.utils.findIndex(checkHWname, self.checkGHWname)
            if self.utils.sameDescription(self.moodle_data, self.gHW_descriptions, i):
                print('executing update_HW')
                self.gCalendar.update_HW(self.calendar_id, self.moodle_data, i, reminder, self.event_id[index])