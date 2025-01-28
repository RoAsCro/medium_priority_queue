import os
from os import access

import boto3
import jira

from dotenv import load_dotenv

load_dotenv()
queue = os.getenv("MID_PRIORITY_QUEUE")
access_id = os.getenv("ACCESS_ID")
access_key = os.getenv("ACCESS_KEY")

sqs = boto3.client("sqs",
                   region_name="us-east-1",
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

get_message()