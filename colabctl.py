import sys
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import pickle
import time
import validators

def sleep(seconds):
    for i in range(seconds):
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            continue


def exists_by_text2(driver, text):
    try:
        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH,"//*[contains(text(), '"+str(text)+"')]")))
    except Exception:
        return False
    return True


def exists_by_xpath(driver, thex, howlong):
    try:
        WebDriverWait(driver, howlong).until(ec.visibility_of_element_located((By.XPATH, thex)))
    except:
        return False


def exists_by_text(driver, text):
    driver.implicitly_wait(2)
    try:
        driver.find_element(By. XPATH, "//*[contains(text(), '"+str(text)+"')]")
    except NoSuchElementException:
        driver.implicitly_wait(5)
        return False
    driver.implicitly_wait(5)
    return True


def user_logged_in(driver):
    try:
        driver.find_element(By.XPATH, '//*[@id="file-type"]')
    except NoSuchElementException:
        driver.implicitly_wait(5)
        return False
    driver.implicitly_wait(5)
    return True


def wait_for_xpath(driver, x):
    while True:
        try:
            driver.find_element(By.XPATH, x)
            return True
        except:
            time.sleep(0.1)
            pass


def scroll_to_bottom(driver):
    SCROLL_PAUSE_TIME = 0.5
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def file_to_list(filename):
    colabs = []
    for line in open(filename):
        if validators.url(line):
            colabs.append(line)
    return colabs


def switch_to_tab(driver, tab_index):
    print("Switching to tab " + str(tab_index))
    try:
        driver.switch_to.window(driver.window_handles[tab_index])
    except:
        print("Error switching tabs.")
        return False


def new_tab(driver, url, tab_index):
    print("Opening new tab to " + str(url))
    try:
        driver.execute_script("window.open('" + str(url) + "')")
    except:
        print("Error opening new tab.")
        return False
    switch_to_tab(driver, tab_index)
    return True
    

fork = sys.argv[1]
timeout = int(sys.argv[2])
colab_urls = file_to_list('notebooks.csv')

if len(colab_urls) > 0 and validators.url(colab_urls[0]):
    colab_1 = colab_urls[0]
else:
    raise Exception('No notebooks')

chrome_options = Options()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument('--headless') # uncomment for headless mode
chrome_options.add_argument('--no-sandbox')
#chrome_options.add_argument("user-data-dir=profile") # left for debugging
chrome_options.add_argument('--disable-dev-shm-usage')
wd = webdriver.Chrome('chromedriver', options=chrome_options)

wd.get(colab_1)
try:
    for cookie in pickle.load(open("gCookies.pkl", "rb")):
        wd.add_cookie(cookie)
except Exception:
    pass
wd.get(colab_1)

if exists_by_text(wd, "Sign in"):
    print("No auth cookie detected. Please login to Google.")
    wd.close()
    wd.quit()
    chrome_options_gui = Options()
    chrome_options_gui.add_argument('--no-sandbox')
    #chrome_options.add_argument("user-data-dir=profile") # left for debugging
    chrome_options_gui.add_argument('--disable-infobars')
    wd = webdriver.Chrome('chromedriver', options=chrome_options_gui)
    wd.get("https://accounts.google.com/signin")
    wait_for_xpath(wd, '//*[@id="yDmH0d"]')
    wd.find_element_by_name("identifier").send_keys("supp8255@gmail.com")
    wd.find_element_by_xpath("//*[@id='identifierNext']/div/button/span").click()
    wd.implicitly_wait(4)
    wd.find_element_by_name("password").send_keys("supp123456")
    wd.find_element_by_xpath("//*[@id='passwordNext']/div/button/span").click()
    print("Login detected. Saving cookie & restarting connection.")
    time.sleep(5)
    pickle.dump(wd.get_cookies(), open("gCookies.pkl", "wb"))
    complete = False

while (complete == False):
    for colab_url in colab_urls:
        complete = False
        wd.get(colab_url)
        print("Logged in.") # for debugging
        running = False
        wait_for_xpath(wd, '//*[@id="file-menu-button"]/div/div/div[1]')
        print('Notebook loaded.')
        sleep(10)

        while (running == False):
            if exists_by_text(wd, "Runtime disconnected"):
                try:
                    wd.find_element_by_xpath('//*[@id="ok"]').click()
                except NoSuchElementException:
                    pass
            if exists_by_text2(wd, "Notebook loading error"):
                wd.get(colab_url)
            try:
                if not running:
                    sleep(5)
                    wd.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.SHIFT + Keys.F9)
                    wd.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.F9)
                    running = True
            except NoSuchElementException:
                pass
            if running:
                time.sleep(2)
                try:
                    link = wd.find_element_by_partial_link_text("https://accounts.google.com/o/oauth2")
                    new_tab(wd, link.get_attribute("href"), 1)
                    wd.find_element_by_css_selector('li.JDAKTe.ibdqA.W7Aapd.zpCp3.SmR8').click()
                    wd.find_element_by_css_selector('#submit_approve_access > div > button').click()
                    auth_code = wd.find_element_by_css_selector('#view_container > div > div > div.pwWryf.bxPAYd > div > div.WEQkZc > div > form > span > section > div > div > div > span > div > textarea').text
                    switch_to_tab(wd,0)
                    wd.find_element_by_class_name("raw_input").send_keys(auth_code)
                    actions = ActionChains(wd)
                    actions.send_keys(Keys.ENTER).perform()
                    time.sleep(2)
                except NoSuchElementException:
                    pass
                if exists_by_text(wd,"Permit this notebook to access your Google Drive files?"):
                    try:
                        connect = wd.find_element_by_xpath('//*[@id="ok"]').click()
                        window_before = wd.window_handles[0]
                        window_after = wd.window_handles[1]
                        wd.switch_to_window(window_after)
                        wd.find_element_by_css_selector('li.JDAKTe.ibdqA.W7Aapd.zpCp3.SmR8').click()
                        wd.find_element_by_css_selector('#submit_approve_access > div > button').click()
                        time.sleep(1)
                    except NoSuchElementException:
                        pass
                scroll_to_bottom(wd)
                for output in wd.find_elements_by_tag_name('pre'):
                    if fork in output.text:
                        running = False
                        complete = True
                        break
                wd.switch_to.default_content()
                if complete:
                    break
            if complete:
                break
wd.quit()
