# app.py
from flask import Flask, request, jsonify
from main import prompt, initialize_app  # Import the function from test.py

from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow all domains to access this API


# Define an API route to use process_data
@app.route('/prompt', methods=['POST'])
def process():
    data = request.json
    if 'prompt' in data:
        print("PROMPT: ", data['prompt'])
        result = prompt(data['prompt'])  # Call the function from test.py
        return jsonify(result)


# Run the app
if __name__ == '__main__':
    initialize_app()
    app.run(debug=True)
