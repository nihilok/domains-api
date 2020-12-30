import base64
import os
import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

driver = webdriver.Remote(
  desired_capabilities=webdriver.DesiredCapabilities.HTMLUNIT)

def get_pwd():
    if os.path.isfile("cred.txt"):
        with open('cred.txt', 'r') as f:
            pwd = f.read()
            if pwd:
                pwd = base64.b64decode(pwd).decode('utf-8')
        return pwd


def auto_edit_forwarding(ip):
    browser = webdriver.Remote(desired_capabilities=webdriver.DesiredCapabilities.HTMLUNIT)
    browser.get('https://stackoverflow.com')
    login_link = browser.find_element_by_class_name('login-link')
    login_link.click()
    login_link = browser.find_element_by_class_name('s-btn__google')
    login_link.click()
    input_element = browser.find_element_by_id('identifierId')
    input_element.send_keys('mjfullstack')
    input_element.send_keys(Keys.ENTER)
    time.sleep(1)
    input_element = browser.find_element_by_class_name('whsOnd')
    input_element.send_keys(get_pwd())
    input_element.send_keys(Keys.ENTER)
    time.sleep(.5)
    browser.get('https://domains.google.com')
    time.sleep(4.5)
    site_link = browser.find_element_by_link_text('mjfullstack.com')
    site_link.click()
    time.sleep(1.5)
    edit_btn = browser.find_elements_by_class_name('mat-button')
    for btn in edit_btn:
        try:
            btn.click()
        except StaleElementReferenceException:
            continue
    time.sleep(.5)
    ip_input = browser.find_element_by_id('mat-input-0')
    ip_input.clear()
    ip_input.send_keys(ip)
    ip_input.send_keys(Keys.ENTER)
    time.sleep(.5)
    browser.quit()
    return f'IP changed to {ip} at domains.google.com'


if __name__ == '__main__':
    auto_edit_forwarding('86.150.163.169')
