# from flask import Flask
#
# app = Flask(__name__, static_url_path='')
#
# from app.routes import index
# from app.routes import api
#
# zappa_app = app
#
# # We only need this for local development.
# if __name__ == '__main__':
#     print("initiating the web app...")
#     app.run(debug=True)
import logging
import sys

logging.basicConfig(
    stream=sys.stdout,
    format="('%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt='%H:%M:%S',
    level=logging.DEBUG)
