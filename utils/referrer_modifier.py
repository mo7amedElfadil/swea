from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


def modify_referrer_lang(referrer, new_lang):
    """Extract the 'lang' from the referrer and replace it"""
    
    if referrer:
        # Parse the referrer URL
        parsed_url = urlparse(referrer)
        
        # Extract the query parameters as a dictionary
        query_params = parse_qs(parsed_url.query)
        
        # Modify the 'lang' parameter (replace or add if missing)
        query_params['lang'] = [new_lang]

        # Rebuild the query string with the updated parameters
        new_query = urlencode(query_params, doseq=True)

        # Rebuild the full URL with the updated query string
        new_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment
        ))

        return new_url
    return '/'
