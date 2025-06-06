from flask import Flask, request, jsonify
import asyncio
import os
from pydantic import BaseModel
from browser_use import Agent, ActionResult, Controller
from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY
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

    return jsonify({'result': result})

async def main(url):
    controller = Controller(output_model=Lists)
    cllm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.5,
        api_key=OPENAI_API_KEY,
        base_url="https://api.openai.com/v1",
    )
    agent = Agent(
        task=f"Find all the properties listed on {url}, If some fields do not exist, please write that the field is not available on the website",
        llm=cllm,
        controller=controller,
    )
    history = await agent.run()
    result = history.final_result()
    await agent.close()
    if result:
        parsed: Lists = Lists.model_validate_json(result)
        print(str(parsed))
        return str(parsed)
    else:
        return 'No result'

if __name__ == '__main__':
    app.run(debug=True)