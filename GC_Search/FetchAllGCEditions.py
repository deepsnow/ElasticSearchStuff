import unittest
from unittest.mock import patch
from unittest.mock import Mock
import urllib.request
import io

class FetchEditions:

    def FetchEditions(self, archiveUrl):
        archiveHandle = self._FetchArchivePage(archiveUrl)
        return self._FetchEditionsUrls(archiveHandle)

    def _FetchEditionsUrls(self, archiveHandle):
        self.handlesToEditions = []
        reachedArchive = False
        for line in archiveHandle:
            str_line = str(line)
            if str_line.find('<h2>Conference Archive</h2>') > 0:
                reachedArchive = True
            if reachedArchive:
                endIndex = self._FindUrlOnLine(str_line, 0)
                self._FindUrlOnLine(str_line, endIndex) # some lines have two URLs
        return self.handlesToEditions

    def _FindUrlOnLine(self, str_line, callersIndex):
        urlPrefix = 'https://www.lds.org/general-conference/sessions'
        urlStartIndex = str_line.find(urlPrefix, callersIndex)
        if urlStartIndex > 0:
            urlEndIndex = str_line.find('"', urlStartIndex)
            #print(str(urlStartIndex) + "-" + str(urlEndIndex) + "-" + str_line)
            newUrl = str_line[urlStartIndex:urlEndIndex]
            print(newUrl)
            self.handlesToEditions.append(newUrl)
            return urlEndIndex

    def _FetchArchivePage(self, url):
        return urllib.request.urlopen(url)

class FetchEditionsTest(unittest.TestCase):

    htmlContent = """<html>
                    <title>General Conference Sessions - Archive of Previous Conferences</title>
                    <div class="archive-by-year-list">
                    <h2>Conference Archive</h2>
                    <ul>
                    <li><a href="#">2015</a>
                    <ul class="menu-list click-menu" style="display: none;">
                    <li><a href="https://www.lds.org/general-conference/sessions/2015/04?lang=eng">April</a></li>
                    </ul>
                    </li>
                    <li><a href="#">2014</a>
                    <ul class="menu-list click-menu" style="display: none;">
                    <li><a href="https://www.lds.org/general-conference/sessions/2014/10?lang=eng">October</a></li><li><a href="https://www.lds.org/general-conference/sessions/2014/04?lang=eng">April</a></li>
                    </ul>
                    </li>
                    </ul>
                    </div>
                    </html>"""

    def setUp(self):
        self.fe = FetchEditions()
        self.archiveUrl = 'https://www.lds.org/general-conference/conferences?lang=eng'

    def test_FetchArchivePage_OneUrlRequestMade(self):
        with patch.object(urllib.request, 'urlopen', return_value=None) as mock_method:
            self.fe._FetchArchivePage(self.archiveUrl)
        mock_method.assert_called_once_with(self.archiveUrl)

    def test_FetchEditionsUrls_LoneUrlFoundAndReturned(self):
        urls = self.fe._FetchEditionsUrls(io.StringIO(self.htmlContent))
        self.assertEqual(urls[0], 'https://www.lds.org/general-conference/sessions/2015/04?lang=eng')
        self.assertEqual(urls[1], 'https://www.lds.org/general-conference/sessions/2014/10?lang=eng')
        self.assertEqual(urls[2], 'https://www.lds.org/general-conference/sessions/2014/04?lang=eng')
        self.assertEqual(len(urls), 3)
