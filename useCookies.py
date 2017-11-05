import os
import pickle
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

projectRoot = os.path.dirname(os.path.realpath(__file__))

# Place the geckodriver in the project root
driver = webdriver.Firefox(executable_path = projectRoot + "/geckodriver")

url='https://www.google.com/recaptcha/api2/demo'

driver.get(url)

# Add cookies previously gathered from various websites
cookies = pickle.load(open("cookies.pkl", "rb"))
print cookies
for cookie in cookies:
    driver.add_cookie(cookie)

# Move into the first iFrame (checkbox)
driver.switch_to.frame(driver.find_elements_by_tag_name("iframe")[0])

# Wait for checkbox to load
checkBox = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID ,"recaptcha-anchor")))

checkBox.click()
