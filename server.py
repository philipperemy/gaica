import os

from flask import Flask, request

from gaica import api

app = Flask(__name__)


@app.route('/hello', methods=['GET'])
def hello():
    return 'ok'


@app.route('/balance', methods=['POST'])
def balance():
    user = request.values['gaica_user']
    password = request.values['gaica_pass']
    os.environ['GAICA_USER'] = user
    os.environ['GAICA_PASS'] = password
    return api()


def run(host='0.0.0.0', port='4783'):
    app.run(host=host, port=port)


if __name__ == '__main__':
    run()
