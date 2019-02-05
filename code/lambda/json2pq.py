import boto3

glue_client = boto3.client('glue')

def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        json_input = 's3://' + bucket + '/' + key
        glue_client.start_job_run(JobName='json-to-pq-first',
                                  Arguments={'--json_input': json_input})
