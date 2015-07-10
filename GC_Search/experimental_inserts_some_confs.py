from FetchAllGCEditions import FetchEditions
from InsertGCTalksIntoES import IndexTalks

def main():
    urls = []
    urls.append('https://www.lds.org/general-conference/sessions/2015/04?lang=eng')
    urls.append('https://www.lds.org/general-conference/sessions/2014/10?lang=eng')
    indexer = IndexTalks()
    for url in urls:
        indexer.FetchTalksAndIndexThem(url)

if __name__ == '__main__':
    main()
