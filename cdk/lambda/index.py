import os
import json
from parse import parse_line
from aws_lambda_powertools.utilities.streaming.s3_object import S3Object
import psycopg2  # PostgreSQL adapter for Python
from psycopg2.extras import DictCursor  # For Dict-like cursor behavior

BUCKET_NAME = "searchengine-data"

def handler(event, context):
    # Log the event to check its structure
    print("Received event:", event)
    
    # Extract the bucket name and file key from the S3 event
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    
    print(f"Processing file from bucket: {bucket}, key: {key}")
    
    # Process the S3 file
    s3 = S3Object(bucket=bucket, key=key)
    connection = create_rds_connection()
    
    try:
        for line in s3.readlines():
            parsed = parse_line(line)
            if parsed[1]:  # Is valid
                insert_into_rds(connection, parsed[0])
    finally:
        connection.close()

    return {
        "message": f"File {key} processed successfully."
    }

def create_rds_connection():
    """Creates and returns a connection to the PostgreSQL RDS database using environment variables."""
    try:
        connection = psycopg2.connect(
            host=os.environ["PG_HOST"],
            port=int(os.environ["PG_PORT"]),
            user=os.environ["PG_USER"],
            password=os.environ["PG_PASSWORD"],
            dbname=os.environ["PG_DATABASE"],
            cursor_factory=DictCursor  # Optional: enables dict-like row access
        )
        print("PostgreSQL RDS connection established.")
        return connection
    except Exception as e:
        print("Failed to connect to PostgreSQL RDS:", e)
        raise

def insert_into_rds(connection, document):
    """Inserts a document into the PostgreSQL RDS database, creating the table if it does not exist."""
    try:
        with connection.cursor() as cursor:
            # Create the table if it does not exist
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS your_table_name (
                id SERIAL PRIMARY KEY,
                author VARCHAR(255),
                content TEXT,
                description TEXT,
                published_date VARCHAR(30),
                title VARCHAR(255),
                url VARCHAR(255) UNIQUE
            )
            """
            cursor.execute(create_table_sql)

            # Insert the document
            insert_sql = """
            INSERT INTO your_table_name (author, content, description, published_date, title, url) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (document['author'], document['content'], document['description'], document['published_date'], document['title'], document['url']))
            connection.commit()
            print(f"Insert successful for URL: {document['url']}")
    except Exception as e:
        print(f"Error inserting into PostgreSQL RDS for URL: {document['url']}", e)
        raise