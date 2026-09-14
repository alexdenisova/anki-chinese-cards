import logging
import os
from dataclasses import dataclass, field

from anki_chinese_cards.anki_client import AnkiClient
from anki_chinese_cards.hanzicraft import HanziCraft
from anki_chinese_cards.selenium import SeleniumDriver
from anki_chinese_cards.trainchinese import TrainChinese
from anki_chinese_cards.utils import WindowsPath, get_number_suffix


@dataclass
class Config:
    """Configuration from env variables"""

    anki_connect_server: str = field(
        default=os.environ.get("ACC__ANKI_CONNECT_SERVER", "http://localhost:8765")
    )  # Address of the AnkiConnect server

    words_file_path: str = field(
        default=os.environ.get("ACC__WORDS_FILE_PATH", "./words.txt")
    )  # Path to file with words separated by a newline

    translation_language: str = field(
        default=os.environ.get("c", "ru")
    )  # The language from which Chinese words will be translated from. "ru" = "Russian", "en" = "English"

    words_deck: str = field(
        default=os.environ.get("ACC__WORDS_DECK", "Chinese::Words")
    )  # Name of the Deck where Chinese Words cards will be created

    characters_deck: str = field(
        default=os.environ.get("ACC__CHARACTERS_DECK", "Chinese::Characters")
    )  # Name of the Deck where Chinese Characters cards will be created

    audio_deck: str = field(
        default=os.environ.get("ACC__AUDIO_DECK", "Chinese::Passive Vocab")
    )  # Name of the Deck where Audio cards will be created

    anki_file_dir: WindowsPath = field(
        default_factory=lambda: WindowsPath(
            os.environ.get("ACC__ANKI_FILE_DIR", r"C:\Users\user\Documents\Anki\files")
        )
    )  # Path to dir where files for Anki will be stored

    log_level: str = field(
        default_factory=lambda: os.environ.get("ACC__LOG_LEVEL", "INFO")
    )

    def get_words(self) -> list[str]:
        with open(self.words_file_path, "r", encoding="utf-8") as file:
            words = [line.strip() for line in file.readlines()]
            return words


def main():
    config = Config()
    # Configure logging
    log_level = getattr(logging, config.log_level.upper(), logging.INFO)
    logging.basicConfig(format="%(levelname)s: %(message)s", level=log_level)

    anki = AnkiClient(
        config.anki_file_dir,
        config.audio_deck,
        config.characters_deck,
        config.words_deck,
        config.anki_connect_server,
    )

    selenium_driver = SeleniumDriver().setup()
    hc = HanziCraft(selenium_driver, config.anki_file_dir, config.translation_language)
    tc = TrainChinese(selenium_driver)

    # Uncomment if you need to pass Captcha
    tc.do_captcha()
    hc.do_captcha()

    for word_str in config.get_words():
        # Skip word if the line starts with a `#`
        if word_str.startswith("#"):
            continue

        # Get the Chinese characters in the word from HanziCraft
        word_characters = hc.get_word_characters(word_str)

        # Extract the order of the word in TrainChinese from the `word_str`. =0 by default.
        num_suffix = get_number_suffix(word_str)
        word_str = word_str.removesuffix(str(num_suffix))
        word_order = num_suffix - 1 if num_suffix > 0 else 0

        # Find the word in TrainChinese
        word_cw = tc.get_word(word_str, word_order)
        if word_cw is None:
            continue
        word_cw.characters = word_characters

        # Create notes for the Chinese characters in the word
        anki.characters.create_notes_for_word(word_cw)

        if anki.words.check_if_note_exists(word_str):
            logging.warning(f'"Chinese Words" note for {word_str} already exists')

        # Create note for the Chinese word
        anki.words.create_note(word_cw)

        # Add the Chinese word as one of the meanings of a Pinyin
        anki.audio.create_or_update_note(word_cw)


if __name__ == "__main__":
    main()
