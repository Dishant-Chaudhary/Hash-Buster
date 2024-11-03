#!/usr/bin/env python3
import threading
import argparse
from termcolor import colored
import hashlib
import sys
import os

colls = os.get_terminal_size().columns


class Cracker():
    def __init__(self, hash:str, wordlistPath:str, threads:int, mode:str) -> None:
        self.hash = hash
        self.wordlist = self._readFileLines(wordlistPath)
        self.l = len(self.wordlist)
        self.threads = threads
        self.found = False
        self.count = 0
        self.t:list[threading.Thread] = []
        self.cracked = ""
        self.mode = mode
    
    def _readFileLines(self, path:str):
        with open(path, "rb") as f:
            data = [x.strip() for x in f.read().splitlines()]
            f.close()
        return data
    
    def _compare(self, w:bytes):
        self.count += 1
        if hashlib.new(self.mode, w).hexdigest() == self.hash:
            self.found = True
            self.cracked = w
            return True
        return False
    
    def split(self, a, n):
        k, m = divmod(len(a), n)
        return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))
    
    def _run(self, wordlist:list[bytes]):
        for w in wordlist:
            if self.found == True:
                break
            w = str(w)[2:-1].encode()
            if w.startswith(b"#"):
                continue
            showPass = colored((w[:4]).decode(), "yellow", attrs=['bold'])
            precent = str(self.count/self.l*100)
            precent = precent[:precent.index(".")+3]
            sys.stdout.write(f"Comparing {showPass}... |  {self.count} <=> {precent}%\r")
            sys.stdout.flush()
            if self._compare(w):
                break

    def start(self):
        self.wordlist = self.split(self.wordlist, self.threads)
        for w in self.wordlist:
            t = threading.Thread(target=self._run, args=(w, ))
            t.daemon = True
            self.t.append(t)
            t.start()
        self.t[-1].join()
        w = colored(str(self.cracked)[2:-1], "green", attrs=['bold'])
        print("\n"+"-"*(int(colls/2)-3)+"Results"+"-"*(int(colls/2)-3), flush=True)
        for t in self.t:
            t.join()
        if self.cracked == "":
            print(colored("\n\nPassword was not cracked, try expending the wordlist.", "red"))
        else:
            print(colored("\nCracked!\npassword: ","green", attrs=['dark'])+ w)
        print(colored("Done!", "green"))
        exit(0)

                

def getArgs():
    parser = argparse.ArgumentParser(description="available types:\n"+str(hashlib.algorithms_available))
    parser.add_argument("hash", type=str, help="Hash to crack.")
    parser.add_argument("-w", "--wordlist", required=True, type=str, help="Specify the wordlist.")
    parser.add_argument("-t", "--threads", type=int, default=10, dest="threads", help="use threads")
    parser.add_argument("-m", "--mode", type=str, default="md5", dest="mode", help="Specify the hash type | md5")
    return parser.parse_args()

def main():
    try:
        args = getArgs()
        if not args.mode in hashlib.algorithms_available:
            print(f"The hash type {args.mode} is not available")
            exit(0)
        print("-"*(int(colls/2)-6)+"Hash Cracker"+"-"*(int(colls/2)-6))
        print()
        print("Hash >> "+colored(args.hash, "cyan"))
        print("Wordlist >> "+colored(args.wordlist, "cyan"))
        print("Running Jobs >> "+colored(args.threads, "cyan"))
        print("Hash type >> "+colored(args.mode, "cyan"))
        print()
        print("-"*(int(colls/2)-3)+"Running"+"-"*(int(colls/2)-3))
        c = Cracker(args.hash, args.wordlist, args.threads, args.mode)
        c.start()
    except KeyboardInterrupt:
        print(colored("\nStopping threads...", "red"))
        c.found = True
        for t in c.t:
            t.join()
        print("shava")
if __name__ == '__main__':
    main()