from flask import request, Blueprint
from cognizant import faceprocessor
from flask_restful import Resource, Api

api_bp = Blueprint('api', __name__)
api = Api(api_bp, prefix="/api/v1")

# all requests are multipart/form-data
class Person(Resource):

    # create person with image
    def put(self):
        id = request.form["id"]
        name = request.form["name"]
        persongroupid = request.form["persongroupid"]  # employees | visitors
        images = dict(request.files).get("images")

        images_file = []
        for image in images:
            # images_file.append(image.file)
            images_file.append(image)

        results = faceprocessor.uploadperson(id, persongroupid, name, images_file)
        return {"response": results}

    # identify person based on image. it couldt fall under employees | visitors | unidentified
    def post(self):
        images = dict(request.files).get("images")
        imagefile = images[0].file # images[0].file does not throw error in local dev
        # imagefile = images[0] # images[0].file thros error in deployment, so use images[0] instead. seems to be the same thing

        results = faceprocessor.identify(imagefile)
        return {"response": results}

    def delete(self):
        id = request.form["id"]
        results = faceprocessor.deleteperson(id)
        return {"response":results}

class Face(Resource):

    # adds face to person
    def post(self,type):
        # if type == "similar":
        #     images = dict(request.files).get("images")
        #     image_file = images[0].file
        #     results = faceprocessor.identify(image_file)
        #     return {"response": results}
        #
        # elif type == "upload":

        images = dict(request.files).get("images")
        id = request.form["id"]
        images_file = []
        for image in images:
            images_file.append(image.file)

        results = faceprocessor.uploadface(id, images_file)

        return {"response": results}


api.add_resource(Person, "/person")
api.add_resource(Face, "/face")
