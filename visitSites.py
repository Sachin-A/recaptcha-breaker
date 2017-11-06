import os
import pickle
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

GOOGLE = "http://www.google.com"
YOUTUBE = "http://www.youtube.com"

projectRoot = os.path.dirname(os.path.realpath(__file__))
driver = webdriver.Firefox(executable_path=projectRoot + "/geckodriver")

websites = [GOOGLE, YOUTUBE]
cookies = []


def search_and_follow_up(search_term):
    element = driver.find_element_by_name("q")
    element.send_keys(search_term)
    element.submit()

    # wait until the google page shows the result
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "resultStats")))

    find_elements = driver.find_elements_by_xpath("//*[@id='rso']//h3/a")

    # this are all the links google returns
    links = [element.get_attribute("href") for element in find_elements[:5]]
    websites.extend(links)

    ActionChains(driver).move_to_element(find_elements[0]).click().perform()


def visit_websites():
    for website in websites:
        driver.get(website)
        if website == GOOGLE:
            search_and_follow_up("Cheese!\n")

        cookies.extend(driver.get_cookies())


def main():
    visit_websites()
    print(cookies)
    # Store our cookies in a file
    pickle.dump(cookies, open("cookies.pkl", "wb"))


main()
