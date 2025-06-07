
import requests
import  csv
from models import Output, Lists
import json
from config import OPENAI_API_KEY, OUTPUT_CSV_FILE, API_ENDPOINT, SCRAPER_ENDPOINT, MAX_WORKERS
def getInfo(urls: str) -> str:
    """
    Send the URL list to the backend API, and the backend website will batch process all URLs and output the results.

    Args:
        urls (str): The URL list string to retrieve.

    Returns:
        str: The result string.

    Raises:
        ValueError: If the input URL is None or invalid.
    """
    if not urls:
        raise ValueError("URL cannot be empty")
    urls = urls.split(",")
    res = ""
    try:
        for i in range(0, len(urls), MAX_WORKERS):
            data = {"url": ",".join(map(str, urls[i:i + MAX_WORKERS]))}
            response = requests.post(SCRAPER_ENDPOINT, json=data)
            if response.status_code == 200:
                result = response.json()
                res += result.get("result", {})
            else:
                print(response.json())
                raise ValueError(f"Failed to retrieve data. Status code: {response.status_code}")

        return res
    except requests.RequestException as e:
        print(f"Request Error: {e}")
        raise ValueError("Failed to retrieve data from the API")
    except Exception as e:
        print(f"Error: {e}")
        raise ValueError("An unexpected error occurred")


def write_to_csv(data: str) -> None:
    """
    Write JSON data to a CSV file. Handles both:
    - {"lists": [{...}, {...}]} format
    - [{...}, {...}] format (direct array of items)

    Args:
        data: JSON string containing the data to be written to CSV
        filename: The name/path of the CSV file to create/overwrite

    Raises:
        ValueError: If the JSON data is invalid or doesn't match the expected schema
    """
    filename = OUTPUT_CSV_FILE
    try:
        # Parse JSON string into Python object
        json_data = json.loads(data)

        # Determine if we have a direct array or the Lists structure
        if isinstance(json_data, list):
            # Direct array case - wrap in Lists model
            lists_data = Lists(lists=json_data)
        else:
            # Standard case with "lists" key
            lists_data = Lists(**json_data)

        # Extract field names from the Output model
        fieldnames = list(Output.__annotations__.keys())

        # Open the CSV file for writing
        with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            # Write the header row
            writer.writeheader()

            # Write each Output object as a row in the CSV
            for output in lists_data.lists:
                writer.writerow(output.dict())

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON data: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error: {str(e)}")




def getSubpage(url: str) -> str:
    """
       Retrieve all subpage links from the URL and output a list string, for example: https://www.pkhotelsandresorts.com/portfolio#$propertyid=new-york-hilton-midtown.

       Args:
           url (str): URL of the portfolio page

       Returns:
          str: json string of individual property URLs
    """
    if not url:
        raise ValueError("URL cannot be empty")

    try:
        data = {
            "prompt": f"Retrieve all hotel detailed information page links from {url}, but due to the website's anti crawling technology, you cannot obtain the correct sub links from the webpage. You can refer to the following format and output a list string,for example: https://www.pkhotelsandresorts.com/portfolio#$propertyid=new-york-hilton-midtown."}
        response = requests.post(API_ENDPOINT, json=data)
        if response.status_code == 200:
            result = response.json()
            return result.get("result", {})
        else:
            raise ValueError(f"Failed to retrieve data. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Request Error: {e}")
        raise ValueError("Failed to retrieve data from the API")
    except Exception as e:
        print(f"Error: {e}")
        raise ValueError("An unexpected error occurred")
