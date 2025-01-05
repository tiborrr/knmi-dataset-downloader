import httpx
import re

async def get_anonymous_api_key() -> str:
    """Fetch the anonymous API key from the KNMI developer portal.
    
    Returns:
        str: The anonymous API key
    
    Raises:
        ValueError: If the API key cannot be found on the page
        httpx.HTTPError: If there is an error fetching the page
        httpx.TimeoutException: If the request times out after 5 seconds
    """
    url = "https://developer.dataplatform.knmi.nl/open-data-api"
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        
        pattern = r'eyJ[a-zA-Z0-9_-]+'
        match = re.search(pattern, response.text)
        
        if not match:
            raise ValueError("Could not find API key on the page")
            
        return match.group(0) 