import unittest
from unittest.mock import patch
from unittest.mock import Mock
from elasticsearch import Elasticsearch
import io
from FetchAllTalksForOneGC import FetchTalks
from FetchAllTalksForOneGC import HtmlTagParser
import json
import urllib.request


class IndexTalks:

    index_name = 'gc'
    doc_type = 'talk'

    def __init__(self):
        self.ft = FetchTalks()
        self.es = Elasticsearch()
        self.es_id_seq = 0
        self.confId = ''

    def _FetchIndividualTalk(self, url):
        return urllib.request.urlopen(url)

    def FetchTalksAndIndexThem(self, weekendUrl):
        self.confId, talkUrls = self.ft.FetchTalks(weekendUrl)
        print(str.format('confId: {}, num talk urls: {}', self.confId, len(talkUrls)))
        for url in talkUrls:
            handle = self._FetchIndividualTalk(url)
            self._InsertOneTalkIntoES(handle, url)

    def _GetNextId(self):
        result = self.es_id_seq
        self.es_id_seq = self.es_id_seq + 1
        return result

    def _GetTitleAndAuthor(self, line, tag, tagIndex):
        titleString = HtmlTagParser.GetTagContents(tag, line, tagIndex)
        print('title string: ' + titleString)
        titleSegments = titleString.split('-')
        title = titleSegments[0].strip()
        author = titleSegments[1].strip()
        if author.find('By') == 0:
            author = author[3:].strip()
        return ( title, author )

    def _GetTitleAuthorContent(self, talkHandle):
        title = ''
        author = ''
        titleOpenTag = '<title>'
        titleFound = False
        talkContent = ''
        for line in talkHandle:
            #strLine = str(line)
            strLine = line.decode()
            talkContent = talkContent + strLine
            if titleFound == False:
                titleIndex = strLine.find(titleOpenTag)
                if titleIndex != -1:
                    title, author = self._GetTitleAndAuthor(strLine, titleOpenTag, titleIndex)
                    titleFound = True
        return ( title, author, talkContent )

    def _InsertOneTalkIntoES(self, talkHandle, talkUrl):
        title, author, talkContent = self._GetTitleAuthorContent(talkHandle)
        json_body = json.dumps({'title': title, 'author': author, 'confid': self.confId, 'content': talkContent, 'url': talkUrl})
        idnum = self._GetNextId()
        print('indexing doc num: ' + str(idnum))
        self.es.index(index=self.index_name, doc_type=self.doc_type, id=idnum, body=json_body)



class IndexTalksTest(unittest.TestCase):

    htmlContent = """<html>
                    <title>Welcome to Conference - By President Thomas S. Monson</title>
                    </html>"""

    confId = 'October 2014'
    talkUrl = 'https://www.lds.org/general-conference/2014/10/welcome-to-conference?lang=eng'

    def setUp(self):
        self.it = IndexTalks()

    def test_FetchPage_OneUrlRequestMade(self):
        talkUrl = 'https://www.lds.org/general-conference/2014/10/welcome-to-conference?lang=eng'
        with patch.object(urllib.request, 'urlopen', return_value=None) as mock_method:
            self.it._FetchIndividualTalk(talkUrl)
        mock_method.assert_called_once_with(talkUrl)

    def test_InsertOneTalkIntoES_ESApiCalled(self):
        json_body = json.dumps({'title': 'Welcome to Conference', 'author': 'President Thomas S. Monson', 'confid': self.confId, 'content': self.htmlContent, 'url': self.talkUrl})
        talkHandle = io.BytesIO(bytes(self.htmlContent, 'utf-8'))
        self.it.confId = self.confId
        with patch.object(Elasticsearch, 'index', return_value=None) as mock_method:
            self.it._InsertOneTalkIntoES(talkHandle, self.talkUrl)
        mock_method.assert_called_once_with(index=self.it.index_name, doc_type=self.it.doc_type, id=self.it._GetNextId()-1, body=json_body)

    def test_FetchTalks_IndexThemOneByOne(self):
        weekendUrl = 'https://www.lds.org/general-conference/sessions/2014/10?lang=eng'
        talkHandles = []
        talkHandles.append(io.StringIO('some talk\'s content'))
        self.it.ft.FetchTalks = Mock(return_value= ( self.confId, [ self.talkUrl ] ))
        self.it._InsertOneTalkIntoES = Mock(return_value=None)
        self.it._FetchIndividualTalk = Mock(return_value=talkHandles[0])
        self.it.FetchTalksAndIndexThem(weekendUrl)
        self.it.ft.FetchTalks.assert_called_once_with(weekendUrl)
        self.it._FetchIndividualTalk.assert_called_with(self.talkUrl)
        self.it._InsertOneTalkIntoES.assert_called_once_with(talkHandles[0], self.talkUrl)


    def test_GetTitleAndAuthor_ProperSplittingDone(self):
        tag = '<title>'
        title, author = self.it._GetTitleAndAuthor('<title>Filling Our Homes with Light and Truth -  By Cheryl A. Esplin </title>', tag, 0)
        self.assertEqual(title, 'Filling Our Homes with Light and Truth')
        self.assertEqual(author, 'Cheryl A. Esplin')
        title, author = self.it._GetTitleAndAuthor('<title>Welcome to Conference - By President Thomas S. Monson</title>', tag, 0)
        self.assertEqual(title, 'Welcome to Conference')
        self.assertEqual(author, 'President Thomas S. Monson')
        title, author = self.it._GetTitleAndAuthor('<title>Welcome to Conference - Thomas S. Monson</title>', tag, 0)
        self.assertEqual(title, 'Welcome to Conference')
        self.assertEqual(author, 'Thomas S. Monson')
        
        
