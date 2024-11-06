import boto3
import json
from parse import parse_line
import boto3
import concurrent.futures
import os

session = boto3.Session()
url = 'https://search-searchengine-zvepn4hr2yyugmei4fqnxxhqaq.us-east-2.es.amazonaws.com/search/_doc/'  # Replace with your endpoint and index

BUCKET_NAME = 'searchengine-data'
DIRECTORY = "scraped"

def main():
    files = get_s3_object_names()
    print("Files to process:", files)

    # Ensure the output directory exists
    os.makedirs('scraped', exist_ok=True)

    # Use ThreadPoolExecutor to process files in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_file, files)

def process_file(file):
    res = []
    print(f"Processing file: {file}")
    for line in stream_s3_file(file):
        parsed = parse_line(line)
        if parsed[1]:  # Is valid
            res += json.dumps(parsed[0])
    res = json.dumps(res)
    # Create a JSON filename for saving results
    output_file_path = f'scraped/{file.split("/")[-1]}'  # Use the original filename
    print(f"Writing results to: {output_file_path}")

    # Write JSON data to file
    with open(output_file_path, 'w') as json_file:
        json.dump(res, json_file, indent=4)  # Write the result as JSON

def get_s3_object_names():
    s3_client = boto3.client('s3')
    object_names = []

    # Use paginator for large buckets
    paginator = s3_client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=BUCKET_NAME):
        if 'Contents' in page:
            for obj in page['Contents']:
                object_names.append(obj['Key'])  # Append object name to the list

    return object_names

def stream_s3_file(key):
    # Create an S3 client
    s3_client = boto3.client('s3')
    
    # Get the object from S3
    s3_object = s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
    
    # Get the body of the object
    body = s3_object['Body']
    
    # Stream the file as lines
    for line in body.iter_lines():
        # Decode the line if necessary and strip any whitespace
        yield line.decode('utf-8')

if __name__ == "__main__":
    main()