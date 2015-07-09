import unittest
from unittest.mock import patch
from unittest.mock import Mock
from elasticsearch import Elasticsearch
import json


class ESIndexOps:

    def __init__(self):
        self.es = Elasticsearch()
        self.index_config = {
                 "settings" : {
                    "analysis" : {
                        "analyzer" : {
                            "remove_html" : {
                                "tokenizer" : "standard",
                                "char_filter" : [ "html_strip" ]
                                }
                            }
                        }
                    }
                
                ,
                
                    "mappings" : {
                        "talk" : {
                            "properties" : {
                                "title" : { "type": "string" },
                                "author" : { "type": "string" },
                                "confid" : { "type": "string" },
                                "content" : { "type": "string", "analyzer": "remove_html" }
                            }
                        }
                    }
                
            }
        self.index_name = "gc-index"
        

    def CreateGCIndexWithMapping(self):
        index_json = json.dumps(self.index_config)
        self.es.indices.create(index=self.index_name, body=index_json)


class ESIndexOpsTests(unittest.TestCase):

    def setUp(self):
        self.esio = ESIndexOps()

    def test_CreateGCIndexWithMapping_ESCalledAppropriately(self):
        with patch.object(self.esio.es.indices, "create", return_value=None) as mock_method:
            self.esio.CreateGCIndexWithMapping()
        mock_method.assert_called_once_with(index=self.esio.index_name, body=json.dumps(self.esio.index_config))
