import traceback

from flask import request, Blueprint, Response
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest
from flask_restful import Resource, Api, reqparse
import logging

from regident.ris import RIS

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__)
api = Api(api_bp, prefix="/api/v1")
# error handling auto handled by the flask-restful lib. it will give a html

# all requests body are multipart/form-data content type
class Person(Resource):
    def get(self):
        """
        Get's info about the person, including all the persongroups the person is in.
        :return:
        """

        try:
            parser = reqparse.RequestParser()
            parser.add_argument("id", type=str, help="Wrong id format. Must be string.",
                                location="args")
            args = parser.parse_args()
            resp = RIS.get_person_info(**args)

        except BadRequest as e:
            return Response(response=e.data, status=e.code)

        except Exception as e:
            if hasattr(e, "status_code"):
                return Response(response=str(e), status=e.status_code)
            else:
                return Response(response=str(e), status=400)

        return resp.items

    def post(self):
        """
        Registers a new user with a unique id.

        :return:
        """
        results = []
        try:
            logger.debug("request headers " + str(request.headers))
            logger.debug("request body " + str(request.data))
            parser = reqparse.RequestParser()
            parser.add_argument("name", type=str, help="Wrong name format. Must be string.",
                                location="form")
            parser.add_argument("images", type=FileStorage, help="Wrong images format", action='append',
                                location="files")
            parser.add_argument("id", type=str, help="Wrong id format",
                                location="form")
            parser.add_argument("persongroupid", type=str, help="Wrong persongroupid format. Must be integer"
                                , location="form")

            args = parser.parse_args()

            results = RIS.register_person(**args)
        except BadRequest as e:
            return Response(response=e.data, status=e.code)

        except Exception as e:
            if hasattr(e, "status_code"):
                return Response(response=str(e), status=e.status_code)
            else:
                return Response(response=str(e), status=400)

        return results

    def put(self):
        """
        Adds faces to an already registered user.

        :return:
        """
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("id", type=str, help="Wrong id format.", location="args")
            parser.add_argument("persongroupid", type=str, help="Wrong persongroupid format.", location="args")
            parser.add_argument("images", type=FileStorage, help="Wrong images format", location="files",
                                action="append")
            args = parser.parse_args()

            results = RIS.add_face(**args)

        except BadRequest as e:
            return Response(response=e.data, status=e.code)

        except Exception as e:
            if hasattr(e, "status_code"):
                return Response(response=str(e), status=e.status_code)
            else:
                return Response(response=str(e), status=400)

        return results

    def delete(self):
        """
        Deletes a registered person from all person groups If persongroupid param is specified,
        will only delete person in that persongroupid.
        :param id:
        :return:
        """

        try:
            parser = reqparse.RequestParser()
            parser.add_argument("id", type=str, help="Wrong id format.", location="args")
            parser.add_argument("persongroupid", type=str, help="Wrong persongroupid format.", location="args", required=False
                                )
            args = parser.parse_args()
            results = RIS.delete_person(**args)

        except Exception as e:
            if hasattr(e, "status_code"):
                return Response(response=str(e), status=e.status_code)
            else:
                return Response(response=str(e), status=400)

        return results


class Identify(Resource):

    def post(self):
        """
        Analyzes an image for a person who is registered, and identifies them.

        :return:
        """
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("image", type=FileStorage, help="Wrong images format", location="files")
            parser.add_argument("threshold", type=float, help="Wrong argument format. Must be float.", location="form",
                                required=False)
            parser.add_argument("max_candidates_return", type=int, help="Wrong argument format. Must be int",
                                location="form", required=False)
            parser.add_argument("persongroups", type=str, help="Wrong persongroups format. Must be comma separated strings"
                                , location="args", required=False)

            args = parser.parse_args()

            # images = dict(request.files).get("images")
            # imagefile = images[0].file # images[0].file does not throsw error in local dev
            # images[0].file thros error in deployment, so use images[0] instead. seems to be the same thing
            results = RIS.identify(**args)

        except BadRequest as e:
            return Response(response=e.data, status=e.code)

        except Exception as e:
            if hasattr(e, "status_code"):
                return Response(response=str(e), status=e.status_code)
            else:
                return Response(response=str(e), status=400)

        return results


class PersonGroup(Resource):
    def get(self):
        """
        Get details of a person group. If persongroupid not specified, it will return all details
        of persongroup.
        :return:
        """
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("persongroupid", type=str, required=False,
                                help="Wrong person group id format. Must be string", location="args")
            args = parser.parse_args()
            resp = RIS.get_persongroup_details(**args)
        except BadRequest as e:
            return Response(response=e.data, status=e.code)

        except Exception as e:
            if hasattr(e, "status_code"):
                return Response(response=str(e), status=e.status_code)
            else:
                return Response(response=str(e), status=400)

        return resp

    def post(self):
        """
        Creates a person group.
        :return:
        """
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("persongroupid", type=str, help="Wrong person group id format. Must be string",
                                location="form")
            parser.add_argument("name", type=str, help="Wrong name format. Must be string", location="form",
                                required=False)
            parser.add_argument("data", type=str, help="Wrong data format. Must be string", location="form",
                                required=False)
            args = parser.parse_args()
            resp = RIS.create_persongroup(**args)

        except BadRequest as e:
            return Response(response=e.data, status=e.code)

        except Exception as e:
            if hasattr(e, "status_code"):
                return Response(response=str(e), status=e.status_code)
            else:
                return Response(response=str(e), status=400)

        return resp

    def delete(self):
        """
        Deletes a person group.
        :return:
        """
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("persongroupid", type=str, help="Wrong person group id format. Must be string",
                                location="args")
            args = parser.parse_args()
            resp = RIS.delete_persongroup(**args)

        except BadRequest as e:
            return Response(response=e.data, status=e.code)

        except Exception as e:
            if hasattr(e, "status_code"):
                return Response(response=str(e), status=e.status_code)
            else:
                return Response(response=str(e), status=400)

        return resp

# api.handle_error()

api.add_resource(Person, "/person")
api.add_resource(Identify, "/identify")
api.add_resource(PersonGroup, "/persongroup")
