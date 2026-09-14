import shutil

import pytest

from anki_chinese_cards.anki_client import AnkiCharactersClient, AnkiWordsClient
from anki_chinese_cards.chinese import ChineseCharacter, ChineseCharMeaning, ChineseWord
from anki_chinese_cards.utils import WindowsPath

anki_file_dir = WindowsPath(r"C:\Users\user\Documents\Anki\files")
deck_name = "Test"


@pytest.fixture
def setup_anki_character_note():
    """Create a test card and delete it after test."""
    # Setup - create deck
    anki = AnkiCharactersClient(anki_file_dir, deck_name)
    anki.create_deck()

    # Setup - create the card
    radical_pic_path = r"./tests/files/啊_radicals.png"
    radical_pic_new_path = anki_file_dir.join("啊_radicals.png")
    shutil.copy(radical_pic_path, radical_pic_new_path.wsl_path)

    character = ChineseCharacter(
        "啊",
        radical_pic_new_path.basename(),
        meanings=[
            ChineseCharMeaning("ā", "interjection of surprise • Ah! • Oh!"),
            ChineseCharMeaning(
                "á",
                "interjection expressing doubt or requiring answer • Eh? • what? • to show realization • to stress",
            ),
        ],
        phonetics=["啊 ā has component 阿 ā. Exact match."],
        examples=["啊 - а, ой (смягчение речи)"],
    )

    note_id = anki.create_note(character)

    # Yield the note_id to the test
    yield note_id

    # Teardown
    anki.delete_note(note_id)
    anki.delete_deck()


def test_anki_chinese_character(setup_anki_character_note):
    note_id = setup_anki_character_note
    assert note_id != None


@pytest.fixture
def setup_anki_word_note():
    """Create a test card and delete it after test."""
    # Setup - create deck
    anki = AnkiWordsClient(anki_file_dir, deck_name)
    anki.create_deck()

    # Setup - create the card
    characters = []
    for char in ["是", "啊"]:
        radicals_file = f"{char}_radicals.png"
        radical_pic_path = r"./tests/files/" + radicals_file
        radical_pic_new_path = anki_file_dir.join(radicals_file)
        shutil.copy(radical_pic_path, radical_pic_new_path.wsl_path)

        characters.append(
            ChineseCharacter(char, radicals_file, meanings=[], phonetics=[])
        )

    word = ChineseWord(
        translation="фраз. Да., Верно. (для выражения согласия или подтверждения)",
        characters=characters,
        pinyin="shì a .",
        audio_url="https://www.trainchinese.com/v1/word_lists/tc_words/w_dirs/w978/56978A_cm_f_l_o12_4.mp3",
        stroke_order_urls=[
            "https://www.trainchinese.com/v2/charTracing/Simplified/26159.gif",
            "https://www.trainchinese.com/v2/charTracing/Simplified/21834.gif",
        ],
    )

    note_id = anki.create_note(word)

    # Yield the note_id to the test
    yield note_id

    # Teardown
    anki.delete_note(note_id)
    anki.delete_deck()


def test_anki_chinese_word(setup_anki_word_note):
    note_id = setup_anki_word_note
    assert note_id != None
