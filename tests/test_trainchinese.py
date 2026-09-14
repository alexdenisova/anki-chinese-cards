import pytest

from anki_chinese_cards.selenium import SeleniumDriver
from anki_chinese_cards.trainchinese import TrainChinese


@pytest.fixture
def setup_trainchinese():
    """Setup the Selenium driver and do the Captcha test."""
    selenium_driver = SeleniumDriver().setup()
    tc = TrainChinese(selenium_driver)

    # Uncomment if you need to pass Captcha
    # tc.do_captcha()

    yield tc

    tc.quit()


def test_trainchinese_get_pinyin(setup_trainchinese):
    tc = setup_trainchinese
    tc.go_to_word("加拿大")
    pinyin = tc.get_pinyin()

    assert pinyin == "jiā ná dà"


def test_trainchinese_get_translation(setup_trainchinese):
    tc = setup_trainchinese
    tc.go_to_word("加拿大")
    translation = tc.get_translation()

    assert translation == "Канада"


def test_trainchinese_get_audio(setup_trainchinese):
    tc = setup_trainchinese
    tc.go_to_word("加拿大")
    audio_url = tc.get_audio_url()

    assert (
        audio_url
        == "https://www.trainchinese.com/v1/word_lists/tc_words/w_dirs/w588/10588A_cm_f_l_p226630_3.mp3"
    )


def test_trainchinese_get_stroke_order(setup_trainchinese):
    tc = setup_trainchinese
    tc.go_to_word("加拿大")
    image_urls = tc.get_stroke_order()

    expected_image_urls = [
        "https://www.trainchinese.com/v2/charTracing/Simplified/21152.gif",
        "https://www.trainchinese.com/v2/charTracing/Simplified/25343.gif",
        "https://www.trainchinese.com/v2/charTracing/Simplified/22823.gif",
    ]

    assert image_urls == expected_image_urls
