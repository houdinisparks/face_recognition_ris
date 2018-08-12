'''
Reads the config.ini file.
'''
import configparser
import io
import os
import sys

# todo: config class should read the passwords from the http message header.
# https://blog.restcase.com/restful-api-authentication-basics/

config = configparser.ConfigParser()
dir = os.path.dirname(__file__)
config.read(dir + "/config.ini")
print(dir)

# with open("regident\\config\\config.ini") as f:
#     sample_config = f.read()
# config = configparser.ConfigParser.RawConfigParser(allow_no_value=True)
# config.readfp(io.BytesIO(sample_config))

class Config():
    """Parent configuration class."""
    DEBUG = False
    CSRF_ENABLED = True
    FACEAPI_KEY = config["DEFAULT"]["FACEAPI_KEY"]
    FACEAPI_BASEURL = config["DEFAULT"]["FACEAPI_BASEURL"]
    AZURESTORAGE_KEY = config["DEFAULT"]["AZURESTORAGE_KEY"]
    AZURESTORAGE_CONNECTIONSTRING = config["DEFAULT"]["AZURESTORAGE_CONNECTIONSTRING"]
    AZURESTORAGE_ACCTNAME = config["DEFAULT"]["AZURESTORAGE_ACCTNAME"]
    AZURESTORAGE_TABLENAME = config["DEFAULT"]["AZURESTORAGE_TABLENAME"]


app_config = {
    "default": Config
}
