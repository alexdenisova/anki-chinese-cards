import logging
import os
import re
from time import sleep

from selenium.webdriver.common.by import By

from anki_chinese_cards.chinese import ChineseCharacter, ChineseCharMeaning
from anki_chinese_cards.utils import WindowsPath, remove_right_whitespace

from .selenium import SeleniumDriver


class HanziCraftCharMeaning:
    def __init__(self, pinyin: str, meaning: str):
        self.pinyin = pinyin
        self.meaning = meaning

    def __eq__(self, other):
        if not isinstance(other, HanziCraftCharMeaning):
            return False
        return self.pinyin == other.pinyin and self.meaning == other.meaning

    def to_chinese_char_meaning(self) -> ChineseCharMeaning:
        return ChineseCharMeaning(self.pinyin, self.meaning)


class HanziCraft:
    def __init__(
        self,
        selenium_driver: SeleniumDriver,
        image_dir: WindowsPath = WindowsPath("./radicals/"),
    ):
        self.selenium_driver = selenium_driver
        self.image_dir = image_dir  # directory to save screenshots of radicals
        self.target_character = None  # the Chinese character to look up

        try:
            os.mkdir(image_dir.wsl_path)
            logging.info(f"Directory '{image_dir.wsl_path}' created successfully.")
        except FileExistsError:
            logging.debug(f"Directory '{image_dir.wsl_path}' already exists.")
        except PermissionError:
            logging.error(
                f"Permission denied: Unable to create '{image_dir.wsl_path}'."
            )
        except Exception as e:
            raise (f"An error occurred: {e}")

    def quit(self):
        self.selenium_driver.quit()
        self.target_character = None

    def do_captcha(self):
        """When you open HanziCraft for the first time,
        you need to fill out the captcha,
        so I've added some sleep time to give you time."""
        search_url = f"https://hanzicraft.com/character/问"
        self.selenium_driver.get(search_url)
        sleep(1)
        search_url = f"https://hanzicraft.com/character/题"
        self.selenium_driver.get(search_url)
        sleep(20)

    def go_to_character(self, character):
        self.selenium_driver.setup()
        self.selenium_driver.get(f"https://hanzicraft.com/character/{character}")
        self.target_character = character

    def get_word_characters(self, word: str) -> list[ChineseCharacter]:
        """Creates a list[ChineseCharacter] type from the Chinese characters in the word."""
        word_characters = []
        for char in word:
            if not ('\u4e00' <= char <= '\u9fff'):
                logging.debug(f"Found non-chinese character: {char}")
                continue

            self.go_to_character(char)
            radical_path = self.get_radicals()

            anki_char = ChineseCharacter(
                char,
                radical_path.basename(),
                meanings=[
                    meaning.to_chinese_char_meaning() for meaning in self.get_meanings()
                ],
                phonetics=self.get_phonetics(),
            )

            word_characters.append(anki_char)

        return word_characters

    def get_meanings(self) -> list[HanziCraftCharMeaning]:
        if self.target_character is None:
            raise ("No target_character defined.")

        entries = self.selenium_driver.get_element_by_css(
            ".meaning-entries"
        ).find_elements(By.CSS_SELECTOR, ".popup-entry")

        if not entries:
            raise (f"No meaning found for {self.target_character}")

        meanings = []

        for entry in entries:
            try:
                # Get the pinyin
                pinyin_text = entry.find_element(
                    By.CSS_SELECTOR, ".popup-pinyin"
                ).text.strip()

                # Clean up the pinyin text - remove numbers and extra spaces
                # Example: "1. lín (Lin2)" -> "lín"
                pinyin = pinyin_text.split(".", 1)[-1].split("(", 1)[0].strip()

                # Get the definition
                definition = entry.find_element(
                    By.CSS_SELECTOR, ".popup-definition"
                ).text.strip()

                meanings.append(HanziCraftCharMeaning(pinyin, definition))

            except Exception as e:
                logging.error(f"Error processing entry: {e}")
                continue

        return meanings

    def get_phonetics(self) -> list[str]:
        if self.target_character is None:
            raise ("No target_character defined.")

        entries = self.selenium_driver.get_element_by_css(
            ".meaning-entries", idx=1
        ).find_elements(By.CSS_SELECTOR, ".popup-entry")

        if not entries:
            raise (f"No phonetics found for {self.target_character}")

        phonetics = []

        for entry in entries:
            try:
                # Get the definition
                definition = entry.find_element(
                    By.CSS_SELECTOR, ".popup-definition"
                ).text.strip()

                phonetics.append(re.sub(r"^[0-9]+\.", "", definition).strip())

            except Exception as e:
                logging.error(f"Error processing entry: {e}")
                continue

        return phonetics

    def get_radicals(self) -> WindowsPath:
        """Takes a screenshot of the character's radicals. Returns image path."""
        if self.target_character is None:
            raise ("No target_character defined.")

        output_path = self.image_dir.join(f"{self.target_character}_radicals.png")

        element = self.selenium_driver.get_element_by_css(".decompbox")
        self.selenium_driver.screenshot_element(element, output_path.wsl_path)

        # Removing the excess whitespace
        remove_right_whitespace(output_path.wsl_path)

        logging.debug(
            f"{self.target_character} radicals image saved at {output_path.wsl_path}"
        )
        return output_path
