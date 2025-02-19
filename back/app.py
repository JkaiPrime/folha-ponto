from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return True


@app.route("/get-all")
def get_all():
    pass


@app.route("/get-by-code")
def get_by_code():
    pass


@app.route("/update-period")
def update_period():
    pass


@app.route("/include-period")
def include_period():
    pass
