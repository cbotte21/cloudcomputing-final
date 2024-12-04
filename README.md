# cloudcomputing-final

This can also be found at... [text](https://github.com/cbotte21/cloudcomputing-final)

A fully functional search engine. Upon deploying, will scrape pages from the internet, process them, and supply them to the front end for querying.
## Overview of the project
The web crawler project is an AWS-based system designed to efficiently gather, process, and serve website data. It consists of the following components:
	1.	Web Scrapers (EC2 Instances):
	•	These instances run web scraping tools to crawl and collect raw HTML data from websites.
	•	Scraped data is preprocessed and temporarily stored in ElastiCache for caching and S3 for long-term storage.
	2.	ElastiCache (Redis):
	•	Acts as an in-memory cache for recently crawled pages or metadata.
	•	Ensures faster retrieval of frequently accessed or recently scraped websites, avoiding redundant scrapes.
	3.	S3 Bucket:
	•	Stores raw HTML files and processed data for archival and future reference.
	4.	Lambda Function:
	•	Processes the raw HTML files stored in S3, extract files and write to RDS PostGres database.
	5.	RDS (Relational Database):
	•	Stores structured search data, making it queryable by the web application.
	6.	Web Application (EC2):
	•	Frontend that allows users to search and retrieve website data.
	•	Queries RDS for search results and integrates with other components for dynamic content.

Key Flow:
	1.	Users interact with the web application to search or retrieve website data.
	2.	If the data is cached in ElastiCache, it is retrieved instantly.
	3.	Newly scraped data is processed, stored in S3/RDS, and cached in ElastiCache for future use.

## Important notes / deployment

- Before deploying the app, change the SSH key name to a valid EC2 SSH key in your region. Or delete the ssh key logic entirely.

- Navigate to cdk/, install python packages and run cdk deploy.
