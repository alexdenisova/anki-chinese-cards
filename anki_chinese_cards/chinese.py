import re


class ChineseCharMeaning:
    def __init__(self, pinyin: str, meaning: str):
        """
        Args:
            meaning (str): one of the meanings of the Chinese character
            pinyin (str): the Pinyin of this specific meaning

        """
        self.meaning = meaning
        self.pinyin = pinyin

    def format(self):
        return f'<span style="font-weight: 600; color: rgb(245, 87, 106);">{self.pinyin}</span><br>{self.meaning}'


class ChineseCharacter:
    def __init__(
        self,
        character: str,
        radicals_pic: str = None,  # basename of the pic path
        meanings: list[ChineseCharMeaning] = [],
        phonetics: list[str] = [],
        examples: list[str] = [],
    ):
        """
        Args:
            character (str): a char of the Chinese character
            radicals_pic (str): basename of the pic path
            meanings (list[AnkiCharMeaning]): a list of the Chinese character's meanings
            phonetics (list[str]): a list of the phonetic clues in the Chinese character
            examples (list[str]): a list of words or sentences where the Chinese character is used
        """
        self.character = character
        self.radicals_pic = radicals_pic
        self.meanings = meanings
        self.phonetics = phonetics
        self.examples = examples

    def format_meanings(self):
        result = ""
        for idx, meaning in enumerate(self.meanings):
            result += f"{idx+1}. {meaning.format()}<br>"
        return result

    def format_phonetics(self):
        pattern = r"([\u4e00-\u9fff]) ([^\s\.]+)?"
        result = ""
        for idx, phonetic in enumerate(self.phonetics):
            formatted = re.sub(
                pattern,
                r'<span style="color: rgb(0, 0, 0); background-color: rgb(247, 247, 247);">\1 <span style="color: rgb(46, 158, 91); font-weight: bold;">\2</span></span>',
                phonetic,
            )
            result += f"{idx+1}. {formatted}<br>"
        return result

    def format_examples(self):
        result = ""
        for example in self.examples:
            result += f"{example}<br>"
        return result


class ChineseWord:
    def __init__(
        self,
        translation: str,
        characters: list[ChineseCharacter],
        pinyin: str,
        audio_url: str,
        stroke_order_urls: list[str],
    ):
        """
        Args:
            translation (str): the translation of the Chinese word
            characters (str): the Chinese characters that make up the word
            pinyin (str): the Pinyin of the word
            audio_url (str): a URL to an MP3 file of the word
            stroke_order_urls (list[str]): a list of URLs with pictures of the word's character's stroke orders
        """
        self.translation = translation
        self.characters = characters
        self.pinyin = pinyin
        self.audio_url = audio_url
        self.stroke_order_urls = stroke_order_urls

    def to_string(self) -> str:
        chars = ""
        for char in self.characters:
            chars += char.character
        return chars
