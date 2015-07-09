from FetchAllGCEditions import FetchEditions
from InsertGCTalksIntoES import IndexTalks

def main():  
    indexer = IndexTalks()
    archiveUrl = 'https://www.lds.org/general-conference/conferences?lang=eng'
    finder = FetchEditions()
    editionUrls = finder.FetchEditions(archiveUrl)
    for editionUrl in editionUrls:
        print('GC: ' + editionUrl)
        indexer.FetchTalksAndIndexThem(editionUrl)

if __name__ == '__main__':
    main()
