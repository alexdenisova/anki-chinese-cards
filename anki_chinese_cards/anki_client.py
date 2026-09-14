import logging
import ntpath
import os

from anki_chinese_cards.anki_connect import AnkiConnect
from anki_chinese_cards.chinese import ChineseCharacter, ChineseWord
from anki_chinese_cards.utils import WindowsPath


class AnkiClient:
    """Client that combines AnkiAudioClient, AnkiCharactersClient and AnkiWordsClient"""

    def __init__(
        self,
        anki_file_dir: WindowsPath,
        audio_deck: str,
        characters_deck: str,
        words_deck: str,
        url: str = "http://localhost:8765",
    ):
        """
        Args:
            url (str): the AnkiConnect server
            anki_file_dir (WindowsPath): path to the folder where Anki stores files
            audio_deck (str): name of the Anki deck where "Chinese Audio" notes will be created
            characters_deck (str): name of the Anki deck where "Chinese Characters" notes will be created
            words_deck (str): name of the Anki deck where "Chinese Words" notes will be created
        """
        self.audio = AnkiAudioClient(anki_file_dir, audio_deck, url)
        self.characters = AnkiCharactersClient(anki_file_dir, characters_deck, url)
        self.words = AnkiWordsClient(anki_file_dir, words_deck, url)


class AnkiAudioClient(AnkiConnect):
    """Client for "Chinese Audio" notes"""

    NOTE_MODEL_NAME = "Chinese Audio"

    def __init__(
        self,
        anki_file_dir: WindowsPath,
        deck: str,
        url: str = "http://localhost:8765",
    ):
        """
        Args:
            url (str): the AnkiConnect server
            anki_file_dir (WindowsPath): path to the folder where Anki stores files
            deck (str): name of the Anki deck where "Chinese Audio" notes will be created
        """
        super().__init__(anki_file_dir, deck, url)

    def create_or_update_note(self, word: ChineseWord) -> int | None:
        """Creates a "Chinese Audio" note if it doesn't exist and adds the word to the "Meanings" field. Returns the Note ID"""
        existing_notes = self._get_note_ids(f'"Pinyin:{word.pinyin}"')
        note_id = None
        if len(existing_notes) == 0:
            note_id = self.create_note(word)
        else:
            note_id = self._update_note_meanings(existing_notes[0], word)
        return note_id

    def create_note(
        self,
        anki_word: ChineseWord,
        tags: list[str] = [],
    ) -> int | None:
        """Creates a "Chinese Audio" note. Returns the Note ID"""

        word = anki_word.to_string()
        note = {
            "deckName": self.deck,
            "modelName": self.NOTE_MODEL_NAME,
            "fields": {
                "Pinyin": anki_word.pinyin,
                "Audio": "",
                "Meanings": f"{word} - {anki_word.translation}",
            },
            "tags": tags,
            "options": {"allowDuplicate": False, "duplicateScope": "deck"},
            "audio": [
                {
                    "url": anki_word.audio_url,
                    "filename": os.path.basename(anki_word.audio_url),
                    "fields": ["Audio"],
                }
            ],
        }

        logging.debug(note)

        result = super().create_note(note)
        if result != None:
            logging.info(f"Successfully added note {word} in deck {self.deck}")
        else:
            logging.error(f"Error adding note {word} in deck {self.deck}")
        return result

    def _update_note_meanings(
        self,
        note_id: int,
        word: ChineseWord,
    ) -> int | None:
        """Updates a "Chinese Audio" note by adding the word to the "Meanings" field. Returns the Note ID"""

        current_note = self._get_note_by_id(note_id)
        if current_note is None:
            logging.error(f"Note {note_id} does not exist")
            return None
        current_meanings = current_note["fields"]["Meanings"]["value"]

        word_str = word.to_string()
        note = {
            "id": note_id,
            "modelName": self.NOTE_MODEL_NAME,
            "fields": {
                "Meanings": f"{current_meanings}</br>{word_str} - {word.translation}"
            },
        }

        logging.debug(note)

        result = self._request("updateNoteFields", {"note": note})

        if result and result.get("error") is None:
            logging.info(f"Successfully updated audio note for {word_str}")
            return note_id
        else:
            logging.error(f"Error updating note audio note for {word_str}: {result['error']}")


