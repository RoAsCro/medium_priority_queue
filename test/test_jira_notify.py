import threading
import time

import boto3
import pytest

from moto import mock_aws

import jira_consumer
jira_notify = jira_consumer.jira_notify
consumer = jira_notify.consumer

default_jira_method  = jira_notify.send

message_body = '{"priority": "high", "title": "message title", "message": "this is a message body"}'
received_message = None

@mock_aws
def test_get_message():
    sqs = prepare_aws()
    sqs[0].send_message(QueueUrl=sqs[1],
                         DelaySeconds=0,
                         MessageBody=message_body)

    retrieved_message = consumer.get_from_queue()

    assert retrieved_message is not None

@mock_aws
def test_delete_message():
    sqs = prepare_aws()
    mock_sqs = sqs[0]
    queue = sqs[1]
    mock_sqs.send_message(QueueUrl=queue,
                         DelaySeconds=0,
                         MessageBody=message_body)

    retrieved_message = consumer.get_from_queue()
    consumer.delete(retrieved_message)

    assert "Message" not in mock_sqs.receive_message(
        QueueUrl=queue,
        MaxNumberOfMessages=1,
        MessageAttributeNames=["All"],
        VisibilityTimeout=0,
        WaitTimeSeconds=20
    )

@mock_aws
def test_no_message():
    prepare_aws()

    retrieved_message = consumer.get_from_queue()

    assert retrieved_message is None


@mock_aws
def prepare_aws():
    mock_sqs = boto3.client("sqs", region_name='us-east-1')
    queue = mock_sqs.create_queue(QueueName="team")['QueueUrl']
    consumer.sqs = mock_sqs
    consumer.queue = queue
    return mock_sqs, queue

def timer(seconds):
    time.sleep(seconds)
    consumer.running = False

def notify_jira_stub(message):
    global received_message
    received_message = message["Body"]
    consumer.running = False

@pytest.fixture(autouse=True)
def before_each():
    consumer.running = False
    jira_notify.bg_thread.join()
    consumer.send = default_jira_method
    global received_message
    received_message = None

@mock_aws
def test_process_without_jira():
    sqs = prepare_aws()
    mock_sqs = sqs[0]
    queue = sqs[1]
    consumer.send = notify_jira_stub
    mock_sqs.send_message(QueueUrl=queue,
                          DelaySeconds=0,
                          MessageBody=message_body)
    timer_thread = threading.Thread(target=timer, args=[20])  # Ensure test doesn't run forever if it fails
    timer_thread.start()
    consumer.running = True
    jira_notify.consumer.process()
    consumer.running = False
    global received_message
    assert (received_message is not None  # Message was received
            and "Message" not in mock_sqs.receive_message(  # Message was deleted
                QueueUrl=queue,
                MaxNumberOfMessages=1,
                MessageAttributeNames=["All"],
                VisibilityTimeout=0,
                WaitTimeSeconds=20
            ))

