import pytest

from anki_chinese_cards.hanzicraft import HanziCraft, HanziCraftCharMeaning
from anki_chinese_cards.selenium import SeleniumDriver
from anki_chinese_cards.utils import WindowsPath

image_dir = WindowsPath("./radicals/")


@pytest.fixture
def setup_hanzicraft():
    """Setup the Selenium driver and do the Captcha test."""
    selenium_driver = SeleniumDriver().setup()
    hc = HanziCraft(selenium_driver, image_dir)

    # Uncomment if you need to pass Captcha
    # hc.do_captcha()

    yield hc

    hc.quit()


def test_hanzicraft_get_meanings(setup_hanzicraft):
    hc = setup_hanzicraft
    hc.go_to_character("林")
    meanings = hc.get_meanings()

    expected_meanings = [
        HanziCraftCharMeaning("lín", "surname Lin"),
        HanziCraftCharMeaning(
            "lín",
            "woods • forest • CL:片[pian4] • circle(s) (i.e. specific group of people) • a collection (of similar things)",
        ),
    ]

    assert meanings == expected_meanings


def test_hanzicraft_get_phonetics(setup_hanzicraft):
    hc = setup_hanzicraft
    hc.go_to_character("机")
    phonetics = hc.get_phonetics()

    expected_phonetics = [
        "机 jī has component 几 jī. Exact match.",
        "机 jī has component 几 jǐ. Same pinyin, different tone.",
    ]
    assert phonetics == expected_phonetics


def test_hanzicraft_empty_phonetics(setup_hanzicraft):
    hc = setup_hanzicraft
    hc.go_to_character("林")
    phonetics = hc.get_phonetics()

    expected_phonetics = ["There are no phonetic clues for this character."]
    assert phonetics == expected_phonetics


def test_hanzicraft_radicals_screenshot(setup_hanzicraft):
    hc = setup_hanzicraft
    hc.go_to_character("啊")
    path = hc.get_radicals()

    expected_path = image_dir.join("啊_radicals.png")
    assert path.wsl_path == expected_path.wsl_path
