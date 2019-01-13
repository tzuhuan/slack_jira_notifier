import random
import time
import os

import db_manager
from slack_notifier import SlackNotifier
import tracelog

DB_FILE_PATH = "case.db"
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
        case["id"] = case_id
        case["title"] = "Windows Server BSOD"
        case["url"] = "https://www.google.com.tw"
        case["priority"] = db_manager.get_random_priority()
        case["label"] = db_manager.get_random_label()
        case["assignee"] = "patrick_tang"
        case_list.append(case)
    
    return case_list
 
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d    
 
def update_database(fetched_case_list):
    print(">> update_database")
    
    db_conn = db_manager.create_db(DB_FILE_PATH)
    db_conn.row_factory = dict_factory
    cursor = db_conn.cursor()
    
    cursor.execute("SELECT * FROM case_table")
    existing_case_list = cursor.fetchall()
    cursor.close()
    #print(existing_case_list)
 
    for fetched_case in fetched_case_list:
        handle_case(db_conn, existing_case_list, fetched_case)
 
    db_conn.commit()
    db_conn.close()    
    
def handle_case(db_conn, existing_case_list, fetched_case):
    print(">> handle_case")
    
    print("arrival case {}".format(fetched_case))
    logger.info("arrival case {}".format(fetched_case))
    existing_case = find_existing_case(existing_case_list, fetched_case)
    
    if existing_case == None:
        insert_case_into_db(db_conn, fetched_case)
    else:
        update_existing_case(db_conn, existing_case, fetched_case)
    
def find_existing_case(existing_case_list, fetched_case):
    print(">> find_existing_case")
    
    for existing_case in existing_case_list:
        if existing_case["id"] == fetched_case["id"]:
            print("found existing case {}".format(existing_case))
            logger.info("found existing case {}".format(existing_case))
            return existing_case
            
    return None
    
def insert_case_into_db(db_conn, fetched_case):
    print(">> insert_case_into_db")
    
    send_notification = False
    
    if fetched_case["label"] != "":
        send_notification = True
    
    cursor = db_conn.cursor()
    ## ID URL TITLE PRIORITY LABEL ASSIGNEE NOTIFY ALREADY_NOTIFIED
    data = (fetched_case["id"], fetched_case["url"], fetched_case["title"], fetched_case["priority"], fetched_case["label"], fetched_case["assignee"], send_notification, False)
    cursor.execute("INSERT INTO case_table VALUES (?, ?, ?, ?, ?, ?, ?, ?)", data)
    cursor.close()
    logger.info("insert case {}".format(fetched_case))

def update_existing_case(db_conn, existing_case, fetched_case):
    print(">> update_existing_case")
    
    send_notification = False
    if (fetched_case["label"] != "") and (existing_case["label"] != fetched_case["label"]):
        print("Label changed '{}' -> '{}'".format(existing_case["label"], fetched_case["label"]))
        logger.info("label changed '{}' -> '{}'".format(existing_case["label"], fetched_case["label"]))
        send_notification = True
    
    if send_notification:
        cursor = db_conn.cursor()
        ## ID URL TITLE PRIORITY LABEL ASSIGNEE NOTIFY ALREADY_NOTIFIED
        data = (fetched_case["url"], fetched_case["title"], fetched_case["priority"], fetched_case["label"], fetched_case["assignee"], send_notification, False, fetched_case["id"])
        cursor.execute("UPDATE case_table SET url = ?, title = ?, priority = ?, label = ?, assignee = ?, notify = ?, already_notified = ? WHERE id = ?", data)
        cursor.close()
    else:
        logger.info("no need to update database")
    
def send_notification_to_slack(fetched_case_list):
    print(">> send_notification_to_slack")
    
    db_conn = db_manager.create_db(DB_FILE_PATH)
    db_conn.row_factory = dict_factory
    cursor = db_conn.cursor()
    
    cursor.execute("SELECT * FROM case_table WHERE notify = 1")
    notification_list = cursor.fetchall()
    cursor.close()
    print(notification_list)
    logger.info("{} cases to be sent...".format(len(notification_list)))
    
    slack = SlackNotifier(SLACK_CHANNEL)
    for case in notification_list:
        slack.send_case(case)
        logger.info("sent: {}".format(case))
    
    logger.info("sending notification completed")
    db_conn.commit()
    db_conn.close()
    
def main():
    fetched_case_list = fetch_jira_cases()
    print(fetched_case_list)
    
    update_database(fetched_case_list)
    send_notification_to_slack(fetched_case_list)
        

if __name__ == '__main__':
    main()