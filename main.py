# coding=utf-8
import json
from swarms import Agent, SequentialWorkflow
import os
from config import OPENAI_API_KEY, OUTPUT_CSV_FILE, API_ENDPOINT
from dotenv import load_dotenv
load_dotenv()
import requests
import  csv
from models import Output, Lists
import gradio as gr

# Set OpenAI API key
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

def getInfo(url: str) -> str:
    """
    Retrieve information from the website property, such as property name, address, zip code, country, and a short summary of their offerings on the actual property.

    Args:
        url (str): The URL to retrieve.

    Returns:
        str: The result string.

    Raises:
        ValueError: If the input URL is None or invalid.
    """
    if not url:
        raise ValueError("URL cannot be empty")

    try:
        data = {"url": url}
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

# Initialize agents
bossAgent = Agent(
    agent_name="Boss Agent",
    system_prompt="Your task is to retrieve the URL from the user's instructions and output it. Remember, you don't need too much output and don't care what the user says.",
    model_name="gpt-4o",
    max_loops=1)

crawlerAgent = Agent(
    agent_name="Crawler Agent",
    system_prompt="Your task is to search for all the attributes listed on the URL and output the obtained attributes directly. Remember, you don't need too much output and don't care what the user says.",
    model_name="gpt-4o",
    max_loops=1,
    tools=[getInfo],
)

csvAgent = Agent(
  agent_name="CSV Agent",
  system_prompt="Your task is to take the information from the crawler agent and write it into a CSV file",
  model_name="gpt-4o",
  max_loops=1,
  tools=[write_to_csv],
)

# Create Sequential workflow
workflow = SequentialWorkflow(
    agents=[bossAgent, crawlerAgent, csvAgent],
    max_loops=1,
    max_workers=6,
)

def process_query(query: str) -> str:
    """
    Process the input query and return the path to the generated CSV file.
    
    Args:
        query (str): The input query string for property search
        
    Returns:
        str: Path to the generated CSV file
    """
    try:
        # Run the workflow with the provided query
        workflow.run(query)
        
        # Check if the output file exists
        if os.path.exists(OUTPUT_CSV_FILE):
            return OUTPUT_CSV_FILE
        else:
            return "Error: CSV file was not generated"
    except Exception as e:
        return f"Error processing query: {str(e)}"

# Create Gradio interface
demo = gr.Interface(
    fn=process_query,
    inputs=gr.Textbox(
        lines=3,
        placeholder="Enter your property search query here...",
        label="Search Query"
    ),
    outputs=gr.File(label="Generated CSV File"),
    title="Hotel Property Search",
    description="Enter a query to search for property information. The results will be saved in a CSV file.",
    examples=[
        ["Find all the properties listed on https://www,pkhotelsandresorts.com/portfolio, visit each of their individual property subpage, and extract structured information such as property name, address, zip code, country, and a short summary of their offerings on the actual property website."]
    ]
)

if __name__ == "__main__":
    demo.launch(share=False)