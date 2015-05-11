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
            ahrefIndex = line.find('<a href=', talkTag_index + len(talkTag))
            if ahrefIndex == -1:
                return None
            linkStart_index = line.find('"', talkTag_index + len(talkTag))
            linkEnd_index = line.find('"', linkStart_index + 1)
            return(line[linkStart_index + 1:linkEnd_index])
        else:
            return None
                
    def _FindConfIdAndTalkLinksInPage(self, pageHandle):
        confId = ''
        talkLinks = []
        titleFound = False
        for line in pageHandle:
            str_line = str(line)
            if titleFound == False:
                confId = self._FindConfId(str_line)
                if confId != '':
                    titleFound = True
            str_link = self._GetTalkLink(str_line)
            if str_link != None:
                talkLinks.append(str_link)
        return ( confId, talkLinks )

    def _FetchWeekenSummaryPage(self, url):
        return self._FetchPage(url)

    def _FetchIndividualTalk(self, url):
        return self._FetchPage(url)

    def _FindConfId(self, strLine):
        confId = ''
        titleOpenTag = '<title>'
        titleIndex = strLine.find(titleOpenTag)
        if titleIndex != -1:
            titleString = HtmlTagParser.GetTagContents(titleOpenTag, strLine)
            titleSegments = titleString.split(' ')
            confId = titleSegments[0] + ' ' + titleSegments[1]
            titleFound = True
        return confId

    def FetchTalks(self, weekendUrl):
        handlesToTalks = []
        summaryPageHandle = self._FetchWeekenSummaryPage(weekendUrl)
        confId, linksToTalks = self._FindConfIdAndTalkLinksInPage(summaryPageHandle)
        print('num talks: ' + str(len(linksToTalks)))
        for link in linksToTalks:
            print(link)
            handlesToTalks.append(self._FetchIndividualTalk(link))
        return (confId, handlesToTalks)


class FetchTalksTest(unittest.TestCase):

    htmlContent = """<html>
                    <title>October 2014 LDS General Conference Talks</title>
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
                    <tr>
                    <td>
                    <span class="talk">Video Presentation: The Holy Temple</span>
                    <span class="speaker">The Church of Jesus Christ of Latter-day Saints</span>
                    </td>
                    </tr>
                    </table>
                    </html>"""

    confId = 'October 2014'

    def setUp(self):
        self.ft = FetchTalks()

    def test_FetchWeekenSummaryPage_OneUrlRequestMade(self):
        talkUrl = 'https://www.lds.org/general-conference/2014/10/welcome-to-conference?lang=eng'
        with patch.object(urllib.request, 'urlopen', return_value=None) as mock_method:
            self.ft._FetchWeekenSummaryPage(talkUrl)
        mock_method.assert_called_once_with(talkUrl)

    def test_FetchPage_OneUrlRequestMade(self):
        talkUrl = 'https://www.lds.org/general-conference/2014/10/welcome-to-conference?lang=eng'
        with patch.object(urllib.request, 'urlopen', return_value=None) as mock_method:
            self.ft._FetchIndividualTalk(talkUrl)
        mock_method.assert_called_once_with(talkUrl)

    def test_FindConfId_TitleTagSearched(self):
        confId = self.ft._FindConfId('<title>October 2014 LDS General Conference Talks</title>')
        self.assertEqual(confId, self.confId)

    def test_FindConfIdAndTalkLinksInPage_AllTalkLinksFound(self):
        confId, linksToTalks = self.ft._FindConfIdAndTalkLinksInPage(io.StringIO(self.htmlContent))
        self.assertEqual(len(linksToTalks), 2)
        self.assertEqual(linksToTalks[0], 'https://www.lds.org/general-conference/2014/10/welcome-to-conference?lang=eng')
        self.assertEqual(linksToTalks[1], 'https://www.lds.org/general-conference/2014/10/the-reason-for-our-hope?lang=eng')
        self.assertEqual(confId, self.confId)

    def test_FetchTalks_ReqSummaryParseItThenReqAllTalks(self):
        weekendUrl = 'https://www.lds.org/general-conference/sessions/2014/10?lang=eng'
        wHandle = io.StringIO(self.htmlContent)
        talkLinks = []
        talkLinks.append('https://www.lds.org/general-conference/2014/10/welcome-to-conference?lang=eng')
        self.ft._FetchWeekenSummaryPage = Mock(return_value=wHandle)
        self.ft._FindConfId = Mock(return_value=self.confId)
        self.ft._FindConfIdAndTalkLinksInPage = Mock(return_value=( self.confId, talkLinks ))
        self.ft._FetchIndividualTalk = Mock(return_value=io.StringIO('some talk\'s content'))
        self.ft.FetchTalks(weekendUrl)
        self.ft._FetchWeekenSummaryPage.assert_called_with(weekendUrl)
        self.ft._FindConfIdAndTalkLinksInPage.assert_called_once_with(wHandle)
        self.ft._FetchIndividualTalk.assert_called_with(talkLinks[0])


class HtmlTagParser:

    def GetTagContents(tag, line, tagIndex = -1):
        contents = ''
        if tagIndex == -1:
            tagIndex = line.find(tag)
        if tagIndex != -1:
            tagStartIndex = tagIndex + len(tag)
            tagEndIndex = line.find('<', tagStartIndex + 1)
            contents = line[tagStartIndex:tagEndIndex]
        return contents


class HtmlTagParserTest(unittest.TestCase):

    def test_GetTagContents(self):
        htmlStr = '<title>October 2014 LDS General Conference Talks</title>'
        tag = '<title>'
        tagContent = HtmlTagParser.GetTagContents(tag, htmlStr)
        self.assertEqual(tagContent, 'October 2014 LDS General Conference Talks')
