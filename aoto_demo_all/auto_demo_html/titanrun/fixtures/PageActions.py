import codecs
import os
import sys
import time
import traceback
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.errorhandler import ElementNotVisibleException
from selenium.webdriver.remote.errorhandler import NoSuchElementException
from selenium.webdriver.remote.errorhandler import NoAlertPresentException
from selenium.webdriver.remote.errorhandler import NoSuchFrameException
from selenium.webdriver.remote.errorhandler import NoSuchWindowException
# from titanrun.config import Settings
import titanrun.config.Settings as Settings

def is_element_present(driver, selector, by=By.CSS_SELECTOR):
    try:
        driver.find_element(by=by, value=selector)
        return True
    except Exception:
        return False

def is_element_selected(driver, selector, by=By.CSS_SELECTOR):
    try:
        element = driver.find_element(by=by, value=selector)
        return element.is_selected()
    except Exception:
        return False


def is_element_visible(driver, selector, by=By.CSS_SELECTOR):
    try:
        element = driver.find_element(by=by, value=selector)
        return element.is_displayed()
    except Exception:
        return False


def is_text_visible(driver, text, selector, by=By.CSS_SELECTOR):
    try:
        element = driver.find_element(by=by, value=selector)
        return element.is_displayed() and text in element.text
    except Exception:
        return False


def hover_on_element(driver, selector, by=By.CSS_SELECTOR):
    element = driver.find_element(by=by, value=selector)
    hover = ActionChains(driver).move_to_element(element)
    hover.perform()


def hover_and_click(driver, hover_selector, click_selector,
                    hover_by=By.CSS_SELECTOR, click_by=By.CSS_SELECTOR,
                    timeout=Settings.SMALL_TIMEOUT):
    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    element = driver.find_element(by=hover_by, value=hover_selector)
    hover = ActionChains(driver).move_to_element(element)
    hover.perform()
    for x in range(int(timeout * 10)):
        try:
            element = driver.find_element(by=click_by,
                                          value="%s" % click_selector).click()
            return element
        except Exception:
            now_ms = time.time() * 1000.0
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
    raise NoSuchElementException(
        "Element {%s} was not present after %s seconds!" %
        (click_selector, timeout))


def wait_for_element_present(driver, selector, by=By.CSS_SELECTOR,
                             timeout=Settings.LARGE_TIMEOUT):
    element = None
    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    for x in range(int(timeout * 10)):
        try:
            by, selector = _css_change_id(by, selector)
            element = driver.find_element(by=by, value=selector)
            return element
        except Exception:
            now_ms = time.time() * 1000.0
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
    if not element:
        raise NoSuchElementException(
            "Element {%s} was not present after %s seconds!" % (
                selector, timeout))

def _css_change_id(by,selector):
    if "." in selector:
        if selector.startswith('#'):
            by = By.ID
            selector = selector[1:]
    return by,selector

def wait_for_element_visible(driver, selector, by=By.CSS_SELECTOR,
                             timeout=Settings.LARGE_TIMEOUT):
    element = None
    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    for x in range(int(timeout * 10)):
        try:
            by, selector = _css_change_id(by, selector)
            element = driver.find_element(by=by, value=selector)
            if element.is_displayed():
                return element
            else:
                element = None
                raise Exception()
        except Exception:
            now_ms = time.time() * 1000.0
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
    if not element and by != By.LINK_TEXT:
        raise ElementNotVisibleException(
            "Element {%s} was not visible after %s seconds!" % (
                selector, timeout))
    if not element and by == By.LINK_TEXT:
        raise ElementNotVisibleException(
            "Link text {%s} was not visible after %s seconds!" % (
                selector, timeout))


def wait_for_text_visible(driver, text, selector, by=By.CSS_SELECTOR,
                          timeout=Settings.LARGE_TIMEOUT):
    element = None
    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    for x in range(int(timeout * 10)):
        try:
            by, selector = _css_change_id(by, selector)
            element = driver.find_element(by=by, value=selector)
            if element.is_displayed():
                if text in element.text:
                    return element
                else:
                    element = None
                    raise Exception()
        except Exception:
            now_ms = time.time() * 1000.0
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
    if not element:
        raise ElementNotVisibleException(
            "Expected text {%s} for {%s} was not visible after %s seconds!" %
            (text, selector, timeout))


def wait_for_element_absent(driver, selector, by=By.CSS_SELECTOR,
                            timeout=Settings.LARGE_TIMEOUT):
    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    for x in range(int(timeout * 10)):
        try:
            by, selector = _css_change_id(by, selector)
            driver.find_element(by=by, value=selector)
            now_ms = time.time() * 1000.0
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
        except Exception:
            return True
    raise Exception("Element {%s} was still present after %s seconds!" %
                    (selector, timeout))


def wait_for_element_not_visible(driver, selector, by=By.CSS_SELECTOR,
                                 timeout=Settings.LARGE_TIMEOUT):
    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    for x in range(int(timeout * 10)):
        try:
            by, selector = _css_change_id(by, selector)
            element = driver.find_element(by=by, value=selector)
            if element.is_displayed():
                now_ms = time.time() * 1000.0
                if now_ms >= stop_ms:
                    break
                time.sleep(0.1)
            else:
                return True
        except Exception:
            return True
    raise Exception(
        "Element {%s} was still visible after %s seconds!" % (
            selector, timeout))


