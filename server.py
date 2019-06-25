import json
import os

from flask import Flask, request

from gaica import GaicaClient

app = Flask(__name__)


def pretty(d, indent=0, output_list=[]):
    for key, value in d.items():
        output_list.append('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent + 1, output_list)
        else:
            output_list.append('\t' * (indent + 1) + str(value))


@app.route('/hello', methods=['GET'])
def hello():
    return 'ok'


@app.route('/balance', methods=['POST'])
def balance():
    user = request.values['gaica_user']
    password = request.values['gaica_pass']
    os.environ['GAICA_USER'] = user
    os.environ['GAICA_PASS'] = password
    current_balance = json.loads(GaicaClient().fetch_balance())
    o = []
    pretty(current_balance, indent=0, output_list=o) # updates o
    output_str = '\n'.join(o)
    return output_str
    # '通貨コード'


@app.route('/charge', methods=['POST'])
def charge():
    user = request.values['gaica_user']
    password = request.values['gaica_pass']
    os.environ['GAICA_USER'] = user
    os.environ['GAICA_PASS'] = password
    return GaicaClient().charge()


def run(host='0.0.0.0', port='4783'):
    app.run(host=host, port=port)


if __name__ == '__main__':
    run()
