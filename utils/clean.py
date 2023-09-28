import re
import string

import nltk
from nltk.corpus import stopwords


def remove_stop(corpus: str) -> str:
    """Remove stop words from a corpus

    Arguments:
        corpus {str} -- The corpus

    Returns:
        str -- The corpus without stop words
    """
    nltk.download("stopwords")

    words = nltk.word_tokenize(corpus)

    table = str.maketrans("", "", string.punctuation)
    stripped_words = [word.translate(table) for word in words]

    stop_words = set(stopwords.words("english"))
    filtered_words = [
        word for word in stripped_words if word.lower() not in stop_words
    ]

    filtered_text = " ".join(filtered_words)

    print(len(filtered_text))

    return filtered_text


def remove_emojis(text: str) -> str:
    """Remove emojis from a text

    Arguments:
        text {str} -- The text

    Returns:
        str -- The text without emojis
    """
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & Pictographs
        "\U0001F680-\U0001F6FF"  # Transport & Map Symbols
        "\U0001F700-\U0001F77F"  # Alchemical Symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U0001F004-\U0001F0CF"  # CJK Compatibility Ideographs
        "\U0001F170-\U0001F251"  # Enclosed Ideographic Supplement
        "]+",
        flags=re.UNICODE,
    )

    text_without_emojis = re.sub(emoji_pattern, "", text)

    return text_without_emojis
