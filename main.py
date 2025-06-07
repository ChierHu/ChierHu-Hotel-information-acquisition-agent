# coding=utf-8
import json
import multiprocessing

from swarms import MixtureOfAgents, Agent, SequentialWorkflow, ConcurrentWorkflow
import os
from config import OPENAI_API_KEY, OUTPUT_CSV_FILE, API_ENDPOINT
from dotenv import load_dotenv
load_dotenv()
import asyncio
import gradio as gr
import numpy as np
from tools import getSubpage, getInfo, write_to_csv

# Set OpenAI API key
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

# Initialize agents
bossAgent = Agent(
    agent_name="Boss Agent",
    system_prompt="Your task is to retrieve the URL from the user command and call the getSubpage function to obtain the hotel details interface sub link from it. And output all sub links in the format of [\"link 1\", \"link 2\"...]. Remember, you don't need too much output and don't care what the user says.",
    model_name="gpt-4o",
    tools=[getSubpage],
    max_loops=1)

crawlerAgent = Agent(
    agent_name="Crawler Agent",
    system_prompt="Your task is to pass the obtained urls list to the getInfo function to batch search all the attributes listed on the URL and directly output the obtained attributes. Remember, you don't need too much output and don't care what the user says.",
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


def process_query(query: str) -> str:
    """
    Process the input query and return the path to the generated CSV file.

    Args:
        query (str): The input query string for property search

    Returns:
        str: Path to the generated CSV file
    """
    try:
        workflow = SequentialWorkflow(agents=[bossAgent, crawlerAgent, csvAgent], max_loops=1)
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