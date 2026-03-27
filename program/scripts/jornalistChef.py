from .getRssFeed import getNews
from pathlib import Path
import random
import re
import unicodedata

#smells bad? Mas confia



base_dir = Path(__file__).resolve().parent
words_dir = base_dir.parent / "wordsData"
caminho = words_dir / "sensibleThemes_PTBR.txt" # deixar em português essa varivel :v
# carregamentos :D
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
'''def smartCut(title):
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
    return cutTitles(title)'''

def smartCut(title): #thanks copilot
    # Conectivos que naum podem ficar no final da primeira parte nem no início da segunda
    bad_words = r'\b(que|quando|pela|após|enquanto|com|de|do|da|dos|das|em|no|na|nos|nas|para|pro|pra|e|ou|mas|porém)\b'

    # 1. Tenta cortar por pontuação forte
    parts = re.split(r'[,:;]', title)
    if len(parts) > 1:
        p1, p2 = parts[0].strip(), " ".join(parts[1:]).strip()
        # Se a primeira parte terminar em "lixo", limpa
        p1 = re.sub(bad_words + r'\s*$', '', p1, flags=re.IGNORECASE).strip()
        return p1, p2

    # 2. Se não tem pontuação, corta no meio, mas foge das "bad_words"
    words = title.split()
    if len(words) < 4: return title, ""
    
    mid = len(words) // 2
    # Se a palavra do meio for um conectivo, pula ela
    if re.match(bad_words, words[mid-1], re.IGNORECASE):
        mid -= 1
        
    p1 = " ".join(words[:mid])
    p2 = " ".join(words[mid:])
    return p1, p2


def cutTitles(title):
    words = title.split()
    if len(words) < 4:
        return title, ""

    middle = len(words) // 2
    return " ".join(words[:middle]), " ".join(words[middle:])

def fixConnectiveCollisions(text):
    # Lista de substituições para conectivos grudados
    substitutions = [
        (r'\bcom\s+no\b', 'no'),        # "com no" -> "no"
        (r'\bcom\s+na\b', 'na'),        # "com na" -> "na"
        (r'\bcom\s+o\b', 'com o'),      # Garante espaço correto
        (r'\bem\s+no\b', 'no'),         # "em no" -> "no"
        (r'\bde\s+do\b', 'do'),         # "de do" -> "do"
        (r'\bpara\s+pro\b', 'pro'),     # "para pro" -> "pro"
        (r'\bcom\s+com\b', 'com'),      # "com com" -> "com"
        (r'\bque\s+que\b', 'que'),      # "que que" -> "que"
        (r'\bcom\s+em\b', 'em'),        # "com em" -> "em"
    ]
    
    for pattern, replacement in substitutions:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text


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
        "{}, veja as imagens",
        "{} #nuticia", 
        "{} s̵u̵d̷o̵ ̸a̸p̵t̴-̶g̸e̷t̵ ̵v̸i̸d̸a̴",
        "{} #getlife",
        "{} #bot",
        "{} #purenews",
        "{} #dadaismo",
        "{} 🔥🔥🔥🔥🔥",
        "{} 🔴",
        "{} 😨",
        "{} :P",
        "{} :O",
         "{} ¯\\_(ツ)_/¯",
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


def finalizeTitle(title):
    # 1. Remove espaços duplicados
    title = re.sub(r'\s+', ' ', title).strip()
    
    # 2. Limpeza de colisões (ex: "do em" -> "em")
    # Agora só remove se forem preposições grudadas, sem tocar na pontuação
    prep_collision = r'\b(com|de|do|da|em|no|na|para|por|e)\s+(com|de|do|da|em|no|na|para|por|e)\b'
    title = re.sub(prep_collision, r'\2', title, flags=re.IGNORECASE)
    
    # 3. Arruma o espaço das vírgulas (Garante "palavra, palavra")
    title = re.sub(r'\s+,', ',', title) # remove espaço antes
    title = re.sub(r',([^\s])', r', \1', title) # adiciona espaço depois se não tiver
    
    # 4. Remove preposição pendurada no FINAL (antes dos emojis/estilo)
    title = re.sub(r'\s+(com|de|do|da|em|no|na|para|e|o|a|os|as|que)$', '', title, flags=re.IGNORECASE)

    # 5. Capitalização
    if len(title) > 0:
        title = title[0].upper() + title[1:]
        
    return title

