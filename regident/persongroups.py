import json
import logging
import traceback

import cognitive_face as CF
from azure.storage.table import TableService, TableBatch

from regident import config

logger = logging.getLogger(__name__)

class PersonGroup:

    table_service = TableService(account_name=config.AZURESTORAGE_ACCTNAME,
                                 account_key=config.AZURESTORAGE_KEY)

    @staticmethod
    def get_persongroup_details(persongroupid=None):
        if persongroupid != None:
            result = CF.person_group.get(persongroupid)
        else:
            result = CF.person_group.lists()

        return result

    @classmethod
    def delete_persongroup(cls,persongroupid):
        try:

            # delete partition key from azure table
            entities = cls.table_service.query_entities(table_name=config.AZURESTORAGE_TABLENAME,
                                                        filter="PartitionKey eq '{}'".format(persongroupid))
            batch = TableBatch()
            for entity in entities.items:
                batch.delete_entity(partition_key=entity["PartitionKey"],
                                    row_key=entity["RowKey"])

            cls.table_service.commit_batch(table_name=config.AZURESTORAGE_TABLENAME,
                                           batch=batch)

            CF.person_group.delete(persongroupid)
        except Exception as e:
            logger.error(traceback.format_exc())
            raise e

    @staticmethod
    def create_persongroup(persongroupid, name=None, data=None):
        if data is None:
            data = {}
        else:
            data = json.loads(data)

        data["person_count"] = 0
        result = CF.person_group.create(persongroupid, name, json.dumps(data))


