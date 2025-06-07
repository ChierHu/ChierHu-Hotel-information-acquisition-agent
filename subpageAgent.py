from flask import Flask, request, jsonify
import asyncio
import os
from pydantic import BaseModel
from browser_use import Agent, ActionResult, Controller
from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY, BASEURL
app = Flask(__name__)
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

class Output(BaseModel):
    subpage: str

class Lists(BaseModel):
    lists: list[Output]
@app.route('/extract', methods=['POST'])
def extract():
    prompt = request.json.get('prompt')
    if not prompt:
        return jsonify({'error': 'prompt is required'}), 400

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(main(prompt))

    return jsonify({'result': result})

async def main(prompt):
    controller = Controller(output_model=Lists)
    cllm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.5,
        api_key=OPENAI_API_KEY,
        base_url=BASEURL,
    )
    agent = Agent(
        task=prompt,
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