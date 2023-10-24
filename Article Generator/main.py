from flask import Flask, render_template, request
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import openai

load_dotenv()
API_KEY = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/generate', methods=['GET','POST'])
def generate():
    if request.method == 'POST':
        llm = OpenAI(openai_api_key=API_KEY,temperature = 0.7)
        prompt = PromptTemplate.from_template("Write an Article on {title}")
        title = request.json.get('prompt') #! allows you to access JSON data sent in an HTTP request.
        #? request.form-> The key/value pairs in the body, from a HTML post form, or JavaScript request that isn't JSON encoded.
        chain = LLMChain(llm=llm, prompt=prompt)
        output = chain.run(title)
    return output

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