def isValidPart(text):
    if not text or len(text.split()) < 2:
        return False
    # Evita que a parte termine em conectivos que pedem complemento
    invalid_ends = r'\b(com|de|para|em|que|o|a|os|as|e|no|na)$'
    if re.search(invalid_ends, text.strip(), flags=re.IGNORECASE):
        return False
    return True

def makeNewNewsShuffle(news_list):
    if len(news_list) < 2: return []
    new_news = []

    for _ in range(len(news_list)):
        n1, n2 = random.sample(news_list, 2)
        p1, _ = smartCut(n1)
        _, p2 = smartCut(n2)

        if not isValidPart(p1) or not isValidPart(p2):
            continue

        # Adicionamos uma vírgula na união para dar ritmo
        new_title = f"{p1}, {p2}".strip()
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

    for n in news_list:
        base, _ = smartCut(n)

        # 🔥 valida base
        if not isValidPart(base):
            continue

        char = random.choice(chars)
        connector = ', ' + random.choice([
            "com", "acompanhado de", "diz", "segundo","diz","diz","diz","diz","diz","diz","diz",
            "argumenta", "afirma", "diz especialista",
            "complementa", "escreve", "posta","relata",
            "conclui", "comenta", "tweeta", "debocha"
        ])

        new_news.append(f"{base}{connector} {char}")

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
            "e mercado reage",
            "e mercado reage",
            "e mercado reage",
            "e mercado reage",
            "mas a que custo?",
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

    connectors_pattern = r'\b(que|quando|após|depois que|enquanto|mas|porém|e|com|para|,)\b'

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

    if not isValidPart(title): #tentar nao validar vazios
        return []

    extra_generators = [
        
        lambda t: makePlotTwistNews([t])[0],
        lambda t: makeNewNewsPlace([t], wordLists["places"])[0],
        lambda t: makeNewNewsChars([t], wordLists["chars"])[0],
        lambda t: makeFakeStyleNews([t], wordLists["chars"], wordLists["adjectives"])[0],
    ]

    for _ in range(random.randint(1, 3)):
        try:
            func = random.choice(extra_generators)
            new_title = func(title)

            if isValidPart(new_title):
                title = new_title
        except:
            pass
        
    if random.random() < 0.5:
        title = replaceConnectorsWithComma(title)
    title = re.sub(r'\s+', ' ', title)  # remove espaços duplicados
    title = re.sub(r'\s+,', ',', title)  # remove espaço antes de vírgula
    title = re.sub(r',\s*,', ',', title)  # remove vírgula dupla
    title = re.sub(r'\b(em|de|para|com)\s*,', ',', title)
    title = title.strip()

    return [title]

def endsBadly(text):
    text = re.sub(r'[^\w\s]$', '', text.strip())
    return re.search(r'\b(em|de|para|com)$', text.strip())

def replaceConnectorsWithComma(title):
    # Conectivos que viram vírgula (adicionamos mais alguns)
    connectors = [
        r'\s+e\s+', r'\s+mas\s+', r'\s+porém\s+', 
        r'\s+no entanto\s+', r'\s+contudo\s+', 
        r'\s+além disso\s+', r'\s+depois que\s+'
    ]

    for c in connectors:
        # Troca o conectivo por vírgula + espaço
        title = re.sub(c, ', ', title, flags=re.IGNORECASE)

    # Limpa vírgulas duplicadas (,,) e espaços extras antes da vírgula
    title = re.sub(r'\s*,\s*', ', ', title)
    title = re.sub(r',+', ',', title)

    return title.strip()

