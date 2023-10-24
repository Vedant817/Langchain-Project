from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/generate', method=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        output = request.form
    return jsonify(output)

app.run(host='0.0.0.0', port=3000)