import sys
from os import environ

import boto3

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

import logging


logging.getLogger().setLevel(logging.INFO)
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'json_input'])
json_input = args['json_input']
job_name = args['JOB_NAME']

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(job_name, args)

def get_parquet_output(json_input):
    path_parts = json_input.split('/')
    convert_bucket = path_parts[2].replace('-delivery-', '-convert-')
    stream_name = path_parts[3]
    batch_id = '-'.join(path_parts[8][:-3].split('-')[10:])
    partitions = 'landed_year={}/landed_month={}/landed_day={}/landed_hour={}/landed_batch_id={}'.format(
        path_parts[4], path_parts[5], path_parts[6], path_parts[7], batch_id)
    convert_path = '/'.join([
        's3:', '',
        convert_bucket,
        stream_name,
        partitions])
    return convert_path

parquet_output = get_parquet_output(json_input)

logging.info("Will try to read from %s.", json_input)
df = spark.read.json(json_input)

logging.info("Will try to write to %s.", parquet_output)
df.write.parquet(parquet_output, mode='overwrite')

region_name = environ.get('NM_HOST').split('.')[1]
glue_client = boto3.client('glue', region_name=region_name)
glue_client.start_crawler(Name='web-analytics-events-crawler')

job.commit()
