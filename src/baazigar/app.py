"""Hello World"""

from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    "Hello World"
    return "Hello World"
