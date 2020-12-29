import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options


def auto_edit_forwarding(ip):
    opts = Options()
    opts.headless = True
    browser = Firefox(options=opts)
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
    input_element.send_keys('2cg6xpo"')
    input_element.send_keys(Keys.ENTER)
    time.sleep(1)
    browser.get('https://domains.google.com')
    time.sleep(5)
    site_link = browser.find_element_by_link_text('mjfullstack.com')
    site_link.click()
    time.sleep(2)
    edit_btn = browser.find_elements_by_class_name('mat-button')
    for btn in edit_btn:
        try:
            btn.click()
        except StaleElementReferenceException as e:
            print(e)
    time.sleep(.5)
    ip_input = browser.find_element_by_id('mat-input-0')
    ip_input.clear()
    ip_input.send_keys(ip)
    ip_input.send_keys(Keys.ENTER)
    return f'IP changed to {ip} at domains.google.com'
