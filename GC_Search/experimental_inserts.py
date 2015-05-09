from InsertGCTalksIntoES import IndexTalks

def main():
    url = 'https://www.lds.org/general-conference/sessions/2014/10?lang=eng'
    indexer = IndexTalks()
    indexer.FetchTalksAndIndexThem(url)

if __name__ == '__main__':
    main()
