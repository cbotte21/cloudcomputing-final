from urllib.parse import urlparse, urlunparse

def fixUrl(nextUrl, prevUrl):
    nextUrl.replace("void(0)", "")
    parNext = urlparse(nextUrl)
    parPrev = urlparse(prevUrl)

    if(not parPrev.path or parPrev.params): return None

    if(parNext.netloc == ''):
        newUrl = (
            parPrev.scheme, 
            parPrev.netloc,
            parNext.path,
            '',
            parNext.query,
            ''
        )
        return urlunparse(newUrl)
    
    return nextUrl