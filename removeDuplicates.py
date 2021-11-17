import hashlib
from finder import PrntScFinder

class SpamKiller:
    def __init__(self, verbose: bool=False) -> None:
        self.finder = PrntScFinder([], [])
        self.verbose = verbose
        self.database = []
    
    def loadUrls(self) -> list:
        f = open('urlSaver.txt', 'r')
        data = f.read()
        f.close()
        validURLs = []
        for u in data.split("\n"):
            if len(u) > 1: validURLs.append(u)
        return validURLs
    
    def removeURLs(self, allUrls:list, toDelete: list) -> None:
        toWrite = ""
        for u in allUrls:
            if u not in toDelete: toWrite += u+'\n'
        f = open('urlSaver.txt', 'w')
        f.write(toWrite[:-1])
        f.close()

    def erase(self) -> None:
        urls = self.loadUrls()
        dupes = []
        for u in urls:
            self.finder.url = u
            if self.verbose: print("[.] Analyzing URL:", u, "("+str(urls.index(u)+1)+"/"+str(len(urls))+")")
            imageURL = self.finder.getImageURL()
            if imageURL != None:
                imgData = self.finder.requestImageFrom(imageURL)
                if imgData != None:
                    imgHash = hashlib.sha256(imgData).hexdigest()
                    if imgHash not in self.database:
                        self.database.append(imgHash)
                    else:
                        dupes.append(u)
        self.removeURLs(urls, dupes)
        print(" >> Found and erased a total of", len(dupes), "duplicated images")

if __name__ == "__main__":
    killer = SpamKiller(verbose=True)
    killer.erase()