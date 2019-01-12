import json
import requests
import datetime
import threading
import time
import random
from queue import Queue
import os

g_webhook_url = os.environ["slack_channel_webhook_url"]

RUN = True
NOTIFIER_SLEEP = 10
FETCHER_SLEEP = 5

class SlackNotifier:    
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.headers = {"Content-type": "application/json"}
        
    def set_webhook_url(self, url):
        self.webhook_url = url
        
    def send_case(self, case):
        message = self.build_message(case)
        json_message = json.dumps(message, indent=4)
        #print(json_message)
        r = requests.post(self.webhook_url, data=json_message, headers=self.headers)
        #print(r.text)
        
    def build_message(self, case):    
        message = {}
        message["text"] = "<{}|{}> *{}*\n>Priority: {}\n>Label: {}\n>Assignee: {}".format(case["URL"],
                                                                                          case["ID"],
                                                                                          case["Title"],
                                                                                          case["Priority"],
                                                                                          case["Label"],
                                                                                          case["Assignee"])
    
        return message    

class SlackNotifierThread(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.slack_notifier = SlackNotifier(g_webhook_url)
        self.queue = queue
        
    def run(self):
        while True:
            time.sleep(NOTIFIER_SLEEP)
            count = 0              
            while not self.queue.empty():
                case = self.queue.get()       
                if case == None:
                    print("case None")
                    return
                
                print("Sending...")
                self.slack_notifier.send_case(case)
                count = count + 1
                self.queue.task_done()
            
            print("Sent {} cases".format(count))            
        
class JiraCaseFetcherThread(threading.Thread):
    def __init__(self, event, queue):
        threading.Thread.__init__(self)
        self.event = event
        self.queue = queue
        pass
        
    def run(self):
        while not self.event.is_set():
            self.queue.join()
            print("Fetching...")
            case_list = self.query_jira_cases()
            for case in case_list:
                self.queue.put(case)
            
            print("Fetching ends...")
            time.sleep(FETCHER_SLEEP);
            
            
    def query_jira_cases(self):  
        case_list = []
        
        for i in range(random.choice(range(3))):
            case = {}
            num = random.choice(range(10000))
            case_id = "SEG-{}".format(num)
            case["ID"] = case_id
            case["Title"] = "Windows Server BSOD"
            case["URL"] = "https://www.google.com.tw"
            case["Priority"] = "P0"
            case["Label"] = "DSA-General"
            case["Assignee"] = "patrick_tang"
            case_list.append(case)
        
        print(len(case_list))
        return case_list

def main():

    #slack_notifier = SlackNotifier(g_webhook_url)
    
    #case_list = []
    #case = {}
    #case["ID"] = "SEG-00000"
    #case["Title"] = "Windows Server BSOD"
    #case["URL"] = "https://www.google.com.tw"
    #case["Priority"] = "P0"
    #case["Label"] = "DSA-General"
    #case["Assignee"] = "patrick_tang"
    #case_list.append(case)
    
    #for case in case_list:
    #    slack_notifier.send_case(case)
        
    #return
    
    try:
        case_list = []
        event = threading.Event()
        queue = Queue()
        
        fetcher = JiraCaseFetcherThread(event, queue)
        notifier = SlackNotifierThread(queue)
        
        fetcher.start()
        notifier.start()
        
        while True:
           time.sleep(30);        
           print("heartbeat")
        
    except:
        print("exception") 
    
    
    event.set()
    fetcher.join()
    
    queue.put(None)
    notifier.join()
    
    print("main exit")

if __name__ == '__main__':
    main()