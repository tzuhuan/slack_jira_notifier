import db_manager
import case_attribute as CASE
import tracelog

logger = tracelog.getLogger()

def filter_cases(db_path, fetched_case_list):
    db_conn = db_manager.create_db(db_path)
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM case_table")
    saved_case_list = cursor.fetchall()
    cursor.close()
 
    for fetched_case in fetched_case_list:
        handle_case(db_conn, saved_case_list, fetched_case)
 
    notification_list = get_notification_list(db_conn)
 
    db_conn.commit()
    db_conn.close()
    
    return notification_list
    
    
def handle_case(db_conn, saved_case_list, fetched_case):
    logger.info("fetched case {}".format(fetched_case))
    saved_case = find_case_from_saved_list(saved_case_list, fetched_case)
    
    if saved_case == None:
        insert_case_into_db(db_conn, fetched_case)
    else:
        update_saved_case(db_conn, saved_case, fetched_case)
        
def find_case_from_saved_list(saved_case_list, target_case):    
    for saved_case in saved_case_list:
        if saved_case[CASE.ID] == target_case[CASE.ID]:
            logger.info("found saved case {}".format(saved_case))
            return saved_case
            
    return None
    
def insert_case_into_db(db_conn, fetched_case):    
    send_notification = False
    
    if fetched_case[CASE.PROBLEM_DOMAIN] != "":
        send_notification = True
    
    cursor = db_conn.cursor()
    data = (fetched_case[CASE.ID], fetched_case[CASE.URL], fetched_case[CASE.SUMMARY], fetched_case[CASE.PRIORITY], fetched_case[CASE.PROBLEM_DOMAIN], fetched_case[CASE.SEG_OWNER], send_notification, False)
    cursor.execute("INSERT INTO case_table VALUES (?, ?, ?, ?, ?, ?, ?, ?)", data)
    cursor.close()
    logger.info("insert case {}".format(fetched_case))

def update_saved_case(db_conn, saved_case, fetched_case):    
    send_notification = False
    if (fetched_case[CASE.PROBLEM_DOMAIN] != "") and (saved_case[CASE.PROBLEM_DOMAIN] != fetched_case[CASE.PROBLEM_DOMAIN]):
        logger.info("Problem domain changed '{}' -> '{}'".format(saved_case[CASE.PROBLEM_DOMAIN], fetched_case[CASE.PROBLEM_DOMAIN]))
        send_notification = True
    
    if not send_notification:
        logger.info("will not send notificaion for this case")
        
    cursor = db_conn.cursor()
    data = (fetched_case[CASE.URL], fetched_case[CASE.SUMMARY], fetched_case[CASE.PRIORITY], fetched_case[CASE.PROBLEM_DOMAIN], fetched_case[CASE.SEG_OWNER], send_notification, False, fetched_case["id"])
    cursor.execute("UPDATE case_table SET url = ?, summary = ?, Priority = ?, 'Problem domain' = ?, 'SEG Owner' = ?, notify = ?, already_notified = ? WHERE id = ?", data)
    cursor.close()
    
def get_notification_list(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM case_table WHERE notify = 1")
    notification_list = cursor.fetchall()

    print(notification_list)
    logger.info("{} cases to be sent...".format(len(notification_list)))
    
    # set "notify" as False
    for case in notification_list:
        data = (case[CASE.URL], case[CASE.SUMMARY], case[CASE.PRIORITY], case[CASE.PROBLEM_DOMAIN], case[CASE.SEG_OWNER], False, False, case[CASE.ID])
        cursor.execute("UPDATE case_table SET url = ?, summary = ?, Priority = ?, 'Problem domain' = ?, 'SEG Owner' = ?, notify = ?, already_notified = ? WHERE id = ?", data)
        
    cursor.close()
    return notification_list
    