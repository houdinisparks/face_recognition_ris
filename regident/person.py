import json
import logging
import traceback

import time
from azure.common import AzureConflictHttpError, AzureMissingResourceHttpError
from azure.storage.table import TableService, Entity
from cognitive_face import CognitiveFaceException
import cognitive_face as CF
from requests import HTTPError

from regident import config

logger = logging.getLogger(__name__)


class Person:
    table_service = TableService(account_name=config.AZURESTORAGE_ACCTNAME,
                                 account_key=config.AZURESTORAGE_KEY)

    @classmethod
    def register_person(cls, persongroupid, name, images, id, userdata={}):
        """
        Uploads a person to the Face API with persongroupid, name and .png image details.
        After uploading to the Face API, a person_id is generated. Together with this person id,
        the given user id will be added to the Azure Storage Table.
        :param id:
        :param persongroupid:
        :param name:
        :param images:
        :return:
        """
        person_id = ""

        try:

            # todo: get access keys and secrets from os.environ

            userdata["id"] = id
            userdata = json.dumps(userdata)
            person_id = CF.person.create(persongroupid, name, userdata)
            person_id = person_id["personId"]

            # add id and person_id to azure table
            entity = Entity()
            entity["PartitionKey"] = persongroupid
            entity["RowKey"] = id
            entity["PersonId"] = person_id
            entity['PersonName'] = name
            entity['PersonData'] = userdata

            cls.table_service.insert_entity(table_name=config.AZURESTORAGE_TABLENAME,
                                            entity=entity)

            for image in images:
                CF.person.add_face(image, persongroupid, person_id)

            # update the person group data to update the person_count
            resp = CF.person_group.get(persongroupid)
            persongroup_userdata = json.loads(resp["userData"])
            persongroup_userdata["person_count"] += 1
            CF.person_group.update(persongroupid, user_data=json.dumps(persongroup_userdata))

            # train person in person group
            CF.person_group.train(persongroupid)

            # todo: save image in azure blob storage.

        except AzureConflictHttpError as e:
            CF.person.delete(persongroupid, person_id)
            raise e
            # raise HTTPError("Person already registered.", status_code = e.status_code)

        except CognitiveFaceException as e:
            if e.code == "PersonGroupNotFound":
                e.msg = "Person group is not found. Please create the group first."
                raise e

            if e.code == "PersonGroupTrainingNotFinished":
                train_finish = False
                try:
                    while not train_finish:
                        time.sleep(2)
                        result = CF.person_group.get_status(persongroupid)
                        if result["status"] == "succeeded":
                            train_finish = True
                except Exception as e:
                    pass

            else:
                raise e

        except Exception as e:
            # response = "error({0}): {1}".format(e.errno, e.strerror)
            response = "unexpected error: {}".format(str(e))
            logger.debug(response)
            CF.person.delete(persongroupid, person_id)
            cls.table_service.delete_entity(table_name=config.AZURESTORAGE_TABLENAME,
                                            partition_key=persongroupid,
                                            row_key=id)
            raise Exception(response)

    @classmethod
    def delete_person(cls, id, persongroupid=None):
        try:

            if persongroupid == None:
                # delete person from all person groups
                entities = cls.get_person_info(id)

            else:
                # partitions = []
                # for id in persongroupid:
                #     partitions.append("PartitionKey eq {}".format(id))
                # query = "and".join(partitions)

                # query = query + " and RowKey eq '{}'".format(id)
                query = "PartitionKey eq '{0}' and RowKey eq '{1}'".format(persongroupid, id)
                entities = cls.table_service.query_entities(config.AZURESTORAGE_TABLENAME,
                                                            filter=query)
            # personid = entities.items[0]["PersonId"]
            for item in entities.items:
                persongroupid = item["PartitionKey"]
                personid = item["PersonId"]
                cls.table_service.delete_entity(table_name=config.AZURESTORAGE_TABLENAME,
                                                partition_key=persongroupid,
                                                row_key=id)
                try:
                    # delete from face api and azure storage
                    CF.person.delete(persongroupid, personid)

                    # update the person group data to update the person_count
                    resp = CF.person_group.get(persongroupid)
                    persongroup_userdata = json.loads(resp["userData"])
                    persongroup_userdata["person_count"] -= 1
                    CF.person_group.update(persongroupid, user_data=json.dumps(persongroup_userdata))

                    # retrain person group
                    CF.person_group.train(persongroupid)

                except CognitiveFaceException as e:

                    if e.code == "PersonGroupTrainingNotFinished":
                        train_finish = False
                        try:
                            while not train_finish:
                                time.sleep(2)
                                result = CF.person_group.get_status(persongroupid)
                                if result["status"] == "succeeded":
                                    train_finish = True
                        except Exception as e:
                            pass
                    else:
                        cls.table_service.insert_entity(table_name=config.AZURESTORAGE_TABLENAME,
                                                        entity=item)


        except AzureMissingResourceHttpError as e:
            # e = "Person not found in Azure table \n" \
            #             "persongroupid {0}\n" \
            #             "id {1}".format(persongroupid, id)
            raise e

        except Exception as e:
            # response = "unexpected error: " + sys.exc_info()[0]
            response = "caught error: {}".format(str(e))
            logger.debug(response)
            raise e

    @classmethod
    def add_face(cls, persongroupid, id, images):
        try:

            # get personid based on id. full table scan
            entity = cls.table_service.get_entity(config.AZURESTORAGE_TABLENAME,
                                                  partition_key=persongroupid, row_key=id)

            personid = entity.get("PersonId")

            for image in images:
                CF.person.add_face(image, persongroupid, personid)

            CF.person_group.train(persongroupid)

        except AzureMissingResourceHttpError as e:
            raise e

        except CognitiveFaceException as e:
            if e.code == "PersonGroupTrainingNotFinished":
                train_finish = False
                try:
                    while not train_finish:
                        time.sleep(2)
                        result = CF.person_group.get_status(persongroupid)
                        if result["status"] == "succeeded":
                            train_finish = True
                except Exception as e:
                    logger.debug(traceback.format_exc())

        except Exception as e:
            # response = "unexpected error: " + sys.exc_info()[0]
            response = "unexpected error: " + str(e)
            logger.debug(response)
            raise e

    @classmethod
    def get_person_info(cls, id):
        """
        Retrieves all the person's info includin the personid tagged with Azure Face Api,
        all the persongroups they are in.

        :param id:
        :return: all the personids based on the unique id
        """

        query = "RowKey eq '{0}'".format(id)
        entities = cls.table_service.query_entities(table_name=config.AZURESTORAGE_TABLENAME,
                                                    filter=query,
                                                    select="PartitionKey,RowKey,PersonId,"
                                                           "PersonName,PersonData")
        return entities