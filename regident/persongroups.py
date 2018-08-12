import logging
import cognitive_face as CF

logger = logging.getLogger(__name__)

class PersonGroup:

    @staticmethod
    def get_persongroup_details(persongroupid=None):
        if persongroupid != None:
            result = CF.person_group.get(persongroupid)
        else:
            result = CF.person_group.lists()
        return result

    @staticmethod
    def delete_persongroup(persongroupid):
        result = CF.person_group.delete(persongroupid)
        return result

    @staticmethod
    def create_persongroup(persongroupid, name=None, data=None):
        result = CF.person_group.create(persongroupid, name, data)
        return result