import logging
import re
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebElement

from anki_chinese_cards.chinese import ChineseWord

from .selenium import SeleniumDriver


class TrainChinese:
    def __init__(self, selenium_driver: SeleniumDriver, language="ru"):
        self.selenium_driver = selenium_driver
        self.language = language  # the language to translate words to
        self.target_word = None  # the Chinese word to look up

    def quit(self):
        self.selenium_driver.quit()

    def do_captcha(self):
        """When you open TrainChinese for the first time,
        you need to fill out the captcha,
        so I've added some sleep time to give you time."""
        search_url = f"https://www.trainchinese.com/v2/search.php?searchWord=加&rAp=0&height=0&width=0&tcLanguage={self.language}"
        self.selenium_driver.get(search_url)
        sleep(60)

    def go_to_word(self, word: str, word_order: int = 0) -> str | None:
        """
        Args:
            word (str): the word to look for in TrainChinese
            word_order (int): the order of the word in the search result (since characters can have multiple meanings)

        Returns:
            None if the word was not found."""
        self.selenium_driver.setup()

        try:
            # Search for the word
            search_url = f"https://www.trainchinese.com/v2/search.php?searchWord={word}&rAp=0&height=0&width=0&tcLanguage={self.language}"
            self.selenium_driver.get(search_url)

            # Find matching query result
            element = self.selenium_driver.get_element_by_css_and_text(
                ".leadXXL.chinese", word, word_order
            )
            if element is None:
                raise

            # Click the parent td
            parent_td = element.find_element(By.XPATH, "./..")
            parent_td.click()

            self.target_word = word
            return word
        except:
            logging.error(f"Could not find word {word} in TrainChinese")
            return None

    def get_word(self, word: str, word_order: int = 0) -> ChineseWord | None:
        """Creates a ChineseWord type from word.
        Args:
            word (str): the word to look for in TrainChinese
            word_order (int): the order of the word in the search result (since characters can have multiple meanings)

        Returns:
            None if the word was not found.
        """
        if self.go_to_word(word, word_order) is None:
            return None

        if (
            self.selenium_driver.get_element_by_css(".chinese")
            .text.replace(" ", "")
            .strip()
        ) != word:
            logging.error(f"Could not find .chinese element of {word} in TrainChinese")
            return None

        return ChineseWord(
            translation=self.get_translation(),
            characters=[],
            pinyin=self.get_pinyin(),
            audio_url=self.get_audio_url(),
            stroke_order_urls=self.get_stroke_order(),
        )

    def get_pinyin(self) -> str:
        return self.selenium_driver.get_element_by_css(".pinyin").text

    def get_translation(self) -> str:
        translation = self.selenium_driver.get_element_by_css(
            ".translation"
        ).text.strip()
        if " " in translation:
            return (
                translation.split(" ", 1)[1].removeprefix("сл.").strip()
            )  # Removes the "part of speech" prefix
        return translation

    def get_audio_url(self) -> str:
        audio_element = self.selenium_driver.get_element_by_css(
            "img[onclick*='playAudioFile']"
        )
        return extract_audio_url(audio_element.get_attribute("onclick"))

    def get_stroke_order(self) -> list[str]:
        """Returns list of image URLs"""
        self.selenium_driver.click_element(
            "div.panel-heading[onclick*='loadStrokeImages']"
        )

        urls = []
        for char in self.target_word:
            if not ("\u4e00" <= char <= "\u9fff"):
                continue
            image_url = self.selenium_driver.get_element_by_css(
                f"img[alt='{char}']"
            ).get_attribute("src")

            urls.append(image_url)
        return urls


def extract_audio_url(audio_element: WebElement):
    """Extract audio URL from audio element."""
    pattern = r"playAudioFile\s*\(\s*'([^']+)'.*,([0-9]+)"
    match = re.search(pattern, audio_element)

    if match:
        filename = match.group(1)
        word_id = int(match.group(2)) % 1000
        return f"https://www.trainchinese.com/v1/word_lists/tc_words/w_dirs/w{word_id}/{filename}"
    return None
