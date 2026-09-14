from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class SeleniumDriver:
    def __init__(self):
        self.driver = None

    def setup(self):
        """Initializes the Chrome driver. Returns Self"""
        if self.driver is not None:
            return self

        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        # Hide automation
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            },
        )

        return self

    def quit(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def get(self, url):
        if self.driver is None:
            self.setup()
        self.driver.get(url)

    def get_element_by_css(self, css: str, idx=0) -> WebElement:
        if self.driver is None:
            self.setup()
        if idx == 0:
            return WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css))
            )
        else:
            return WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, css))
            )[idx]

    def get_element_by_css_and_text(
        self, css: str, text: str, element_order: int = 0
    ) -> WebElement | None:
        if self.driver is None:
            self.setup()

        elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, css))
        )

        current_order = 0
        text = text.strip()
        for element in elements:
            if text == element.text.strip():
                if current_order == element_order:
                    return element
                else:
                    current_order += 1

        return None

    def screenshot_element(self, element: WebElement, output_path):
        if self.driver is None:
            self.setup()
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        element.screenshot(output_path)

    def click_element(self, css: str):
        if self.driver is None:
            self.setup()
        element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    css,
                )
            )
        )
        element.click()
