from opensearchpy import OpenSearch
from collections import defaultdict

# Initialize OpenSearch client
client = OpenSearch(
    hosts=[{'host': 'search-searchengine-zvepn4hr2yyugmei4fqnxxhqaq.us-east-2.es.amazonaws.com', 'port': 443}],  # Adjust host and port as necessary
    http_auth=('admin', ')3*8*FiLHM2yVHS'),  # Adjust authentication as necessary
    use_ssl = True,
)

index_name = 'search'  # Replace with your index name

def get_all_documents(index):
    documents = []
    response = client.search(
        index=index,
        body={
            "query": {
                "match_all": {}
            },
            "size": 10000  # Adjust size based on expected number of documents
        },
        scroll='2m'  # Keep the scroll context alive for 2 minutes
    )
    
    # Initial scroll ID
    scroll_id = response['_scroll_id']
    
    # Collect documents
    while True:
        documents.extend(response['hits']['hits'])
        if len(response['hits']['hits']) == 0:
            break
        response = client.scroll(scroll_id=scroll_id, scroll='2m')
    
    return documents

def delete_duplicates(documents):
    url_map = defaultdict(list)
    
    # Group documents by URL
    for doc in documents:
        url = doc['_source'].get('url')
        if url:
            url_map[url].append(doc)

    # Iterate through the grouped documents and delete duplicates
    for url, docs in url_map.items():
        # Keep one copy
        docs_to_delete = docs[1:]  # Keep the first one and delete the rest
        for doc in docs_to_delete:
            doc_id = doc['_id']
            print(f'Deleting document ID: {doc_id} with URL: {url}')
            client.delete(index=index_name, id=doc_id)

def main():
    # Get all documents
    documents = get_all_documents(index_name)
    
    # Delete duplicates
    delete_duplicates(documents)

if __name__ == '__main__':
    main()
