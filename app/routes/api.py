import io

from flask import request
from flask_restful.reqparse import RequestParser
from werkzeug.datastructures import ImmutableMultiDict

from cognizant import faceprocessor
from app import app
from flask_restful import Resource, Api
from PIL import Image

api = Api(app, prefix="/api/v1")


# all requests are multipart/form-data
# class PersonDetect(Resource):
#     def post(self):
#         images = dict(request.files).get("images")
#         image_file = images[0].file
#         results = faceprocessor.identify(image_file)
#         return {"response": results}


class Person(Resource):

    # create person with image
    def put(self):
        id = request.form["id"]
        name = request.form["name"]
        persongroupid = request.form["persongroupid"]  # employees | visitors
        images = dict(request.files).get("images")

        images_file = []
        for image in images:
            images_file.append(image.file)

        results = faceprocessor.uploadperson(id, persongroupid, name, images_file)
        return {"response": results}

    # identify person based on image. it couldt fall under employees | visitors | unidentified
    def post(self):
        images = dict(request.files).get("images")
        imagefile = images[0].file # empty the buffer and store into a python object.

        results = faceprocessor.identify(imagefile)
        return {"response": results}



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

        results = faceprocessor.uploadface(id,images_file)

        return {"response": results}


api.add_resource(Person, "/person")
api.add_resource(Face, "/face")
