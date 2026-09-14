# anki-chinese-cards

A tool that creates Anki cards to help me learn Mandarin. Given a list of Chinese words, it scrapes [HanziCraft](https://hanzicraft.com/) and [TrainChinese](https://www.trainchinese.com/v2/index.php?rAp=1431449459271) using Selenium, gets the translation, character meanings and downloads pronunciation audio to create cards in Anki using AnkiConnect API.

## How it Works

Since neither HanziCraft nor TrainChinese have a public API, and both are protected by a Captcha, the tool uses Selenium to access them. It parses the provided Chinese word list, and then for each entry it gathers the needed information from HanziCraft and TrainChinese, and then creates cards using the AnkiConnect API.

For each word provided, 3 cards will be created:

1. A "Chinese Words" card that will be used as a flashcard where the Russian/English translation is shown and the Chinese word is the answer.
2. A "Chinese Characters" card that will contain the Chinese character, its various meanings and words that use it.
3. An "Audio" card that will contain an audio file of the Chinese word.

## Requirements

Poetry, Python (^3.10), Anki + AnkiConnect, ChromeDriver

My versions: Poetry 1.5.1, Python 3.10.12, ChromeDriver 150.0.7871.114

## Setup

`poetry install`

### Environment Variables

- `ACC__ANKI_CONNECT_SERVER` (optional, `="http://localhost:8765"`) - the AnkiConnect server.
- `ACC__TRANSLATION_LANGUAGE` (optional, `="ru"`) - the language from which Chinese words will be translated from. "ru" = "Russian", "en" = "English".
- `ACC__WORDS_FILE_PATH` (optional, `="./words.txt"`) - path to file with words (separated by a newline) for which Anki cards will be created.
- `ACC__WORDS_DECK` (optional, `="Chinese::Words"`) - name of the Anki Deck where Chinese Words cards will be created.
- `ACC__CHARACTERS_DECK` (optional, `="Chinese::Characters"`) - name of the Anki Deck where Chinese Characters cards will be created.
- `ACC__AUDIO_DECK` (optional, `="Chinese::Passive Vocab"`) - name of the Anki Deck where Audio cards will be created.
- `ACC__ANKI_FILE_DIR` (optional, `="C:\Users\user\Documents\Anki\files"`) - path to the folder where files for Anki will be stored. Audio files and pictures will be downloaded to here. 
- `ACC__LOG_LEVEL` (optional, `="INFO"`) - the logging level.

## Usage

`poetry run python3 -m anki_chinese_cards`

## Example Cards

### Chinese Word

<p float="left">
    <img src="examples/chinese word.png" width="300" >
</p>

### Chinese Character

<p float="left">
    <img src="examples/chinese character.png" width="300" >
</p>

### Chinese Audio

<p float="left">
    <img src="examples/chinese audio.png" width="300" >
</p>
