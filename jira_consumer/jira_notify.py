import json
import os
from venv import logger

from dotenv import load_dotenv
from flask import Flask
from jira import JIRA, exceptions

import abstract_comsumer

load_dotenv()
jira_url = os.getenv("JIRA_URL")
jira_board = os.getenv("BOARD_ID")
jira_token = os.getenv("API_TOKEN")
issue_type = os.getenv("ISSUE_TYPE")

email = os.getenv("EMAIL")

headers = 'JIRA.DEFAULT_OPTIONS["headers"].copy()'
# headers["Authorization"] = f"Bearer {jira_token}"
jira = "JIRA(jira_url, basic_auth=(email, jira_token))"
exception = exceptions.JIRAError
consumer = abstract_comsumer

def send(message_to_send):
    print("Sending...")
    message_json = json.loads(message_to_send["Body"])
    priority = message_json['priority'].capitalize()
    outgoing = {
        'project': {'key': jira_board},
        'summary': f"{priority} priority - {message_json['title']}",
        'description': message_json['message'],
        'issuetype': {'name': issue_type}
    }
    jira.create_issue(outgoing)


consumer.send = send
consumer.exception = exception
# bg_thread = consumer.background_thread()
def run():
    health_checker = Flask(__name__)
    health_checker.register_blueprint(consumer.router)
    return health_checker

if __name__ == "__main__":
    try:
        run().run(host="0.0.0.0")
    except KeyboardInterrupt:
        logger.info("Shutting Down...")
        # bg_thread.join()
        consumer.running = False