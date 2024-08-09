from textblob import TextBlob
import pathlib
import csv
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import re
import string


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
GAME_PATH = ROOT_PATH / "games"

# nltk.download("punkt")
# nltk.download("stopwords")

texts1 = ""
texts2 = ""

with open(GAME_PATH / "game-1-8.csv") as f:
    csv_reader = csv.DictReader(f, delimiter=";")
    for row in csv_reader:
        texts1 += row["text1"]
        texts2 += row["text2"]

words1 = normalize(texts1)
words2 = normalize(texts2)

sorted_words1 = get_word_count(words1)
sorted_words2 = get_word_count(words2)

for i in range(20, 0, -1):
    print(f"{sorted_words1[i][0]}: {sorted_words1[i][1]} | {sorted_words2[i][0]}: {sorted_words2[i][1]}")

s1 = TextBlob(texts1)
s2 = TextBlob(texts2)
print(s1.sentiment)
print(s2.sentiment)
