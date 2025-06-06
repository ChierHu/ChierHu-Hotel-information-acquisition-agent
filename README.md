# Hotel Property Information Scraper

A Python application that scrapes hotel property information from websites and exports it to CSV format. The application uses a multi-agent workflow system powered by OpenAI's GPT models to process and structure the data.

## Features

- Web scraping of hotel property information
- Structured data extraction including:
  - Property name
  - Address
  - Zip code
  - Country
  - Property summary
- CSV export functionality
- User-friendly Gradio interface

## Prerequisites

- Python 3.11+
- Required Python packages (install via pip):
  - swarms
  - requests
  - python-dotenv
  - gradio
  - pydantic

## Setup

1. Clone this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```
3. Configure your OpenAI API key:
   - Open `config.py`
   - Set your `OPENAI_API_KEY` value
   - (Optional) Modify `OUTPUT_CSV_FILE` path if needed
   - (Optional) Configure `API_ENDPOINT` for your scraping service

## Usage

1. Run the application:
```bash
python main.py
```

2. Access the Gradio interface in your web browser
3. Enter a URL or search query in the text box
4. The application will process the request and generate a CSV file with the extracted information

## Project Structure

- `main.py`: Main application file with workflow logic
- `config.py`: Configuration settings
- `models.py`: Data models for structured information
- `requirements.txt`: Project dependencies

## Note

Make sure to properly configure your OpenAI API key in `config.py` before running the application. The API key is required for the GPT models to function correctly.