def splitByCommaStyle(title):
    parts = re.split(r'\s+e\s+|\s+mas\s+|\s+porém\s+|\s+e\s+', title)

    # limpa espaços
    parts = [p.strip() for p in parts if p.strip()]

    if len(parts) > 1:
        return ", ".join(parts)

    return title

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
        "Jornalismo ou esquema de pirâmede? Descubra",
        "Pix sumiu, servidor caiu"
    ]

    if not clean_news:
        return random.choice(desculpas)

    if not wordLists["chars"] or not wordLists["places"]:
        return random.choice(desculpas)
    generators = [
        (lambda: combineStyles(
            clean_news,
            [
                lambda: makeNewNewsShuffle(clean_news),
                lambda: makeNewNewsChars(clean_news, wordLists["chars"])
            ],
            wordLists
        ), 4),
        (lambda: combineStyles(
            clean_news,
            [
                lambda: makeDadaLikeNews(clean_news),
                lambda: makeNewNewsShuffle(clean_news)
            ],
            wordLists
        ), 1),

        (lambda: makeNewNewsShuffle(clean_news), 6),
        (lambda: makeNewNewsChars(clean_news, wordLists["chars"]), 4),
        #(lambda: makeFirstPartNews(clean_news), 3),
        (lambda: makeNewNewsPlace(clean_news, wordLists["places"]), 2),
        (lambda: makeDadaLikeNews(clean_news),3),
    ]

    funcs = [g for g, _ in generators]
    weights = [w for _, w in generators]

    generated_list = random.choices(funcs, weights=weights, k=1)[0]()
    '''generators = [ #chei de gabiarra
        lambda: combineStyles(
            clean_news,
            [
                
                lambda: makeNewNewsShuffle(clean_news),
                lambda: makeNewNewsChars(clean_news, wordLists["chars"])
            ],
            wordLists
        ),
        lambda: combineStyles(
            clean_news,
            [
                
                lambda: makeNewNewsShuffle(clean_news),
                lambda: makeNewNewsChars(clean_news, wordLists["chars"])
            ],
            wordLists
        ),
        lambda: combineStyles(
            clean_news,
            [
                
                lambda: makeNewNewsShuffle(clean_news),
                lambda: makeNewNewsChars(clean_news, wordLists["chars"])
            ],
            wordLists
        ),
        lambda: makeDadaLikeNews(clean_news),
        lambda: makeNewNewsShuffle(clean_news),
        lambda: makeNewNewsShuffle(clean_news),
        lambda: makeNewNewsShuffle(clean_news),
        lambda: makeNewNewsShuffle(clean_news),
        lambda: makeNewNewsShuffle(clean_news), #gambiarra, eu sei
        lambda: makeNewNewsChars(clean_news, wordLists["chars"]),
        lambda: makeFirstPartNews(clean_news),
        #lambda: makePlotTwistNews(clean_news), # não tô gostando dos resultados
        lambda: makeNewNewsPlace(clean_news, wordLists["places"]),
        lambda: combineStyles(
            clean_news,
            [
                lambda: makeDadaLikeNews(clean_news),
                lambda: makeNewNewsShuffle(clean_news)
            ],
            wordLists
        ),
        #lambda: makeFakeStyleNews(clean_news, wordLists["chars"], wordLists["adjectives"]),
    ]'''

    valid_titles = [t for t in generated_list if isValidPart(t)]

    if not valid_titles:
        return random.choice(clean_news)
    for _ in range(3):
        titulo = random.choice(valid_titles)
        if not endsBadly(titulo):
            break
    else:
        return applyNewsStyle(random.choice(clean_news))

    titulo = finalizeTitle(titulo)
    pontuacao = ['','','','.','?','!','!!!','',' #post',' ','',''] #gambiarra passou para cá
    titulo = titulo.strip() + random.choice(pontuacao)

    return titulo