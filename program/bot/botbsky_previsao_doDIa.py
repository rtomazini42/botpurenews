from atproto import Client
from pathlib import Path
import random
import os
from datetime import datetime

# ---------------- PATHS ----------------
base_dir = Path(__file__).resolve().parent
words_dir = base_dir.parent / "wordsData" / "todayly"



# ---------------- LOADERS ----------------
def loadList(file_name):
    path = words_dir / file_name
    with open(path, 'r', encoding='utf-8') as f:
        return [
            l.strip()
            for l in f
            if l.strip() and not l.strip().startswith("#")
        ]

# ---------------- BUILD DAILY ----------------

def getMoodEmoji():
    moods = [
        "😀","😎","😴","🤡","😡","🥲","😈","🤯",
        "😇","🤖","👀","🫠","😵","🥳","😐","🙄",
        "😬","🫥","😱","🤨","😏","🤠","🥴","🤢",
        "🤮","😤","😶","😑","🫡","🤥","🤫","🫣",
        "🧐","😺","🙀","😹","👻","💀","☠️","👽",
        "👾","🤖","🎭","🌀","🔥","🌪️","⚡","🌈",
        "🌚","🌝","⭐","🌟","💫","✨","🧨","💣",
        "🧃","🍕","🍜","🍩","🍷","☕","🧉","🧠",
        "🫀","🦴","👁️","🫦","👣","🧍","🕴️","🪑",
        "🚀","🛸","🚧","🏁","🎲","🃏","🎯","🎰",
        "📡","💻","📺","📞","📢","🔮","🪬","🧿",
        "⚠️","❗","❓","‼️","💥","🔴","🟡","🟢"
    ]
    return random.choice(moods)

def getHashtags():
    tags = [
        "#daily", "#bot", "#random",
        "#previsao", "#sorte", "#bichoDoDia", "#caos",
        "#energiaDuvidosa"
    ]
    return " ".join(random.sample(tags, k=2))

def buildDaily():
    today = datetime.now().strftime("%d/%m/%Y")
    mood = getMoodEmoji()

    weathers = loadList("wheaterPTBR.txt")
    animals = loadList("animalsPTBR.txt")
    colors = loadList("colorPTBR.txt")
    quests = loadList("quest.txt")

    weather = random.choice(weathers) if weathers else "quebrou a antena"
    animal = random.choice(animals) if animals else "soltaro os bicho"
    color = random.choice(colors) if colors else "daltonismo"
    quest = random.choice(quests) if quests else "consetar o bot"
    hashtags = getHashtags()

    lucky_number = random.randint(0, 100)

    daily = f"""📅 Daily do Dia - {today} {mood}

Previsão: {weather}
Bicho do dia: {animal}
Cor do dia: {color}
Número da sorte: {lucky_number}

Desafio: {quest}
{hashtags}
"""

    return daily.strip()

# ---------------- POST ----------------
def postDaily():
    client = Client()

    user = os.environ.get("BSKY_USER")
    password = os.environ.get("BSKY_PASS")

    if not user or not password:
        raise ValueError("Credenciais não encontradas")

    client.login(user, password)

    daily = buildDaily()

    print("Postando daily:\n", daily)

    try:
        client.send_post(daily[:300])  # limite Bluesky
    except Exception as e:
        print("Erro ao postar:", e)


# ---------------- RUN ----------------
if __name__ == "__main__":
    try:
        postDaily()
        #print(buildDaily())
        print("Daily postado com sucesso.")
    except Exception as error:
        print(f"Erro no daily: {error}")
        exit(1)