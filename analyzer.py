import os, time, sys
from pynput.keyboard import Key, Listener
from selenium.webdriver import Chrome

class URLAnalyzer:
    def __init__(self, verbose=False) -> None:
        self.bindings = {"PREV": ',', "NEXT": '.', "SAVE": '/'}
        self.outputFile = "FinalSavedURLs.txt"
        self.actionBuffer = []
        self.browser = Chrome()
        self.saveSkip = True
        self.verbose = verbose
    
    def _waitForAction(self) -> str:
        while len(self.actionBuffer) == 0: time.sleep(0.1)
        action = self.actionBuffer[0]
        del self.actionBuffer[0]
        return action

    def end(self, outputData: str) -> None:
        oldData = ""
        if os.path.exists(self.outputFile):
            f = open(self.outputFile, 'r')
            oldData = f.read()
            f.close()
        f = open(self.outputFile, 'w')
        f.write(oldData+"\n"*int(len(oldData)>0)+outputData)
        f.close()
        cmd = input("Do you want to delete all unsaved data? (y/n)\n > ")
        if cmd.lower()[0] == "y":
            f = open('urlSaver.txt', 'w')
            f.write('')
            f.close()
    
    def loadURLs(self) -> list:
        f = open('urlSaver.txt', 'r')
        data = f.read()
        f.close()
        validURLs = []
        for u in data.split("\n"):
            if len(u) > 1: validURLs.append(u)
        return validURLs

    def listenForKeyboardInput(self) -> None:
        def keyPressed(key):
            try:
                x = key.char
            except:
                return
            if key.char == self.bindings["PREV"]:
                self.actionBuffer.append("PREV")
            elif key.char == self.bindings["NEXT"]:
                self.actionBuffer.append("NEXT")
            elif key.char == self.bindings["SAVE"]:
                self.actionBuffer.append("SAVE")
        self.keyInput = Listener(on_press=keyPressed)
        self.keyInput.start()

    def analyze(self, userInterraction: bool=True):
        urls = self.loadURLs()
        saved = []
        self.listenForKeyboardInput()
        i = 0
        while True:
            if i > len(urls)-1: break
            u = urls[i]
            print(u)
            self.browser.get(u)
            a = self._waitForAction()
            if a == "PREV":
                print("PREV DETECTED!")
                i -= 1
            elif a == "NEXT":
                print("NEXT DETECTED!")
                i += 1
            elif a == "SAVE":
                saved.append(u)
                if self.verbose: print("[.] URL ("+u+") was saved!")
                if self.saveSkip: i += 1
        self.browser.stop_client()
        if userInterraction:
            self.end("\n".join(saved))
        else:
            return saved

if __name__ == "__main__":
    analyzer = URLAnalyzer(verbose=True)
    analyzer.analyze()