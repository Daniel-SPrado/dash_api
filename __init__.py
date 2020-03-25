import os

from flask import Flask


def create_app(config_object=''):
    app = Flask(__name__)
    return app