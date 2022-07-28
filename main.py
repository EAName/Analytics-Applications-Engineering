from flask import Flask
from flask import json
import ml_satellite


app = Flask(__name__)

@app.route('/get-model')
def get_model():
    """Return a friendly HTTP greeting."""
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


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app.
    app.run(host='127.0.0.1', port=8080, debug=True)
