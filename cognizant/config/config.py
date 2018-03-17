'''
Reads the config.ini file.
'''
import configparser
import io

config = configparser.ConfigParser()
config.read("cognizant\\config\\config.ini")

# with open("cognizant\\config\\config.ini") as f:
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
    FACEAPI_FACELISTID = config["DEFAULT"]["FACEAPI_FACELISTID"]


app_config = {
    "default": Config
}
