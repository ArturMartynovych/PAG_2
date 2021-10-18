import requests
from bs4 import BeautifulSoup
from collections import Counter
from string import punctuation

r = requests.get("https://pl.wikipedia.org/wiki/Polska")
soup = BeautifulSoup(r.content, features="html.parser")

paragraphText = (''.join(s.findAll(text=True))for s in soup.findAll('p'))
countP = Counter((x.rstrip(punctuation).lower() for y in paragraphText for x in y.split()))

divText = (''.join(s.findAll(text=True))for s in soup.findAll('div'))
countDiv = Counter((x.rstrip(punctuation).lower() for y in divText for x in y.split()))

allWords = countDiv + countP
totalSorted = sorted(allWords.items(), key=lambda item: (-item[1], item[0]))

print(totalSorted)