def find_visible_elements(driver, selector, by=By.CSS_SELECTOR):
    elements = driver.find_elements(by=by, value=selector)
    return [element for element in elements if element.is_displayed()]


def save_screenshot(driver, name, folder=None):
    if folder:
        abs_path = os.path.abspath('.')
        file_path = abs_path + "/%s" % folder
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        screenshot_file = "%s/%s" % (file_path, name)
    else:
        screenshot_file = name
    driver.get_screenshot_as_file(screenshot_file)


def _get_last_page(driver):
    try:
        last_page = driver.current_url
    except Exception:
        last_page = '[WARNING! Browser Not Open!]'
    if len(last_page) < 5:
        last_page = '[WARNING! Browser Not Open!]'
    return last_page


def save_test_failure_data(driver, name, browser_type, folder=None):
    if folder:
        abs_path = os.path.abspath('.')
        file_path = abs_path + "/%s" % folder
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        failure_data_file_path = "%s/%s" % (file_path, name)
    else:
        failure_data_file_path = name
    failure_data_file = codecs.open(failure_data_file_path, "w+", "utf-8")
    last_page = _get_last_page(driver)
    data_to_save = []
    data_to_save.append("Last_Page: %s" % last_page)
    data_to_save.append("Browser: %s " % browser_type)
    data_to_save.append("Traceback: " + ''.join(
        traceback.format_exception(sys.exc_info()[0],
                                   sys.exc_info()[1],
                                   sys.exc_info()[2])))
    failure_data_file.writelines("\r\n".join(data_to_save))
    failure_data_file.close()


def wait_for_ready_state_complete(driver, timeout=Settings.EXTREME_TIMEOUT):
    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    for x in range(int(timeout * 10)):
        try:
            ready_state = driver.execute_script("return document.readyState")
        except WebDriverException:
            # Bug fix for: [Permission denied to access property "document"]
            time.sleep(0.03)
            return True
        if ready_state == u'complete':
            time.sleep(0.01)  # Better be sure everything is done loading
            return True
        else:
            now_ms = time.time() * 1000.0
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
    raise Exception(
        "Page elements never fully loaded after %s seconds!" % timeout)


def wait_for_and_accept_alert(driver, timeout=Settings.LARGE_TIMEOUT):
    alert = wait_for_and_switch_to_alert(driver, timeout)
    alert_text = alert.text
    alert.accept()
    return alert_text


def wait_for_and_dismiss_alert(driver, timeout=Settings.LARGE_TIMEOUT):
    alert = wait_for_and_switch_to_alert(driver, timeout)
    alert_text = alert.text
    alert.dismiss()
    return alert_text


def wait_for_and_switch_to_alert(driver, timeout=Settings.LARGE_TIMEOUT):
    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    for x in range(int(timeout * 10)):
        try:
            alert = driver.switch_to.alert
            dummy_variable = alert.text  # noqa
            return alert
        except NoAlertPresentException:
            now_ms = time.time() * 1000.0
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
    raise Exception("Alert was not present after %s seconds!" % timeout)


def switch_to_frame(driver, frame, timeout=Settings.SMALL_TIMEOUT):
    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    for x in range(int(timeout * 10)):
        try:
            driver.switch_to.frame(frame)
            return True
        except NoSuchFrameException:
            now_ms = time.time() * 1000.0
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
    raise Exception("Frame was not present after %s seconds!" % timeout)

def switch_to_parent_frame(driver, timeout=Settings.SMALL_TIMEOUT):
    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    for x in range(int(timeout * 10)):
        try:
            driver.switch_to.parent_frame()
            return True
        except NoSuchFrameException:
            now_ms = time.time() * 1000.0
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
    raise Exception("Frame was not present after %s seconds!" % timeout)

def switch_to_window(driver, window, timeout=Settings.SMALL_TIMEOUT):
    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    if isinstance(window, int):
        for x in range(int(timeout * 10)):
            try:
                window_handle = driver.window_handles[window]
                driver.switch_to.window(window_handle)
                return True
            except IndexError:
                now_ms = time.time() * 1000.0
                if now_ms >= stop_ms:
                    break
                time.sleep(0.1)
        raise Exception("Window was not present after %s seconds!" % timeout)
    else:
        window_handle = window
        for x in range(int(timeout * 10)):
            try:
                driver.switch_to.window(window_handle)
                return True
            except NoSuchWindowException:
                now_ms = time.time() * 1000.0
                if now_ms >= stop_ms:
                    break
                time.sleep(0.1)
        raise Exception("Window was not present after %s seconds!" % timeout)

def current_window_handle(driver, timeout=Settings.SMALL_TIMEOUT):
    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    for x in range(int(timeout * 10)):
        try:
            driver.current_window_handle
            return True
        except NoSuchWindowException:
            now_ms = time.time() * 1000.0
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
    raise Exception("Window handle was not present after %s seconds!" % timeout)

def window_handles(driver, timeout=Settings.SMALL_TIMEOUT):
    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    for x in range(int(timeout * 10)):
        try:
            driver.window_handles
            return True
        except NoSuchWindowException:
            now_ms = time.time() * 1000.0
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
    raise Exception("Window handle was not present after %s seconds!" % timeout)