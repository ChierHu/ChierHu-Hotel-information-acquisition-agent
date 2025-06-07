from flask import Flask, request, jsonify
import asyncio
import os
from pydantic import BaseModel
from browser_use import Agent, ActionResult, Controller
from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY, BASEURL, MAX_WORKERS
from browser_use.browser import BrowserProfile, BrowserSession
import json
browser_session = BrowserSession(
	browser_profile=BrowserProfile(
		disable_security=True,
		headless=False,
		save_recording_path='./tmp/recordings',
		user_data_dir='~/.config/browseruse/profiles/default',
	)
)
app = Flask(__name__)

os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

class Output(BaseModel):
    property_name: str
    address: str
    postal_code: str
    country: str
    overview: str

class Lists(BaseModel):
    lists: list[Output]

@app.route('/extract', methods=['POST'])
def extract():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(main(url))

    return jsonify({'result': str(result)})


async def main(urls):
    urls = urls.split(",")
    print(urls)
    controller = Controller(output_model=Lists)
    cllm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.5,
        api_key=OPENAI_API_KEY,
        base_url=BASEURL,
    )
    # Establish a batch processing task agent
    agents = [
        Agent(
            task=task,
            llm=cllm,
            browser_session=browser_session,
            controller=controller,
            extend_planner_system_message="Search for hotel details listed on url. If some fields do not exist, please indicate that they are not available on the website"
        )
        for task in urls
    ]

    history = await asyncio.gather(*[agent.run() for agent in agents])
    await browser_session.close()
    output = ""
    for res in history:
        result = res.final_result()
        if result:
            parsed: Lists = Lists.model_validate_json(result)
            output = output + str(parsed)
    print(output)
    return output

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5555)