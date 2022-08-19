from flask import Flask
from flask import json
from flask import request
import ml_satellite

app = Flask(__name__)

@app.route('/get-model')
def get_model():
    """Return data."""
    result_data = ml_satellite.query_data()
    response = app.response_class(
        response=json.dumps(result_data),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World!' 

@app.route('/satellite-model', methods=['POST'])
def sat_model():
    file = request.files['file']
   
    """Return file data."""
    result_data = ml_satellite.load_csv(file)
    response = app.response_class(
        response=json.dumps(result_data),
        status=200,
        mimetype='application/json'
    )
    return response    


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    
    app.run(host='127.0.0.1', port=8080, debug=True)
