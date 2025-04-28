from flask import Flask, request, jsonify
from command_processor import process_command

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    query = data.get('query', '')
    response = process_command(query)
    return jsonify({'response': response})

if __name__ == "__main__":
    app.run(debug=True, port=5000)