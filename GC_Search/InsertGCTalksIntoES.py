import unittest
from unittest.mock import patch
from unittest.mock import Mock
from elasticsearch import Elasticsearch
import io
from FetchAllTalksForOneGC import FetchTalks
from FetchAllTalksForOneGC import HtmlTagParser
import json



class IndexTalks:

    index_name = 'gc-index'
    doc_type = 'talk'

    def __init__(self):
        self.ft = FetchTalks()
        self.es = Elasticsearch()
        self.es_id_seq = 0
        self.confId = ''

    def FetchTalksAndIndexThem(self, url):
        self.confId, talkHandles = self.ft.FetchTalks(url)
        print(str.format('confId: {}, num talk hanldes: {}', self.confId, len(talkHandles)))
        for handle in talkHandles:
            self._InsertOneTalkIntoES(handle)

    def _GetNextId(self):
        result = self.es_id_seq
        self.es_id_seq = self.es_id_seq + 1
        return result

    def _GetTitleAndAuthor(self, line, tag, tagIndex):
        titleString = HtmlTagParser.GetTagContents(tag, line, tagIndex)
        titleSegments = titleString.split(' - By ')
        title = titleSegments[0]
        author = titleSegments[1]
        return ( title, author )

    def _GetTitleAuthorContent(self, talkHandle):
        title = ''
        author = ''
        titleOpenTag = '<title>'
        titleFound = False
        talkContent = ''
        for line in talkHandle:
            strLine = str(line)
            talkContent = talkContent + strLine
            if titleFound == False:
                titleIndex = strLine.find(titleOpenTag)
                if titleIndex != -1:
                    title, author = self._GetTitleAndAuthor(strLine, titleOpenTag, titleIndex)
                    titleFound = True
        return ( title, author, talkContent )

    def _InsertOneTalkIntoES(self, talkHandle):
        title, author, talkContent = self._GetTitleAuthorContent(talkHandle)
        json_body = json.dumps({'title': title, 'author': author, 'confid': self.confId, 'content': talkContent})
        idnum = self._GetNextId()
        print('indexing doc num: ' + str(idnum))
        self.es.index(index=self.index_name, doc_type=self.doc_type, id=idnum, body=json_body)



class IndexTalksTest(unittest.TestCase):

    htmlContent = """<html>
                    <title>Welcome to Conference - By President Thomas S. Monson</title>
                    </html>"""

    confId = 'October 2014'

    def setUp(self):
        self.it = IndexTalks()

    def test_InsertOneTalkIntoES_ESApiCalled(self):
        json_body = json.dumps({'title': 'Welcome to Conference', 'author': 'President Thomas S. Monson', 'confid': self.confId, 'content': self.htmlContent})
        talkHandle = io.StringIO(self.htmlContent)
        self.it.confId = self.confId
        with patch.object(Elasticsearch, 'index', return_value=None) as mock_method:
            self.it._InsertOneTalkIntoES(talkHandle)
        mock_method.assert_called_once_with(index=self.it.index_name, doc_type=self.it.doc_type, id=self.it._GetNextId()-1, body=json_body)

    def test_FetchTalks_IndexThemOneByOne(self):
        talkUrl = 'https://www.lds.org/general-conference/2014/10/welcome-to-conference?lang=eng'
        talkHandles = []
        talkHandles.append(io.StringIO('some talk\'s content'))
        self.it.ft.FetchTalks = Mock(return_value= ( self.confId, talkHandles ))
        self.it._InsertOneTalkIntoES = Mock(return_value=None)
        self.it.FetchTalksAndIndexThem(talkUrl)
        self.it.ft.FetchTalks.assert_called_once_with(talkUrl)
        self.it._InsertOneTalkIntoES.assert_called_once_with(talkHandles[0])
        
