import os
from abc import ABC, abstractmethod

import boto3
from dotenv import load_dotenv


class AbstractConsumer(ABC):
    load_dotenv()
    # Environment variables
    queue = os.getenv("QUEUE")
    access_id = os.getenv("AWS_ACCESS_KEY_ID")
    access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    exception = Exception

    sqs = boto3.client("sqs",
                       region_name="us-east-1",
                       aws_access_key_id=access_id,
                       aws_secret_access_key=access_key
                       )

    running = False

    def get_from_queue(self):

        response = self.sqs.receive_message(
            QueueUrl=self.queue,
            MaxNumberOfMessages=1,
            MessageAttributeNames=["All"],
            VisibilityTimeout=0,
            WaitTimeSeconds=20
        )

        if "Messages" not in response:
            return None

        message = response["Messages"][0]

        return message

    @abstractmethod
    def send(self, message_to_send):
        pass


    def delete(self, message):
        receipt_handle = message["ReceiptHandle"]

        self.sqs.delete_message(
            QueueUrl=self.queue,
            ReceiptHandle=receipt_handle
        )


    def run(self):
        self.running = True
        while self.running:
            message = self.get_from_queue()
            if message:
                try:
                    self.send(message)
                except self.exception as ex:
                    print(ex)
                    continue
                self.delete(message)

