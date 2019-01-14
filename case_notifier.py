import random
import time
import os

import db_manager
from slack_notifier import SlackNotifier
import tracelog
import case_attribute as CASE
import case_filter as Filter

DB_PATH = "case.db"
TESTING_CASE_ID_RANGE = 10

logger = tracelog.getLogger()

SLACK_CHANNEL = os.environ["slack_channel_webhook_url"]

def fetch_jira_cases():
    print(">> fetch_jira_cases")
    
    case_list = []
    id_list = [i for i in range(TESTING_CASE_ID_RANGE)]
    random.shuffle(id_list)
    
    for i in range(random.randint(1, 1)):
        case = {}
        case_id = "{}".format(id_list[i])
        case[CASE.ID] = case_id
        case[CASE.SUMMARY] = "Windows Server BSOD"
        case[CASE.URL] = "https://www.google.com.tw"
        case[CASE.PRIORITY] = db_manager.get_random_priority()
        case[CASE.PROBLEM_DOMAIN] = db_manager.get_random_label()
        case[CASE.SEG_OWNER] = "patrick_tang"
        case_list.append(case)
    
    return case_list
    
def main():
    logger.info(">> CaseNotifier STARTS!!")
    fetched_case_list = fetch_jira_cases()
    print(fetched_case_list)

    notification_list = Filter.filter_cases(DB_PATH, fetched_case_list)
    #update_database(fetched_case_list)
    #send_notification_to_slack()
    
    slack = SlackNotifier(SLACK_CHANNEL)
    for case in notification_list:
        slack.send_case(case)
        logger.info("sent: {}".format(case))

    logger.info("sending notification completed")        
    logger.info("<< CaseNotifier ENDS!!")
        

if __name__ == '__main__':
    main()