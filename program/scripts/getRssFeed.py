import feedparser
import random
from pathlib import Path

def loadRSSList(path): #pegar a lista lá
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def getNews():
    titlesNews = []

    base_dir = Path(__file__).resolve().parent
    rss_path = base_dir.parent / "fontsNews" / "news_PTBR.txt"

    rss_list = loadRSSList(rss_path)

    if not rss_list:
        return []

    urls = random.sample(rss_list, k=min(5, len(rss_list))) #ao invés do choice, usarei o sample, evitar duplicatas
    #print("Feeds selecionados:") #colocando por controle por enquanto
    #for url in urls:
    #    print(url)

    for url in urls:
        #feed = feedparser.parse(url)
        feed = feedparser.parse(url, request_headers={'User-Agent': 'Mozilla/5.0'})
        if feed.bozo:
            #print("Erro:", feed.bozo_exception) #haha, bozo
            continue

        for entry in feed.entries:
            if hasattr(entry, "title"):
                titlesNews.append(entry.title)


    random.shuffle(titlesNews)  

    return titlesNews[:30]