class AnkiCharactersClient(AnkiConnect):
    """Client for "Chinese Characters" notes"""

    NOTE_MODEL_NAME = "Chinese Characters"

    def __init__(
        self,
        anki_file_dir: WindowsPath,
        deck: str,
        url: str = "http://localhost:8765",
    ):
        """
        Args:
            url (str): the AnkiConnect server
            anki_file_dir (WindowsPath): path to the folder where Anki stores files
            deck (str): name of the Anki deck where "Chinese Characters" notes will be created
        """
        super().__init__(anki_file_dir, deck, url)

    def create_notes_for_word(self, word: ChineseWord) -> int | None:
        """Creates the "Chinese Characters" notes for the word if they do not exist. Returns the Note ID"""
        for anki_char in word.characters:
            note_ids = self._get_note_ids(f"Character:{anki_char.character}")

            note_id = None
            if len(note_ids) == 0:
                note_id = self.create_note(anki_char)
            else:
                logging.info(
                    f"Note for {anki_char.character} already exists in deck {self.deck}"
                )
                note_id = note_ids[0]

            word_str = word.to_string()
            example = f"{word_str} - {word.translation}"
            self._append_to_note_field(note_id, "Examples", example)

    def create_note(
        self,
        character: ChineseCharacter,
        tags: list[str] = [],
    ) -> int | None:
        """Creates a "Chinese Characters" note. Returns the Note ID"""

        note = {
            "deckName": self.deck,
            "modelName": self.NOTE_MODEL_NAME,
            "fields": {
                "Character": character.character,
                "Radicals": "",
                "Meaning": character.format_meanings(),
                "Phonetics": character.format_phonetics(),
                "Examples": character.format_examples(),
            },
            "tags": tags,
            "options": {"allowDuplicate": False, "duplicateScope": "deck"},
            "picture": [
                {
                    "filename": character.radicals_pic,
                    "path": self.anki_file_dir.join(
                        character.radicals_pic
                    ).windows_path,
                    "fields": ["Radicals"],
                }
            ],
        }

        logging.debug(note)

        result = super().create_note(note)
        if result != None:
            logging.info(
                f"Successfully added note {character.character} in deck {self.deck}"
            )
        else:
            logging.error(
                f"Error adding note {character.character} in deck {self.deck}"
            )
        return result


class AnkiWordsClient(AnkiConnect):
    """Client for "Chinese Words" notes"""

    NOTE_MODEL_NAME = "Chinese Words"

    def __init__(
        self,
        anki_file_dir: WindowsPath,
        deck: str,
        url: str = "http://localhost:8765",
    ):
        """
        Args:
            url (str): the AnkiConnect server
            anki_file_dir (WindowsPath): path to the folder where Anki stores files
            deck (str): name of the Anki deck where "Chinese Words" notes will be created
        """
        super().__init__(anki_file_dir, deck, url)

    def create_note(
        self,
        anki_word: ChineseWord,
        tags: list[str] = [],
    ) -> int | None:
        """Creates a "Chinese Words" note. Returns the Note ID"""

        word = anki_word.to_string()
        note = {
            "deckName": self.deck,
            "modelName": self.NOTE_MODEL_NAME,
            "fields": {
                "Translation": anki_word.translation,
                "Chinese Word": word,
                "Radicals": "<br>".join(
                    [
                        f"<img src='{ntpath.basename(char.radicals_pic)}'>"
                        for char in anki_word.characters
                    ]
                ),
                "Pinyin": anki_word.pinyin,
                "Audio": "",
                "Stroke Order": "".join(
                    [
                        f"<img src='{os.path.basename(url)}' style='max-width: 150px; height: auto;'>"
                        for url in anki_word.stroke_order_urls
                    ]
                ),
            },
            "tags": tags,
            "options": {"allowDuplicate": False, "duplicateScope": "deck"},
            "picture": [
                {
                    "filename": char.radicals_pic,
                    "path": self.anki_file_dir.join(char.radicals_pic).windows_path,
                }
                for char in anki_word.characters
            ]
            + [
                {"url": url, "filename": os.path.basename(url)}
                for url in anki_word.stroke_order_urls
            ],
            "audio": [
                {
                    "url": anki_word.audio_url,
                    "filename": os.path.basename(anki_word.audio_url),
                    "fields": ["Audio"],
                }
            ],
        }

        logging.debug(note)

        result = super().create_note(note)
        if result != None:
            logging.info(f"Successfully added note {word} in deck {self.deck}")
        else:
            logging.error(f"Error adding note {word} in deck {self.deck}")
        return result

    def check_if_note_exists(self, word: str) -> bool:
        """Returns True if a "Chinese Words" note exists for `word`"""
        return len(self._get_note_ids(f'"Chinese Word:{word}"')) > 0

    def get_all_words(self) -> list[str]:
        """Returns of all the chinese words in "Chinese Words" deck"""
        words = []
        for note in self._get_notes():
            word = ""
            for char in note["fields"]["Chinese Word"]["value"]:
                if ('\u4e00' <= char <= '\u9fff'):
                    word += char
                else: # skips all non-chinese characters
                    if len(word) != 0:
                        words.append(word)
                        word = ""
            if len(word) != 0:
                words.append(word)
        return words
