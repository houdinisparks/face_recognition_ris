import traceback
from itertools import chain
import cognitive_face as CF
import logging

from azure.storage.table import TableService
from cognitive_face import CognitiveFaceException

from regident.config.config import app_config


from regident.person import Person
from regident.persongroups import PersonGroup

"""
CONFIGURATIONS
"""

logger = logging.getLogger(__name__)

"""
API METHODS
"""


# Registration and Identification System (RIS)
class RIS(Person, PersonGroup):

    @staticmethod
    def identify(image, threshold=0.5, max_candidates_return=2, persongroups=None):
        """
        Detects if there are any faces in the image, and identifies the faces if there is.
        If the face is not found in any person groups, then "identified_in_persongroups" key
        will return an empty list.

        :param image:
        :param threshold:
        :param max_candidates_return:
        :param persongroups: if None, it will check through all persongroups.
        :return:
        """

        response = {}
        detected = CF.face.detect(image)  # returns an array of dictionary
        image.seek(0)  # restart the cursor at the buffer.

        if not detected:
            return response

        faceids = [x["faceId"] for x in detected]
        logger.info("faceids detected: {}".format(faceids))
        if not faceids:
            return response

        # identify face person groups. if persongroups=None, then it will check against all persongroups
        if persongroups is None:
            persongroups = CF.person_group.lists()
            persongroups = [persongroup["personGroupId"]  for persongroup in persongroups]  # [f['name'] for f in fields]
        else:
            persongroups = persongroups.split(",")

        # faceids_similaritycheck = [] # this is for checking against facelists if no person group is found.
        # identified = False
        for persongroupid in persongroups:

            try:
                identify_results = CF.face.identify(faceids, person_group_id=persongroupid,
                                                    max_candidates_return=max_candidates_return, threshold=threshold)
            except CognitiveFaceException as e:
                if e.code == "PersonGroupNotTrained":
                    response[persongroupid] = "Person group is either not trained, or is empty."
                else:
                    response[persongroupid] = e.code

                logger.error(traceback.format_exc())
                continue

            personids = []
            for result in identify_results:
                candidates = result["candidates"]
                if not candidates:
                    continue

                else:
                    # personids = [x["personId"] for x in candidates]
                    personids.append([x["personId"] for x in
                                      candidates])  # [{'personId': '72db5f04-4380-47cd-9091-8ba76495f0a5', 'confidence': 1.0}]
                    # remove identified faceids from list
                    # faceids.remove(result["faceId"])

            # flattens 2d to 1d list
            personids = list(chain.from_iterable(
                personids))  # flattens list https://stackoverflow.com/questions/20112776/how-do-i-flatten-a-list-of-lists-nested-lists

            # remove duplicates
            personids = list(set(personids))
            # faceids_similaritycheck = list(set(faceids_similaritycheck))

            # for each person, make a json dict response
            for personid in personids:
                detected = CF.person.get(persongroupid, personid)
                jsonperson = {"name": detected["name"],
                              "userdata": detected["userData"]}

                if persongroupid not in response:
                    response[persongroupid] = []

                response[persongroupid].append(jsonperson)

            # if faceids is empty / no more face ids to identify then breaks
            # if not faceids:
            #     break

        return response

# """
# JUNK
  # # DONE! For those faceids in the unregistered list, put it into the faceList.
        #
        # facelists = CF.face_list.lists()
        # for facelist in facelists:
        #
        #     for faceid in faceids_similaritycheck:
        #         results_facelist = checksimilarity(faceid, "identified_in_facelists")
        #
        #         if not results_facelist:
        #             for dict_ in [x for x in detected if x["faceId"] == result["faceId"]]:
        #                 # targetFace=left,top,width,height". E.g. "targetFace=10,10,100,100"
        #                 dict_ = dict_["faceRectangle"]
        #                 targetface = (str(dict_["left"]) + "," + str(dict_["top"]) + ","
        #                               + str(dict_["width"]) + "," + str(dict_["height"]))
        #
        #                 CF.face_list.add_face(imagefile, "unregistered", target_face=targetface)
        #                 imagefile.seek(0)
        #         else:
        #             response["unregistered"].append(results_facelist)
        #
        #     response["identified_in_facelists"] = list(chain.from_iterable(
        #         response["identified_in_facelists"]))


# """
# PRIVATE METHODS, FOR INTERNAL USE IN THIS FILE ONLY.
# """
#
#
# # check if there are any similar faces detected before
# def checksimilarity(faceid, facelistid):
#     results = CF.face.find_similars(face_id=faceid,
#                                     face_list_id=facelistid,
#                                     mode="matchPerson")
#     response = []
#     for result in results:
#         if result["confidence"] >= 0.8:
#             response.append(result["persistedFaceId"])
#
#     return response
#
#
# def checkpersonregistered(id, persongroupid):
#     registered = True
#     try:
#         table_service = TableService(account_name=config.AZURESTORAGE_ACCTNAME,
#                                      account_key=config.AZURESTORAGE_KEY)
#         if not persongroupid:
#             query = "RowKey eq '" + str(id) + "'"
#             entity = table_service.query_entities(config.AZURESTORAGE_TABLENAME,
#                                                   filter=query)
#         else:
#             entity = table_service.get_entity(config.AZURESTORAGE_TABLENAME,
#                                               partition_key=persongroupid,
#                                               row_key=id)
#     except Exception as e:
#         registered = False
#
#     return registered
