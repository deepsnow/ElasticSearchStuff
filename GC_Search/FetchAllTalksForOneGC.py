import unittest
from unittest.mock import patch
from unittest.mock import Mock
import urllib.request
import io



class FetchTalks:

    def _FetchPage(self, url):
        return urllib.request.urlopen(url)

    def _GetTalkLink(self, line):
        talkTag = '<span class="talk">'
        talkTag_index = line.find(talkTag)
        if talkTag_index != -1:
            linkStart_index = line.find('"', talkTag_index + len(talkTag))
            linkEnd_index = line.find('"', linkStart_index + 1)
            return(line[linkStart_index + 1:linkEnd_index])
        else:
            return None
                
    def _FindTalkLinksInPage(self, pageHandle):
        talkLinks = []
        for line in pageHandle:
            str_line = str(line)
            str_link = self._GetTalkLink(str_line)
            if str_link != None:
                talkLinks.append(str_link)
        return talkLinks

    def _FetchWeekenSummaryPage(self, url):
        return self._FetchPage(url)

    def _FetchIndividualTalk(self, url):
        return self._FetchPage(url)

    def FetchTalks(self, weekendUrl):
        handlesToTalks = []
        summaryPageHandle = self._FetchWeekenSummaryPage(weekendUrl)
        linksToTalks = self._FindTalkLinksInPage(summaryPageHandle)
        for link in linksToTalks:
            handlesToTalks.append(self._FetchIndividualTalk(link))
        return handlesToTalks


class FetchTalksTest(unittest.TestCase):

    htmlContent = """<html>
                    <table>
                    <tr>
                    <td>
                    <span class="talk"><a href="https://www.lds.org/general-conference/2014/10/welcome-to-conference?lang=eng">Welcome to Conference</a></span>
                    <span class="speaker">By President Thomas S. Monson</span>
                    </td>
                    </tr>
                    <tr>
                    <td>
                    <span class="talk"><a href="https://www.lds.org/general-conference/2014/10/the-reason-for-our-hope?lang=eng">The Reason for Our Hope</a></span>
                    <span class="speaker">By President Boyd K. Packer</span>
                    </td>
                    </tr>
                    </table>
                    </html>"""

    def setUp(self):
        self.ft = FetchTalks()

    def test_FetchPage_OneUrlRequestMade(self):
        talkUrl = 'https://www.lds.org/general-conference/2014/10/welcome-to-conference?lang=eng'
        with patch.object(urllib.request, 'urlopen', return_value=None) as mock_method:
            self.ft._FetchWeekenSummaryPage(talkUrl)
        mock_method.assert_called_once_with(talkUrl)

    def test_FindTalkLinksInPage_AllTalkLinksFound(self):
        linksToTalks = self.ft._FindTalkLinksInPage(io.StringIO(self.htmlContent))
        self.assertEqual(len(linksToTalks), 2)
        self.assertEqual(linksToTalks[0], 'https://www.lds.org/general-conference/2014/10/welcome-to-conference?lang=eng')
        self.assertEqual(linksToTalks[1], 'https://www.lds.org/general-conference/2014/10/the-reason-for-our-hope?lang=eng')

    def test_FetchTalks_ReqSummaryParseItThenReqAllTalks(self):
        weekendUrl = 'https://www.lds.org/general-conference/sessions/2014/10?lang=eng'
        wHandle = io.StringIO(self.htmlContent)
        talkLinks = []
        talkLinks.append('https://www.lds.org/general-conference/2014/10/welcome-to-conference?lang=eng')
        self.ft._FetchWeekenSummaryPage = Mock(return_value=wHandle)
        self.ft._FindTalkLinksInPage = Mock(return_value=talkLinks)
        self.ft._FetchIndividualTalk = Mock(return_value=io.StringIO('some talk\'s content'))
        self.ft.FetchTalks(weekendUrl)
        self.ft._FetchWeekenSummaryPage.assert_called_with(weekendUrl)
        self.ft._FindTalkLinksInPage.assert_called_once_with(wHandle)
        self.ft._FetchIndividualTalk.assert_called_with(talkLinks[0])
