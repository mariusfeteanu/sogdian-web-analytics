import json
import os

import boto3


client = boto3.client('firehose', region_name=os.environ['AWS_REGION'])

def lambda_handler(event, context):
    client.put_record(
        DeliveryStreamName='deliver-web-analytics',
        Record={'Data': (json.dumps(event) + u'\n').encode('utf-8')})
