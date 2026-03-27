from getRssFeed import getNews
from pathlib import Path
import random
import re
import unicodedata

base_dir = Path(__file__).resolve().parent
words_dir = base_dir.parent / "wordsData"
caminho = words_dir / "sensibleThemes_PTBR.txt" # deixar em português essa varivel :v


# carregamentos :D
def loadSensibleThemes(path):
    with open(path, 'r', encoding='utf-8') as f:
        return [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        ]


# teste de novo filtro
def cleanSensibleNews(news_list, sensible_words):
    clean = []

    # normaliza a lista de palavras sensíveis
    patterns = [
        re.compile(rf'\b{re.escape(normalize(word))}\b')
        for word in sensible_words
    ]

    for n in news_list:
        text = normalize(n)

        if not any(p.search(text) for p in patterns):
            clean.append(n)

    return clean


def normalize(text):
    text = text.lower()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return text


def loadWordLists():
    # pegar todos os Salt e colocar em listas
    def load(file_name):
        path = words_dir / file_name
        with open(path, 'r', encoding='utf-8') as f:
            return [
                l.strip()
                for l in f
                if l.strip() and not l.strip().startswith("#")
            ]

    return {
        "adjectives": load("saltWordsAdjectives_PTBR.txt"),
        "chars": load("saltWordsChars_PTBR.txt"),
        "free": load("saltWordsFree_PTBR.txt"),
        "objects": load("saltWordsObjects_PTBR.txt"),
        "places": load("saltWordsPlaces_PTBR.txt"),
    }


# função de cortes com RE, não sei como, só sei que é assim
def smartCut(title):
    # tenta cortar em vírgula, dois pontos ou "que"

    # 1. tenta cortar por pontuação
    parts = re.split(r',|:|-', title)
    if len(parts) > 1:
        return parts[0], " ".join(parts[1:])

    # 2. tenta cortar por conectivos comuns
    parts = re.split(r'\b(que|quando|após|enquanto)\b', title)
    if len(parts) > 2:
        return parts[0], "".join(parts[1:])

    # 3. fallback (corte simples)
    return cutTitles(title)


def cutTitles(title):
    words = title.split()
    if len(words) < 4:
        return title, ""

    middle = len(words) // 2
    return " ".join(words[:middle]), " ".join(words[middle:])


# estilistica
def applyNewsStyle(title):
    patterns = [
        "{}: entenda o caso",
        "{}; veja detalhes",
        "{} e gera reação",
        "{} e repercute nas redes",
        "{} e levanta debate",
        "{} surpreende especialistas",
        "{} chama atenção",
        "{} vira destaque",
    ]

    pattern = random.choice(patterns)
    return pattern.format(title)


def safeApply(func, title):
    try:
        result = func([title])
        if result:
            return result[0]
    except:
        pass
    return title


def finalizeTitle(title):  # isso é trabalho duplicado?
    title = re.sub(r'\s+', ' ', title)
    title = title.strip().capitalize()
    title = applyNewsStyle(title)
    return title


def makeNewNewsShuffle(news_list):
    # mistura noticias, usar recursões regulares para cortar elas bem no meio do titulo,
    # e depois conectar melhor com conectivos

    if len(news_list) < 2:
        return []

    '''connectors = [
        "e", "enquanto", "mas", "após", "depois que",
        "ao mesmo tempo", "enquanto isso", "porém", "além disso"
    ]''' #testar sem conctores

    new_news = []

    for _ in range(len(news_list)):
        n1, n2 = random.sample(news_list, 2)

        p1, _ = smartCut(n1)
        _, p2 = smartCut(n2)

        #connector = random.choice(connectors)

        # evita duplicação estranha de espaços
        #new_title = f"{p1} {connector} {p2}".strip()
        new_title = f"{p1} {p2}".strip()
        new_title = applyNewsStyle(new_title)

        new_news.append(new_title)

    return new_news


def makeNewNewsPlace(news_list, places):
    # pega as noticias e corta o final para botar em algum local da saltWordPlaces
    new_news = []

    for n in news_list:
        base, _ = cutTitles(n)
        place = random.choice(places)
        new_news.append(f"{base} em {place}")

    return new_news


def makeNewNewsAdjctives(news_list, adjectives):
    # pega as noticias e corta o final para botar um adjetivo, pode muito bem ser após um char
    new_news = []

    for n in news_list:
        words = n.split()
        if len(words) > 2:
            idx = random.randint(1, len(words) - 1)
            words.insert(idx, random.choice(adjectives))
        new_news.append(" ".join(words))

    return new_news


def makeNewNewsChars(news_list, chars):
    new_news = []

    # pega as noticias e corta o final para botar "com" ou "acompanhado" de um do char
    for n in news_list:
        base, _ = smartCut(n)  # corta antes de adicionar

        char = random.choice(chars)
        connector = ', ' + random.choice([
            "com", "acompanhado de", "diz", "segundo",
            "argumenta", "afirma", "diz especialista"
        ])

        new_news.append(f"{base} {connector} {char}")

    return new_news

