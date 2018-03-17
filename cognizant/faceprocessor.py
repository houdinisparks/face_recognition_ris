import copy
from itertools import chain

import cognitive_face as CF
import logging

import sys
from azure.storage.table import TableService
from flask import json

from cognizant.config.config import app_config

"""
Configurations
"""
config = app_config["default"]
CF.Key.set(config.FACEAPI_KEY)
CF.BaseUrl.set(config.FACEAPI_BASEURL)
"""
Logging
"""
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def identify(imagefile):
    """
    Detects if there are any faces in the image, and identifies the faces if there is.
    If the face is not found in any person groups ( employees | visitors ), then the face
    will be checked against the facelistid:unregistered. If it's not found then it will be
    uploaded to the facelist with id:unidentified.

    :param imagefile: A URL or a file path or a file-like object represents an image.
    :return: An array of (personname, id, persongroupid)
    """
    # parse image to determine which headers and request
    # type to send
    response = {
        "registered": [],  # identified in employees | visitors groups
        "unregistered": []  # identified in facelistid:unregistered
    }

    detected = CF.face.detect(imagefile)  # resturns an array of dictionary
    imagefile.seek(0)   # restart the cursor at the buffer.
    faceids = []
    for result in detected:
        faceids.append(result["faceId"])

    logger.info("faceids detected: {}".format(faceids))

    # identify face in all person groups
    persongroups = CF.person_group.lists()
    faceids_similaritycheck = []
    if not faceids:
        return response

    for persongroup in persongroups:
        persongroupid = persongroup["personGroupId"]

        identify_results = CF.face.identify(faceids, person_group_id=persongroupid,
                                            max_candidates_return=2, threshold=0.7)
        personids = []
        for result in identify_results:
            candidates = result["candidates"]
            if not candidates:
                faceids_similaritycheck.append(result["faceId"])

            else:
                personids.append(candidates)

        personids = list(chain.from_iterable(
            personids))  # flattens list https://stackoverflow.com/questions/20112776/how-do-i-flatten-a-list-of-lists-nested-lists

        # remove duplicates
        personids = list(set(personids))
        faceids_similaritycheck = list(set(faceids_similaritycheck))

        for personid in personids:
            detected = CF.person.get(persongroupid, personid)
            id = json.loads(detected["userData"])["id"]
            response["registered"].append((detected["name"], id, persongroupid))

    # TODO: For those faceids in the unregistered list, put it into the faceList.
    for faceid in faceids_similaritycheck:
        results_facelist = checksimilarity(faceid, "unregistered")

        if not results_facelist:
            for dict_ in [x for x in detected if x["faceId"] == result["faceId"]]:
                # targetFace=left,top,width,height". E.g. "targetFace=10,10,100,100"
                dict_ = dict_["faceRectangle"]
                targetface = (str(dict_["left"]) + "," + str(dict_["top"]) + ","
                              + str(dict_["width"]) + "," + str(dict_["height"]))

                CF.face_list.add_face(imagefile, "unregistered", target_face=targetface)
                imagefile.seek(0)
        else:
            response["unregistered"].append(results_facelist)

    response["unregistered"] = list(chain.from_iterable(
        response["unregistered"]))

    return response


def uploadperson(id, persongroupid, name, images):
    response = "ok"
    try:
        userdata = "id:" + id
        personid = CF.person.create(persongroupid, name, userdata)

        for image in images:
            CF.person.add_face(image, persongroupid, personid)

        # add id and personid to azure table
        # this is so that when an employee/visitor wants to add their faces to the table
        # we know which personid they are referring to with their given id.
        table_service = TableService(account_name=config.AZURESTORAGE_ACCTNAME,
                                     account_key=config.AZURESTORAGE_KEY)
        entity = {
            "PartitionKey": persongroupid,
            "RowKey": id,
            "PersonId": personid,
            "PersonName": name
        }

        table_service.insert_entity(table_name=config.AZURESTORAGE_TABLENAME,
                                    entity=entity)
    except Exception as e:
        # response = "error({0}): {1}".format(e.errno, e.strerror)
        response = "unexpected error: " + sys.exc_info()[0]

    return response


def uploadface(id, images):
    response = "ok"
    try:
        table_service = TableService(account_name=config.AZURESTORAGE_ACCTNAME,
                                     account_key=config.AZURESTORAGE_KEY)

        # get personid based on id
        entity = table_service.get_entity(config.AZURESTORAGE_TABLENAME,
                                          row_key=id)
        persongroupid = entity.get("PartitionKey")
        personid = entity.get("PersonId")

        for image in images:
            CF.person.add_face(image, persongroupid, personid)

    except Exception as e:
        response = "unexpected error: " + sys.exc_info()[0]

    return response


# internal use only, not accessible by api
def checksimilarity(faceid, facelistid):
    results = CF.face.find_similars(face_id=faceid,
                                    face_list_id=facelistid,
                                    mode="matchPerson")
    response = []
    for result in results:
        if result["confidence"] >= 0.8:
            response.append(result["persistedFaceId"])

    return response
