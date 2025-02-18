import json
import os
import boto3

from jira import JIRA, exceptions

from dotenv import load_dotenv

from abstract_comsumer import AbstractConsumer

load_dotenv()
class JiraConsumer(AbstractConsumer):
    jira_url = os.getenv("JIRA_URL")
    jira_board = os.getenv("BOARD_ID")
    jira_token = os.getenv("API_TOKEN")
    issue_type = os.getenv("ISSUE_TYPE")

    email = os.getenv("EMAIL")

    headers = JIRA.DEFAULT_OPTIONS["headers"].copy()
    headers["Authorization"] = f"Bearer {jira_token}"
    jira = JIRA(jira_url, basic_auth=(email, jira_token))
    exception = exceptions.JIRAError

    def send(self, message_to_send):
        print("Sending...")
        message_json = json.loads(message_to_send["Body"])
        priority = message_json['priority'].capitalize()
        outgoing = {
            'project': {'key': self.jira_board},
            'summary': f"{priority} priority - {message_json['title']}",
            'description': message_json['message'],
            'issuetype': {'name': self.issue_type}
        }
        self.jira.create_issue(outgoing)


def run():
    JiraConsumer().run()


if __name__ == "__main__":
    run()