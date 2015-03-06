import logging
from flask import Flask
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)


@app.route("/")
def hello():
    logging.info('output to log')
    return "Hello World!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)
