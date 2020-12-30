import base64
import os
import time
import logging
from pyvirtualdisplay import Display

from selenium.common.exceptions import StaleElementReferenceException
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys

logging.basicConfig(level=logging.INFO)


def get_pwd():
    if os.path.isfile("cred.txt"):
        with open('cred.txt', 'r') as f:
            pwd = f.read()
            if pwd:
                pwd = base64.b64decode(pwd).decode('utf-8')
        return pwd


def auto_edit_forwarding(ip):
    logging.info('Process started')
    display = Display(visible=0, size=(1366, 768))
    display.start()
    logging.info('Vdisplay started')
    opts = Options()
    opts.headless = True
    browser = webdriver.Firefox(options=opts)
    browser.get('https://stackoverflow.com')
    time.sleep(5)
    logging.info('Logging into stackoverflow.com')
    login_link = browser.find_element_by_class_name('login-link')
    login_link.click()
    time.sleep(5)
    login_link = browser.find_element_by_class_name('s-btn__google')
    login_link.click()
    time.sleep(5)
    try:
        input_element = browser.find_element_by_id('identifierId')
        input_element.send_keys('mjfullstack')
        input_element.send_keys(Keys.ENTER)
        logging.info('username entered')
        time.sleep(5)
        input_element = browser.find_element_by_name('password')
        input_element.send_keys(get_pwd())
        input_element.send_keys(Keys.ENTER)
        logging.info('password entered')
    except Exception as e:
        logging.warning(f'Could not find input: ERROR: {e}')
        browser.quit()
        display.stop()
        return
    time.sleep(5)
    logging.info('Navigating to domains.google.com')
    browser.get('https://domains.google.com/registrar')
    time.sleep(5)
    logging.info(browser.title)
    try:
        site_link = browser.find_element_by_partial_link_text('mjfullstack')
        site_link.click()
        time.sleep(5)
        edit_btn = browser.find_elements_by_class_name('mat-button')
        for btn in edit_btn:
            try:
                btn.click()
            except StaleElementReferenceException:
                continue
    except Exception as e:
        logging.warning(f'Not logged into Google. Process ending. ERROR:{e}')
        browser.quit()
        display.stop()
        return
    time.sleep(5)
    ip_input = browser.find_element_by_id('mat-input-0')
    logging.info('Changing IP')
    ip_input.clear()
    ip_input.send_keys(ip)
    ip_input.send_keys(Keys.ENTER)
    time.sleep(2)
    browser.quit()
    display.stop()
    logging.info('Process completed')
    return f'IP changed to {ip} at domains.google.com'


if __name__ == '__main__':
    auto_edit_forwarding('86.150.163.169')
