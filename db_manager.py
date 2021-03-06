import sqlite3
import os
import random

import tracelog
import case_attribute as CASE

DB_FILEPATH = "case.db"

CASE_PRIORITY = ["P0", "P1", "P2", "P2", "P3", "P3"]
CASE_LABEL = ["DSA", "DSM", "DSR", "DSAAS", ""]

logger = tracelog.getLogger()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d 

def create_db(db_path):
    logger.info("create db %s", db_path)
    need_to_create_table = False
    
    if not os.path.exists(db_path):
        need_to_create_table = True
        
    db_conn = sqlite3.connect(db_path)
    c = db_conn.cursor()
    
    if need_to_create_table:
        c.execute("CREATE TABLE case_table ( \
                         {} TEXT PRIMARY KEY NOT NULL, \
                         {} TEXT NOT NULL, \
                         {} TEXT NOT NULL, \
                         {} TEXT NOT NULL, \
                         '{}' TEXT NOT NULL, \
                         '{}' TEXT NOT NULL, \
                         {} Boolean NOT NULL, \
                         {} Boolean NOT NULL)".format(CASE.ID, CASE.URL, CASE.SUMMARY, CASE.PRIORITY, CASE.PROBLEM_DOMAIN, CASE.SEG_OWNER, CASE.NOTIFY, CASE.ALREADY_NOTIFIED))
        c.close()
        db_conn.commit()
    
    db_conn.row_factory = dict_factory
    return db_conn

def get_random_priority():
    return CASE_PRIORITY[random.randint(0, len(CASE_PRIORITY) - 1)]
    
def get_random_label():
    return CASE_LABEL[random.randint(0, len(CASE_LABEL) - 1)]
    
def get_random_update_time():
    return str(random.randint(0, 10000))
    
def create_testing_db_data(db):
    c = db.cursor()
    
    id_list = [i for i in range(50)]
    random.shuffle(id_list)

    for i in range(50):
        data = (id_list[i], get_random_priority(), "", False, False)
        c.execute("INSERT INTO case_table VALUES (?, ?, ?, ?, ?)", data);
    
    db.commit()
    c.close()

def test(db):
    
    # create testing data
    
    case_list_to_check = []
    #for i in range(5):
    case = {}
    case["id"] = random.randint(0, 20)
    case["priority"] = get_random_priority()
    case["label"] = get_random_label()
    #case["update_time"] = get_random_update_time()
    print(case)
    
    #case_list_to_check.append(case)    
    #print(case_list_to_check)
    
    c = db.cursor()
    
    c.execute("SELECT * FROM case_table WHERE ID=?", (case["id"],))
    case_in_db = c.fetchone()
    print(case_in_db)
    
    if case_in_db == None:
        # new case
        
        notify = False
        #if case["priority"] == "P0" or case["priority"] == "P1":
        #    notify = True
        
        data = (case["id"], case["priority"], case["label"], notify, False)
        c.execute("INSERT INTO case_table VALUES (?, ?, ?, ?, ?)", data)
        
        print("add case = {}, priority = {}, label = {}, notify = {}".format(case["id"], case["priority"], case["label"], notify))
    else:
        notify = False
        
        if case["label"] != "" and case["label"] != case_in_db[2]:
            print(case_in_db[2], ">>", case["label"])
            notify = True
        
        #if case["priority"] == "P0" or case["priority"] == "P1":
        #    notify = True
            
        print("update case = {}, priority = {}, label = {}, notify = {}".format(case["id"], case["priority"], case["label"], notify))
        
    db.commit()
    c.close()
    
def main():
    db = create_db(DB_FILEPATH)
    print(db)
    
    create_testing_db_data(db)
    #test(db)
    
    db.close()
    
if __name__ == '__main__':
    main()