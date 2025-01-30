import json
import os
import boto3

from jira import JIRA, exceptions

from dotenv import load_dotenv

load_dotenv()
queue = os.getenv("MID_PRIORITY_QUEUE")
access_id = os.getenv("AWS_ACCESS_KEY_ID")
access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")
jira_url = os.getenv("JIRA_URL")
jira_board = os.getenv("BOARD_ID")
jira_token = os.getenv("API_TOKEN")
issue_type = os.getenv("ISSUE_TYPE")

email = os.getenv("EMAIL")

headers = JIRA.DEFAULT_OPTIONS["headers"].copy()
headers["Authorization"] = f"Bearer {jira_token}"
jira = JIRA(jira_url, basic_auth=(email, jira_token))

sqs = boto3.client("sqs",
                   region_name=aws_region,
                   aws_access_key_id=access_id,
                   aws_secret_access_key=access_key)

running = True

def get_from_queue():
    response = sqs.receive_message(
        QueueUrl=queue,
        MaxNumberOfMessages=1,
        MessageAttributeNames=["All"],
        VisibilityTimeout=0,
        WaitTimeSeconds=20
    )

    if "Messages" not in response:
        return None

    message = response["Messages"][0]
    return message


def notify_jira(message):
    print("Sending...")
    message_json = json.loads(message["Body"])
    priority = message_json['priority'].capitalize()
    outgoing = {
        'project': {'key': jira_board},
        'summary': f"{priority} priority - {message_json['title']}",
        'description': message_json['message'],
        'issuetype': {'name': issue_type}
    }
    jira.create_issue(outgoing)


def delete(message):
    receipt_handle = message["ReceiptHandle"]
    sqs.delete_message(
        QueueUrl=queue,
        ReceiptHandle=receipt_handle
    )


def run():
    global running
    running = True
    while running:
        message = get_from_queue()
        if message:
            try:
                notify_jira(message)
            except exceptions.JIRAError as ex:
                print(ex)
                continue
            delete(message)

if __name__ == "__main__":
    run()