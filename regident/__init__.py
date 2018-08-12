from regident.config.config import app_config
import cognitive_face as CF

config = app_config["default"]
CF.Key.set(config.FACEAPI_KEY)
CF.BaseUrl.set(config.FACEAPI_BASEURL)
