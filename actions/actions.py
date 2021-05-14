# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import re
import psycopg2
from configparser import ConfigParser
config = ConfigParser()
config.read('database.config')

def create_con(config):
    
    DBNAME = config['RDS']['DBNAME']
    HOST = config['RDS']['HOST']
    PORT = config['RDS']['PORT']
    USER = config['RDS']['USER']
    PASSWORD = config['RDS']['PASSWORD']

    con=psycopg2.connect(f"dbname={DBNAME} host={HOST} port={PORT} user={USER} password={PASSWORD}")
    return con

con = create_con(config)

class ActionStockPrice(Action):
    '''List stocks with specified condition (if any)'''
    def name(self) -> Text:
        return "action_stock_price"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        date = '2020/07/31' #tracker.get_slot('date')
        cur =  con.cursor()
        stock = tracker.get_slot('stock_type')

        if re.search(r"HK|hk", stock):
        	currency = 'HKD'
        	cur.execute(f'''
                    SELECT stock, close_ FROM stock
                    WHERE stock = '{stock}' AND date_ = '{date}'
                    LIMIT 1
                ''')
        else:
        	currency = 'USD'
        	cur.execute(f'''
                    SELECT stock, "Close" FROM chatbot.us_stock
                    WHERE stock = '{stock}' AND Date = '{date}'
                    LIMIT 1
                ''')

        res = cur.fetchall()
        print(res)
        if res is not None:
            if len(res)>=0:
                dispatcher.utter_message(text=f"Found the following {stock} with price:")
                for r in res:
                    dispatcher.utter_message(text=f"{r[0]} -  {currency} {r[1]}")
        else:
            dispatcher.utter_message(text="Not Found")
        cur.close()
        return []