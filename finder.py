import random, requests, re, pytesseract, time, threading, os
from string import ascii_lowercase as allLetters
from nudenet import NudeClassifier
from sys import argv

allowedCharacters = list("0123456789"+allLetters)
headers = {
    "ACCEPT" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "ACCEPT-LANGUAGE": "en-US,en;q=0.9",
    "DEVICE-MEMORY": "8",
    "DOWNLINK": "10",
    "DPR": "1",
    "ECT": "4g",
    "HOST": "prnt.sc",
    "REFERER": "https://www.google.com/",
    "RTT": "50",
    "SEC-FETCH-DEST": "document",
    "SEC-FETCH-MODE": "navigate",
    "SEC-FETCH-SITE": "cross-site",
    "SEC-FETCH-USER": "?1",
    "UPGRADE-INSECURE-REQUESTS": "1",
    "USER-AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    "VIEWPORT-WIDTH": "1920",
}
headers2 = {
    "accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-ch-ua": '"Chromium";v="94", " Not A;Brand";v="99", "Opera GX";v="80"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "UPGRADE-INSECURE-REQUESTS": "1",
    "USER-AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    "VIEWPORT-WIDTH": "1920",
}

class PrntScFinder:
    def __init__(self, keywords: list, blackList: list, saveNudes: bool=False, threads: int=1, autoUrl: bool=True, trackNetworkUsage: bool=False, verbose: bool=False) -> None:
        if autoUrl: self.url = self.generateURL(new=True)
        else: self.url = None
        self.keywords = keywords
        self.blacklist = blackList
        self.searchQuery = [
            "https://i.*jpg\" cross",  "https://i.*png\" cross",  "https://i.*jpeg\" cross",
        ]
        self.noSsQuery = "src=.*prntscr.*png\""
        self.verbose = verbose
        self.outputBuffer = []
        self.threadCount = threads
        self.trackUsage = trackNetworkUsage
        self.totalDownloadSize = 0
        self.threads = []
        self.running = True
        self.errors = 0
        self.found = 0
        self.saveNudes = saveNudes
        if self.saveNudes: self.nudeAnalyzer = NudeClassifier()
    
    def _outputThread(self, runOnce: bool=False) -> None:
        if not os.path.exists('./urlSaver.txt'):
            f = open('urlSaver.txt', 'w')
            f.write('')
            f.close()
        while self.running:
            if len(self.outputBuffer) > 0:
                writed = self.outputBuffer.copy()
                f = open('urlSaver.txt', 'r')
                oldData = f.read()
                f.close()
                f = open('urlSaver.txt', 'w')
                f.write(oldData+'\n'*int(len(oldData)>0)+'\n'.join(writed))
                f.close()
                for data in writed: del self.outputBuffer[self.outputBuffer.index(data)]
            if runOnce:
                return
            time.sleep(0.5)

    def _error(self, errorMsg, kill=False) -> None:
        print("[!] Error:", errorMsg)
        if kill: exit()

    def _formatBytes(self, size):
        n = 0
        power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
        while size > 1024:
            size /= 1024
            n += 1
        return str(round(size, 1))+" "+power_labels[n]+'B'

    def generateURL(self, new=False) -> str:
        if new:
            url = "https://prnt.sc/"+random.choice(allowedCharacters)+random.choice(allowedCharacters)+random.choice(allowedCharacters)+random.choice(allowedCharacters)+random.choice(allowedCharacters)+random.choice(allowedCharacters)
            while url.count("0")+url.count("1")+url.count("2")+url.count("3")+url.count("4")+url.count("5")+url.count("6")+url.count("7")+url.count("8")+url.count("9") == 0:
                url = "https://prnt.sc/"+random.choice(allowedCharacters)+random.choice(allowedCharacters)+random.choice(allowedCharacters)+random.choice(allowedCharacters)+random.choice(allowedCharacters)+random.choice(allowedCharacters)
            return  url
        else:
            for i in range(1, len(self.url)+1):
                if self.url[-i] != allowedCharacters[-1]:
                    return self.url[:-i]+allowedCharacters[allowedCharacters.index(self.url[-i])+1]+allowedCharacters[0]*(i-1)
            return self.generateURL(new=True)
    
    def getImageURL(self, url=None) -> str or None:
        if url == None: url = self.url
        # print("ImageURL from", url)
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            self._error("(imageURL) >> status code expected '200', got:", r.status_code)
            self.errors += 1
            return None
        if self.trackUsage: self.totalDownloadSize += len(r.text)
        for search in self.searchQuery:
            results = re.findall(search, r.text)
            if len(results) > 0: return results[0][:-7]
        if len(re.findall(self.noSsQuery, r.text)) > 0:
            return None
        self._error("(imageURL) >> No valid image URL was found")
        self.errors += 1
        return None
    
    def requestImageFrom(self, url) -> bytes or None:
        for _ in range(5):
            r = requests.get(url, headers=headers2)
            if r.status_code == 200:
                break
            else:
                time.sleep(1)
        if r.status_code != 200:
            self._error("(image) >> status code expected '200', got: "+str(r.status_code))
            self.errors += 1
            return None
        if self.trackUsage: self.totalDownloadSize += len(r.content)
        return r.content
    
    def analyzeImage(self, fileName, url=None) -> None:
        if url == None: url = self.url
        try:
            text = (pytesseract.image_to_string(fileName)).replace("\n", "").lower()
        except:
            self._error("Failed to read from image (invalid characters in image)")
            return
        if any(keyword in text for keyword in self.keywords) and not any(blacklistedWord in text for blacklistedWord in self.blacklist):
            self.found += 1
            print("[^] Found valid URL! ("+url+") ("+str(self.found)+")")
            self.outputBuffer.append(url)
        elif self.saveNudes:
            results = self.nudeAnalyzer.classify(fileName)
            if results[fileName]["unsafe"] > 0.5:
                self.found += 1
                print("[*] Found nude URL! ("+url+") ("+str(self.found)+")")
                self.outputBuffer.append(url)
        self.errors = 0

    def search(self, threadNumber:int=-1) -> None:
        prefix = "[.]"
        if threadNumber >= 0:
            prefix = "["+str(threadNumber)+"]"
        while self.running:
            self.url = url = self.generateURL()
            if self.verbose:
                if self.trackUsage: print(prefix, "Scanning URL:", url, "(NETWORK:", self._formatBytes(self.totalDownloadSize)+")")
                else: print(prefix, "Scanning URL:", url)
            imageURL = self.getImageURL(url=url)
            if imageURL != None:
                if threadNumber >= 0: imageName = "temp"+str(threadNumber)+"."+imageURL[-4:].replace(".", "")
                else: imageName = "temp"+"."+imageURL[-4:].replace(".", "")
                imgData = self.requestImageFrom(imageURL)
                if imgData != None:
                    f = open(imageName, 'wb')
                    f.write(imgData)
                    f.close()
                    self.analyzeImage(imageName, url=url)
                    os.remove(imageName)
    
    def run(self) -> None:
        self.running = True
        oThread = threading.Thread(target=self._outputThread)
        oThread.start()
        self.threads.append(oThread)
        if self.threadCount > 1:
            for tn in range(self.threadCount):
                t = threading.Thread(target=self.search, args=(tn,))
                t.start()
                self.threads.append(t)
            try:
                while True:
                    if self.errors > 10:
                        self.url = self.generateURL(new=True)
                    time.sleep(1)
            except KeyboardInterrupt: print("Exiting...")
        else:
            try: self.search()
            except KeyboardInterrupt: print("Exiting...")
        self.running = False
        for t in self.threads: t.join()
        if len(self.outputBuffer) > 0: self._outputThread(runOnce=True)

if __name__ == "__main__":
    verbose, findNudes, threads, tesseractPath = False, False, 3, "C:\\Program Files\\Tesseract-OCR\\tesseract"
    if "-h" in argv:
        print("\n > '-h' -> help menu\n > '-v' -> enable verbose\n > '-n' -> save nudes\n > '-t <THREAD_NUMBER>' -> run on ... threads\n > '-te <PATH>' -> set the tesseract path\n")
    if "-v" in argv or "--verbose" in argv:
        verbose = True
    if "-n" in argv or "--nudes" in argv:
        findNudes = True
    for opt in ["-t", "--threads"]:
        if opt in argv:
            threads = int(argv[argv.index(opt)+1])
            break
    for opt in ["-te", "--tesseract"]:
        if opt in argv:
            tesseractPath = argv[argv.index(opt)+1]
            break
    pytesseract.pytesseract.tesseract_cmd = tesseractPath
    finder = PrntScFinder(threads=6, trackNetworkUsage=True, saveNudes=findNudes, keywords=["crypto", "btc", "bank", "password", "credit card", "card details", "card number"], blackList=["bit-king", "bit-trading", "bit-trade", "jiratrade", "coinbascet"], verbose=verbose)
    finder.run()
    exit("Done")
