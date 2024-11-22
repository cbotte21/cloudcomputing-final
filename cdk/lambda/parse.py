import json
from bs4 import BeautifulSoup
import re

def parse_line(line):
    j = json.loads(line)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(j["content"], 'html.parser')

    # Extract title
    title = soup.title.string if soup.title else None

    # Extract meta description
    description = None
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        description = meta_desc.get('content')

    # Extract author
    author = None
    meta_author = soup.find('meta', attrs={'name': 'author'})
    if meta_author:
        author = meta_author.get('content')

    # Extract published date
    published_date = None
    time_tag = soup.find('time')
    if time_tag and time_tag.has_attr('datetime'):
        published_date = time_tag['datetime']

    
    # Extract content (assuming it's within a specific tag, e.g., div with class 'content')
    content_div = soup.find('div', class_='content')
    content = clean_text(content_div.get_text(separator=' ').strip() if content_div else None)
    content = []
    for header in ['h1', 'h2', 'h3']:
        for h in soup.find_all(header):
            clean = clean_text(h.get_text(separator=' ', strip=True))
            if clean is not None:
                content.append(clean)            
    if content == []:
        content = None

    #data base rds 
    res = {
        "author": author,
        "content": content,
        "description": description,
        "published_date": published_date,
        "title": title,
        "url": j["url"]
    }

    return (res, is_valid(res))

def clean_text(text):
    if text is None:
        return None

    # Remove all punctuation
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    # Remove all numbers (optional, depending on your needs)
    text = re.sub(r'\d+', '', text)  # Remove numbers if necessary
    # Convert to lowercase
    text = text.lower()
    # Split the text into words and remove extra whitespace
    words = text.split()
    
    # List of stopwords (common words to remove, you can customize this)
    stopwords = {
        'the', 'is', 'in', 'and', 'to', 'a', 'of', 'for', 'on', 'with',
        'this', 'that', 'it', 'are', 'as', 'at', 'by', 'an', 'be', 'but', 
        'not', 'or', 'from', 'all', 'if', 'which', 'when', 'you', 'your', 
        'they', 'their', 'my', 'he', 'she', 'that', 'there', 'what', 'so', 
        'we', 'us', 'his', 'her', 'its', 'can', 'will', 'would', 'should'
    }
    
    # Remove stopwords
    cleaned_words = [word for word in words if word not in stopwords]
    
    # Join the cleaned words back into a single string
    cleaned_text = ' '.join(cleaned_words)
    res = cleaned_text.strip()
    
    return res if res != '' else None   # Remove leading/trailing whitespace

def is_valid(res):
    return res.get("url") is not None and res.get("content") is not None and res.get("title") is not None