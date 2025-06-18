from langchain_tavily import TavilySearch
import os
import docx

def get_profile_url_tavily(name: str) -> str:
    """
    Looks up a LinkedIn profile by name using Tavily Search.
    
    Args:
        name: Search query that may contain name + job title + company (e.g., "Matt software engineer Nickel5")
    
    Returns:
        LinkedIn profile URL or descriptive error message
    """
    try:
        search = TavilySearch(api_key=os.environ.get("TAVILY_API_KEY"))
        
        # Use the search query exactly as provided - don't modify it
        print(f"🔍 Tavily searching for: '{name}'")
        results = search.run(f"{name}")
        
        if not results:
            return f"No search results found for '{name}'"
        
        # Handle different result formats from Tavily
        linkedin_urls = []
        
        # Case 1: Results is a list of dictionaries
        if isinstance(results, list):
            for result in results:
                if isinstance(result, dict):
                    url = result.get('url', '')
                    if 'linkedin.com/in/' in url:
                        linkedin_urls.append(url)
        
        # Case 2: Results is a string containing URLs
        elif isinstance(results, str):
            import re
            # Extract LinkedIn URLs from the string
            urls = re.findall(r'https?://(?:www\.)?linkedin\.com/in/[^\s\)\]<>"\']+', results)
            linkedin_urls.extend(urls)
        
        # Return the first LinkedIn URL found
        if linkedin_urls:
            clean_url = linkedin_urls[0].rstrip('.,;)')  # Clean trailing punctuation
            print(f"✅ Found LinkedIn URL: {clean_url}")
            return clean_url
        
        # If no LinkedIn URLs found, return the raw results for the agent to process
        print(f"⚠️ No LinkedIn URLs found in results, returning raw data")
        return str(results)
        
    except Exception as e:
        error_msg = f"Error searching for '{name}': {str(e)}"
        print(f"❌ Search failed: {error_msg}")
        return error_msg

def extract_text_from_word(file_path: str) -> str:
    """
    Extracts text from Word documents.
    Only tool we actually need since Gemini handles everything else natively!
    """
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to extract text from Word document: {str(e)}")

def process_file_for_gemini(file_path: str) -> dict:
    """
    Determines how to process files for Gemini.
    Most files can be sent directly to Gemini!
    """
    if not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")
    
    file_extension = os.path.splitext(file_path)[1].lower()
    
    # Gemini native formats - send directly
    if file_extension in ['.mp3', '.wav', '.m4a', '.flac', '.aiff', '.aac', '.ogg']:
        return {
            'type': 'audio',
            'file_path': file_path,
            'send_to_gemini': True
        }
    
    elif file_extension == '.pdf':
        return {
            'type': 'pdf', 
            'file_path': file_path,
            'send_to_gemini': True
        }
    
    elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
        return {
            'type': 'image',
            'file_path': file_path,
            'send_to_gemini': True
        }
    
    elif file_extension == '.txt':
        with open(file_path, 'r', encoding='utf-8') as file:
            return {
                'type': 'text',
                'content': file.read(),
                'send_to_gemini': False  # Just text content
            }
    
    # Only Word docs need tool processing
    elif file_extension in ['.docx', '.doc']:
        return {
            'type': 'word',
            'file_path': file_path,
            'send_to_gemini': False,  # Need to extract text first
            'content': extract_text_from_word(file_path)
        }
    
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

