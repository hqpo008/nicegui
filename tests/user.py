import threading
import time

from nicegui import globals, ui
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement

PORT = 3392


class User():

    def __init__(self, selenium: webdriver.Chrome) -> None:
        self.selenium = selenium
        self.server_thread = None

    def start_server(self) -> None:
        '''Start the webserver in a separate thread. This is the equivalent of `ui.run()` in a normal script.'''
        self.server_thread = threading.Thread(target=ui.run, kwargs={'port': PORT, 'show': False, 'reload': False})
        self.server_thread.start()

    def stop_server(self) -> None:
        '''Stop the webserver.'''
        self.selenium.close()
        globals.server.should_exit = True
        self.server_thread.join()

    def open(self, path: str) -> None:
        if self.server_thread is None:
            self.start_server()
        start = time.time()
        while True:
            try:
                self.selenium.get(f'http://localhost:{PORT}{path}')
                break
            except Exception:
                if time.time() - start > 3:
                    raise
                time.sleep(0.1)
                if not self.server_thread.is_alive():
                    raise RuntimeError('The NiceGUI server has stopped running')

    def should_see(self, text: str) -> None:
        assert self.selenium.title == text or self.find(text).text == text

    def click(self, target_text: str) -> None:
        self.find(target_text).click()

    def find(self, text: str) -> WebElement:
        try:
            return self.selenium.find_element_by_xpath(f'//*[contains(text(),"{text}")]')
        except NoSuchElementException:
            raise AssertionError(f'Could not find "{text}" on:\n{self.get_body()}')

    def get_body(self) -> str:
        return self.selenium.find_element_by_tag_name('body').text

    def get_tags(self, name: str) -> list[WebElement]:
        return self.selenium.find_elements_by_tag_name(name)

    def get_attributes(self, tag: str, attribute: str) -> list[str]:
        return [t.get_attribute(attribute) for t in self.get_tags(tag)]

    def sleep(self, t: float) -> None:
        time.sleep(t)