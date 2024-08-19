from textblob import TextBlob
import pathlib
import csv
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import re
import string
import matplotlib
import matplotlib.pyplot as plt

from src.prison_gpt.own_types import Turn


def remove_emojis(input_string):
    # Define the emoji pattern using a regex
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # other miscellaneous symbols
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', input_string)


def normalize(text: str) -> list[str]:
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation + "’"))
    text = remove_emojis(text)

    blob = TextBlob(text)

    stop_words = set(stopwords.words("english"))
    words = [word for word in blob.words if word not in stop_words]

    ps = PorterStemmer()
    words = [ps.stem(word) for word in words]

    return words


def get_word_count(words: list[str]) -> list[tuple[str, int]]:
    word_count = {}
    for word in words:
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    return sorted_words


ROOT_PATH = pathlib.Path(__file__).parent.parent.resolve()
GAME_PATH = ROOT_PATH / "data"

# nltk.download("punkt")
# nltk.download("stopwords")


turns = []


with open(GAME_PATH / "game-1-8.csv") as f:
    csv_reader = csv.DictReader(f, delimiter=";")
    for row in csv_reader:
        turn = Turn(**row)
        turns.append(turn)


for i in range(4):
    plt.hist([TextBlob(turn.text1).sentiment.polarity for turn in turns if turn.turn == i], label=f"Turn {i}", alpha=0.2)
plt.legend(loc='upper right')
plt.savefig('plot1.png', dpi=300)

plt.close()

for i in range(4):
    plt.hist([TextBlob(turn.text2).sentiment.polarity for turn in turns if turn.turn == i], label=f"Turn {i}", alpha=0.2)
plt.legend(loc='upper right')
plt.savefig('plot2.png', dpi=300)
