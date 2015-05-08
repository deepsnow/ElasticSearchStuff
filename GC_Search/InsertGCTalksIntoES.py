import unittest
from unittest.mock import patch
from unittest.mock import Mock
from elasticsearch import Elasticsearch
import io
from FetchAllTalksForOneGC import FetchTalks



class IndexTalks:

    def __init__(self):
        self.ft = FetchTalks()

    def FetchTalksAndIndexThem(self, url):
        talkHandles = self.ft.FetchTalks(url)
        ##for handle in talkHandles:
            


class IndexTalksTest(unittest.TestCase):

    def setUp(self):
        self.it = IndexTalks()

    def test_FetchTalks_IndexThemOneByOne(self):
        talkUrl = 'https://www.lds.org/general-conference/2014/10/welcome-to-conference?lang=eng'
        talkHandles = []
        talkHandles.append(io.StringIO('some talk\'s content'))
        self.it.ft.FetchTalks = Mock(return_value=talkHandles)
        self.it.FetchTalksAndIndexThem(talkUrl)
        self.it.ft.FetchTalks.assert_called_once_with(talkUrl)