def makeFakeStyleNews(news_list, chars, adjectives):
    # pega as noticias e mistura com estilo "fake" usando chars e adjetivos

    new_news = []

    if not news_list:
        return []

    if not chars or not adjectives:
        return []

    for n in news_list:
        adj = random.choice(adjectives)
        char = random.choice(chars)

        title = f"{n} e {adj} {char} aparece"

        title = applyNewsStyle(title)

        new_news.append(title)

    return new_news


def makePlotTwistNews(news_list):
    new_news = []

    for n in news_list:
        twist = random.choice([
            "mas ninguém esperava",
            "e tudo muda",
            "e surpreende",
            "e termina de forma inesperada",
            "e causa confusão",
        ])

        new_news.append(f"{n}, {twist}")

    return new_news


def makeDadaLikeNews(news_list):
    if len(news_list) < 2:
        return []

    word_pool = []

    for n in news_list:
        for w in n.lower().split():
            w = w.strip(".,:;!?()[]\"'")
            if len(w) > 3:
                word_pool.append(w)

    if not word_pool:
        return []

    for _ in range(10):
        common_word = random.choice(word_pool)

        matches = [
            n for n in news_list
            if common_word in n.lower().split()
        ]

        if len(matches) < 2:
            continue

        n1, n2 = random.sample(matches, 2)

        try:
            part1 = n1.lower().split(common_word)[0].strip()
            part2 = n2.lower().split(common_word)[-1].strip()

            return [applyNewsStyle(f"{part1} {common_word} {part2}")]
        except:
            continue

    return []


def makeFirstPartNews(news_list):
    if not news_list:
        return []

    connectors_pattern = r'\b(que|quando|após|depois que|enquanto|mas|porém|e|com|para)\b'

    new_news = []

    for n in news_list:
        parts = re.split(connectors_pattern, n, flags=re.IGNORECASE)

        if len(parts) > 1:
            first_part = parts[0].strip()
        else:
            parts = re.split(r'[,:-]', n)
            first_part = parts[0].strip()

        new_news.append(first_part)

    return new_news


def combineStyles(news_list, generators, wordLists):
    if len(news_list) < 2:
        return []

    base_generator = random.choice(generators)
    generated = base_generator()

    if not generated:
        return []

    title = random.choice(generated)

    extra_generators = [
        
        lambda t: makePlotTwistNews([t])[0],
        lambda t: makeNewNewsPlace([t], wordLists["places"])[0],
        lambda t: makeNewNewsChars([t], wordLists["chars"])[0],
        lambda t: makeFakeStyleNews([t], wordLists["chars"], wordLists["adjectives"])[0],
    ]

    for _ in range(random.randint(1, 3)):
        try:
            func = random.choice(extra_generators)
            title = func(title)
        except:
            pass

    return [title]


# Essa aqui vou botar para testar
def getOneNews():
    sensibleThemes = loadSensibleThemes(caminho)
    wordLists = loadWordLists()
    news = getNews()
    clean_news = cleanSensibleNews(news, sensibleThemes)

    desculpas = [
        "O estágiario cortou nossa internet!",
        "Jornalista encontrado procastinando em casa!",
        "Garfo encontrado na cozinha!",
        "Revolta das máquinas: Bot de notícias se recusa a trabalhar",
        "'tamo' de atestado",
        "tropeçaro nos cabos",
        "O que é lambimia?",
        "Revoltz",
        ":) Tenha um bom dia!",
        "Hackeram meu windows",
        "parem as máquinas!",
        "Jornalismo ou esquema de pirâmede? Descubra"
    ]

    if not clean_news:
        return random.choice(desculpas)

    if not wordLists["chars"] or not wordLists["places"]:
        return random.choice(desculpas)

    generators = [
        #lambda: makeDadaLikeNews(clean_news),
        #lambda: makeNewNewsShuffle(clean_news),
        #lambda: makeNewNewsShuffle(clean_news),
        #lambda: makeNewNewsShuffle(clean_news),
        #lambda: makeNewNewsShuffle(clean_news),
        #lambda: makeNewNewsShuffle(clean_news), #gambiarra, eu sei
        lambda: makeNewNewsChars(clean_news, wordLists["chars"]),
        #lambda: makeFirstPartNews(clean_news),
        # lambda: makePlotTwistNews(clean_news), # não tô gostando dos resultados
        #lambda: makeNewNewsPlace(clean_news, wordLists["places"]),
        lambda: combineStyles(
            clean_news,
            [
                lambda: makeDadaLikeNews(clean_news),
                lambda: makeNewNewsShuffle(clean_news)
            ],
            wordLists
        ),
        #lambda: makeFakeStyleNews(clean_news, wordLists["chars"], wordLists["adjectives"]),
    ]

    generated_list = random.choice(generators)()

    if not generated_list:
        return random.choice(desculpas)

    return random.choice(generated_list)