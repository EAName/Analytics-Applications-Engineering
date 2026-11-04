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
    """Load an uploaded CSV into BigQuery and return model predictions."""
    file = request.files.get('file')
    if file is None or file.filename == '':
        return app.response_class(
            response=json.dumps({"error": "upload a CSV in the 'file' field"}),
            status=400,
            mimetype='application/json'
        )
    result_data = ml_satellite.load_csv(file.stream)
    response = app.response_class(
        response=json.dumps(result_data),
        status=200,
        mimetype='application/json'
    )
    return response    


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, gunicorn serves the app (see app.yaml).
    app.run(host='127.0.0.1', port=8080, debug=True)
