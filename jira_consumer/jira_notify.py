import json
import os
import logging
from dotenv import load_dotenv
from jira import JIRA, exceptions

from sqs_consumer.abstract_consumer import AbstractConsumer

load_dotenv()
jira_url = os.getenv("JIRA_URL")
jira_board = os.getenv("BOARD_ID")
jira_token = os.getenv("API_TOKEN")
issue_type = os.getenv("ISSUE_TYPE")
email = os.getenv("EMAIL")

headers = JIRA.DEFAULT_OPTIONS["headers"].copy()
headers["Authorization"] = f"Bearer {jira_token}"
exception = exceptions.JIRAError
class JiraConsumer(AbstractConsumer):
    def __init__(self):
        super().__init__()
        self.exception = exception
        self.jira = JIRA(jira_url, basic_auth=(email, jira_token))

    def send(self, message_to_send):
        logging.info("Sending...")
        message_json = json.loads(message_to_send["Body"])
        priority = message_json['priority'].capitalize()

        outgoing = {
            'project': {'key': jira_board},
            'summary': f"{priority} priority - {message_json['title']}",
            'description': message_json['message'],
            'issuetype': {'name': issue_type}
        }
        self.jira.create_issue(outgoing)

consumer = JiraConsumer()
run = consumer.run

if __name__ == "__main__":
    try:
        run().run(host="0.0.0.0")
    except KeyboardInterrupt:
        logging.info("Shutting Down...")
        consumer.bg_thread.join()
        consumer.running = False