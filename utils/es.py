from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient

from django.conf import settings

# from mgmt import models as mgmt_models


es = Elasticsearch(
    hosts=settings.ELASTICSEARCH["hosts"],
    # sniff_on_start=True,
    # # refresh nodes after a node fails to respond
    # sniff_on_connection_fail=True,
    # # and also every 60 seconds
    # sniffer_timeout=12,
    http_auth=(
       settings.ELASTICSEARCH["username"],
       settings.ELASTICSEARCH["password"]
    )
)


indices_client = IndicesClient(es)


class Mapping(object):
    MAP = {
        0: {"type": "keyword"},
        1: {"type": "long"},
        2: {"type": "double"},
        3: {"type": "date", "format": "yyyy-MM-dd'T'HH:mm:ss"},
        4: {"type": "date", "format": "yyyy-MM-dd"},
        5: {"type": "boolean"},
        6: {"type": "ip"},
        7: {"type": "keyword"},
        8: {"type": "keyword"},
        9: {"type": "text"},
    }

    @classmethod
    def _generate_mapping(cls, table):
        mapping = {}
        for field in table.fields.all():
            mapping[field.name] = cls.MAP[field.type]
        return mapping

    @classmethod
    def generate_data_mapping(cls, table):
        system_mapping = {
            "S-creator": cls.MAP[0],
            "S-creation-time": cls.MAP[3],
            "S-last-modified": cls.MAP[0]
        }
        field_mapping = cls._generate_mapping(table)
        return dict(**system_mapping, **field_mapping)

    @classmethod
    def generate_record_data_mapping(cls, table):
        system_mapping = {
            "S-data-id": cls.MAP[0],
            "S-changer": cls.MAP[0],
            "S-update-time": cls.MAP[3]
        }
        field_mapping = cls._generate_mapping(table)
        return dict(**system_mapping, **field_mapping)

    @classmethod
    def generate_deleted_data_mapping(cls, table):
        system_mapping = {
            "S-delete-people": cls.MAP[0],
            "S-delete-time": cls.MAP[3]
        }
        field_mapping = cls._generate_mapping(table)
        return dict(**system_mapping, **field_mapping)

    @classmethod
    def generate_field_mapping(cls, field):
        """
        生成一个字段的mapping
        :param field: Filed 的模型对象
        :return: example:
        {
            "d4": {
                "type":  "double"
            }
        }
        """
        return {field.name: cls.MAP[field.type]}
