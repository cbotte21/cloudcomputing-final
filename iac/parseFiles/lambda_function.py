import json
from parse import parse_line
from typing import Dict
from aws_lambda_powertools.utilities.streaming.s3_object import S3Object
from aws_lambda_powertools.utilities.typing import LambdaContext
import requests
from requests_aws4auth import AWS4Auth
import boto3

session = boto3.Session()
credentials = session.get_credentials()
region = 'us-east-2'  
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, 'es', session_token=credentials.token)
url = 'https://search-searchengine-zvepn4hr2yyugmei4fqnxxhqaq.us-east-2.es.amazonaws.com/search/_doc/'  # Replace with your endpoint and index

BUCKET_NAME = 'searchengine-data'

def lambda_handler(event, context):
    # Log the event to check its structure
    print("Received event:", event)
    
    files = event
    if not files:
        print("No files to process.")
        return
    
    print("Files to process:", files)
    for file in files:
        print(f"Processing file: {file}")
        
        s3 = S3Object(bucket=BUCKET_NAME, key=file)
        for line in s3.readlines():
            parsed = parse_line(line)
            if parsed[1]: # Is valid
                send_to_opensearch(parsed[0])

    return {
        "batchResults": files
    }

def send_to_opensearch(document):
    # Make the request to insert the documents
    response = requests.post(url, auth=awsauth, json=document)

    # Check the response
    if response.status_code == 200:
        print(f"Insert successful: {document['url']}")  # Use single quotes
    else:
        print(f"Error during insert: {document['url']}", response.status_code, response.text)  # Use single quotes