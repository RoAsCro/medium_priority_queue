import os
import boto3

from jira import JIRA

from dotenv import load_dotenv

load_dotenv()
queue = os.getenv("MID_PRIORITY_QUEUE")
access_id = os.getenv("AWS_ACCESS_KEY_ID")
access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")
jira_url = os.getenv("JIRA_URL")
jira_board = os.getenv("BOARD_ID")
jira_token = os.getenv("API_TOKEN")

email = os.getenv("EMAIL")

headers = JIRA.DEFAULT_OPTIONS["headers"].copy()
headers["Authorization"] = f"Bearer {jira_token}"
jira = JIRA(jira_url, basic_auth=(email, jira_token))

sqs = boto3.client("sqs",
                   region_name=aws_region,
                   aws_access_key_id=access_id,
                   aws_secret_access_key=access_key)

def get_message():
    response = sqs.receive_message(
        QueueUrl=queue,
        MaxNumberOfMessages=1,
        MessageAttributeNames=["All"],
        VisibilityTimeout=0,
        WaitTimeSeconds=20
    )

    if "Messages" not in response:
        return

    message = response["Messages"][0]
    receipt_handle = message["ReceiptHandle"]

    sqs.delete_message(
        QueueUrl=queue,
        ReceiptHandle=receipt_handle
    )
    notify_jira(message)

def notify_jira(message):
    print(message["Body"])


# get_message()
print(jira.project(jira_board))
print(jira.create_issue({
    'project': {'key': jira_board},
    'summary': 'New issue from jira-python',
    'description': 'Look into this one',
    'issuetype': {'name': 'Task'},
}))