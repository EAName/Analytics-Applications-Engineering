from flask import Flask

App = Flask(__name__)

@app.route('/')
def hello():
	return 'Hello World!'

If __name__ == '__main__':
	app.run(host='127.0.0.1',port=8080, debug=True
