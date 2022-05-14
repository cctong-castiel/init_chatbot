# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.knowledge_base.storage import InMemoryKnowledgeBase
from rasa_sdk.knowledge_base.actions import ActionQueryKnowledgeBase
from rasa_sdk.knowledge_base.utils import (
    SLOT_OBJECT_TYPE,
    SLOT_LAST_OBJECT_TYPE,
    SLOT_ATTRIBUTE,
    reset_attribute_slots,
    SLOT_MENTION,
    SLOT_LAST_OBJECT,
    SLOT_LISTED_OBJECTS,
    get_object_name,
    get_attribute_slots,
)
import random
import re
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# import psycopg2
# from configparser import ConfigParser

# config = ConfigParser()
# config.read("database.config")


# def create_con(config):

#     DBNAME = config["RDS"]["DBNAME"]
#     HOST = config["RDS"]["HOST"]
#     PORT = config["RDS"]["PORT"]
#     USER = config["RDS"]["USER"]
#     PASSWORD = config["RDS"]["PASSWORD"]

#     con = psycopg2.connect(
#         f"dbname={DBNAME} host={HOST} port={PORT} user={USER} password={PASSWORD}"
#     )
#     return con


# con = create_con(config)


class ActionStockPrice(Action):
    """List stocks with specified condition (if any)"""

    def name(self) -> Text:
        return "action_stock_price"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # date = "2020/07/31"  # tracker.get_slot('date')
        # cur = con.cursor()
        # stock = tracker.get_slot("stock_type")

        # if re.search(r"HK|hk", stock):
        #     currency = "HKD"
        #     cur.execute(
        #         f"""
        #             SELECT stock, close_ FROM stock
        #             WHERE stock = '{stock}' AND date_ = '{date}'
        #             LIMIT 1
        #         """
        #     )
        # else:
        #     currency = "USD"
        #     cur.execute(
        #         f"""
        #             SELECT stock, "Close" FROM chatbot.us_stock
        #             WHERE stock = '{stock}' AND Date = '{date}'
        #             LIMIT 1
        #         """
        #     )

        # res = cur.fetchall()
        # print(res)
        # if res is not None:
        #     if len(res) >= 0:
        #         dispatcher.utter_message(
        #             text=f"Found the following {stock} with price:"
        #         )
        #         for r in res:
        #             dispatcher.utter_message(text=f"{r[0]} -  {currency} {r[1]}")
        # else:
        #     dispatcher.utter_message(text="Not Found")
        # cur.close()

        dispatcher.utter_message(text="ask stock")

        return []


class MyKnowledgeBaseAction(ActionQueryKnowledgeBase):
    def __init__(self):
        knowledge_base = InMemoryKnowledgeBase("actions/memories/data.json")

        knowledge_base.set_representation_function_of_object(
            "hotel", lambda obj: obj["name"] + " (" + obj["city"] + ")"
        )

        knowledge_base.set_representation_function_of_object(
            "restaurant", lambda obj: obj["name"] + "_" + str(obj["id"])
        )

        super().__init__(knowledge_base)

class ActionKnowledgeBaseGetAttribute(MyKnowledgeBaseAction):
    def __init__(self):
        super().__init__()

    def name(self) -> Text:
        return "action_knowledgebase_get_attribute"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        object_type = tracker.get_slot(SLOT_OBJECT_TYPE)
        last_object_type = tracker.get_slot("knowledge_base_last_object_type")
        attribute = tracker.get_slot("attribute")

        logger.info(f"object_type: {object_type}, last_object_type: {last_object_type}, attribute: {attribute}")

        new_request = object_type != last_object_type
        logger.info(f"new_request: {new_request}")

        if not object_type:
            logger.info("no object_type")
            # object type always needs to be set as this is needed to query the
            # knowledge base
            dispatcher.utter_message(response="utter_ask_rephrase")
            return []

        if not attribute or new_request:
            logger.info("no attribute or new_request")
            return await self._query_objects(dispatcher, object_type, tracker)
        elif attribute:
            logger.info("has attribute")
            return await self._query_attribute(
                dispatcher, object_type, attribute, tracker
            )

        dispatcher.utter_message(response="utter_ask_rephrase")
        return []
        