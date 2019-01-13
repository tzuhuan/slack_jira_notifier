import random
import time
import os
import db_manager
from slack_notifier import SlackNotifier

DB_FILE_PATH = "case.db"
TESTING_CASE_ID_RANGE = 10

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
 
def update_database(case_list):
    print(">> update_database")
    
    db_conn = db_manager.create_db(DB_FILE_PATH)
    db_conn.row_factory = dict_factory
    cursor = db_conn.cursor()
    
    cursor.execute("SELECT * FROM case_table")
    existing_case_list = cursor.fetchall()
    cursor.close()
    #print(existing_case_list)
 
    for case in case_list:
        handle_case(db_conn, existing_case_list, case)
 
    db_conn.commit()
    db_conn.close()    
    
def handle_case(db_conn, existing_case_list, arrival_case):
    print(">> handle_case")
    
    existing_case = find_existing_case(existing_case_list, arrival_case)
    
    if existing_case == None:
        insert_case_into_db(db_conn, arrival_case)
    else:
        update_existing_case(db_conn, existing_case, arrival_case)
    
def find_existing_case(existing_case_list, arrival_case):
    print(">> find_existing_case")
    
    for existing_case in existing_case_list:
        if existing_case["id"] == arrival_case["id"]:
            print("found existing case {}".format(existing_case))
            return existing_case
            
    return None
    
def insert_case_into_db(db_conn, arrival_case):
    print(">> insert_case_into_db")
    
    send_notification = False
    
    if arrival_case["label"] != "":
        send_notification = True
    
    cursor = db_conn.cursor()
    data = (arrival_case["id"], arrival_case["priority"], arrival_case["label"], send_notification, False)
    cursor.execute("INSERT INTO case_table VALUES (?, ?, ?, ?, ?)", data)
    cursor.close()

def update_existing_case(db_conn, existing_case, arrival_case):
    print(">> update_existing_case")
    
    send_notification = False
    if (arrival_case["label"] != "") and (existing_case["label"] != arrival_case["label"]):
        print("Label changed {} -> {}".format(existing_case["label"], arrival_case["label"]))
        send_notification = True
        
    cursor = db_conn.cursor()
    data = (arrival_case["priority"], arrival_case["label"], send_notification, False, arrival_case["id"])
    cursor.execute("UPDATE case_table SET priority = ?, label = ?, notify = ?, already_notified = ? WHERE id = ?", data)
    cursor.close()
    
def send_notification_to_slack():
    print(">> send_notification_to_slack")
    
    db_conn = db_manager.create_db(DB_FILE_PATH)
    db_conn.row_factory = dict_factory
    cursor = db_conn.cursor()
    
    cursor.execute("SELECT * FROM case_table WHERE notify = 1")
    case_notification_list = cursor.fetchall()
    cursor.close()
    print(case_notification_list)
    
    slack = SlackNotifier(SLACK_CHANNEL)
    
    db_conn.commit()
    db_conn.close() 
    
def main():
    case_list = fetch_jira_cases()
    print(case_list)
    
    update_database(case_list)
    send_notification_to_slack()
        

if __name__ == '__main__':
    main()