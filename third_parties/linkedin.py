import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()


def _recursively_remove_empty_values(item):
    """
    Recursively remove keys from dictionaries if their values are None,
    an empty dictionary, or an empty list.
    Cleans dictionaries within lists as well.
    """
    if isinstance(item, dict):
        cleaned_dict = {}
        for key, value in item.items():
            cleaned_value = _recursively_remove_empty_values(value)
            # Add key only if cleaned_value is not one of the "empty" markers
            if (
                cleaned_value is not None
                and cleaned_value != {}
                and cleaned_value != []
            ):
                cleaned_dict[key] = cleaned_value
        return cleaned_dict
    elif isinstance(item, list):
        cleaned_list = []
        for list_item in item:
            cleaned_list_item = _recursively_remove_empty_values(list_item)
            # Add item to list only if it's not one of the "empty" markers
            # This will also filter out None/[]/{} from within lists if they were standalone
            if (
                cleaned_list_item is not None
                and cleaned_list_item != {}
                and cleaned_list_item != []
            ):
                cleaned_list.append(cleaned_list_item)
        return cleaned_list
    else:
        return item


def scrape_linkedin_profile(
    linkedin_profile_url: str, mock: bool = False, api: str = "scrapin"
):
    """Scrape LinkedIn profile information."""

    if mock:
        linkedin_profile_url = "https://gist.githubusercontent.com/emarco177/859ec7d786b45d8e3e3f688c6c9139d8/raw/5eaf8e46dc29a98612c8fe0c774123a7a2ac4575/eden-marco-scrapin.json"
        response = requests.get(linkedin_profile_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
        else:
            raise Exception(f"Failed to fetch mock data: {response.status_code}")
    elif api == "scrapin":
        # Debug: Check if API key is loaded
        scrapin_key = os.getenv("SCRAPIN_API_KEY")
        print(f"Scrapin API Key loaded: {'Yes' if scrapin_key else 'No'}")
        
        # Use Scrapin.io API with correct authentication and parameter names
        api_endpoint = "https://api.scrapin.io/enrichment/profile"
        
        # Use X-API-Key header and linkedInUrl parameter (based on test results)
        headers = {"X-API-Key": scrapin_key}
        params = {"linkedInUrl": linkedin_profile_url}
        
        response = requests.get(api_endpoint, params=params, headers=headers, timeout=10)
        data = response.json()

    elif api == "proxycurl":
        api_endpoint = "https://nubela.co/proxycurl/api/v2/linkedin"
        header_dic = {"Authorization": f"Bearer {os.environ.get('PROXYCURL_API_KEY')}"}
        response = requests.get(
            api_endpoint,
            headers=header_dic,
            params={"url": linkedin_profile_url},
            timeout=10,
        )
        data = response.json()

    if response.status_code != 200:
        error_data = {}
        try:
            error_data = response.json()
        except json.JSONDecodeError:
            pass
        raise Exception(
            f"Failed to fetch LinkedIn profile (status {response.status_code}): {error_data.get('error', response.text)}"
        )

    # Print the raw data to see what image fields are available
    print("=== DEBUG: Raw API Response Keys ===")
    print(f"Available keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
    
    # Look for image fields in the person object
    person_data = data.get('person', {}) if isinstance(data, dict) else {}
    if person_data:
        print("=== DEBUG: Person Object Keys ===")
        print(f"Person keys: {list(person_data.keys())}")
        
        # Look for the specific image field names we found
        print("=== DEBUG: Image Fields Found in Person Data ===")
        if 'photoUrl' in person_data:
            print(f"photoUrl: {person_data['photoUrl']}")
        if 'backgroundUrl' in person_data:
            print(f"backgroundUrl: {person_data['backgroundUrl']}")

    # Recursively remove empty values
    cleaned_data = _recursively_remove_empty_values(data)
    return cleaned_data


# if __name__ == "__main__":
#     profile_data = scrape_linkedin_profile(
#         linkedin_profile_url="https://www.linkedin.com/in/ebsmartin/", mock=True
#     )
#     print(json.dumps(profile_data, indent=4))
