import os
from time import sleep, time
from random import uniform, randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Sleeps for a random period between a and b
def wait_between(a,b):
	rand = uniform(a, b) 
	sleep(rand)

# Cycle through all the expected conditions
class AnyEc:
    def __init__(self, *args):
        self.ecs = args
    def __call__(self, driver):
        for fn in self.ecs:
            try:
                if fn(driver): return True
            except:
                pass

projectRoot = os.path.dirname(os.path.realpath(__file__))

# Place the geckodriver in the project root
driver = webdriver.Firefox(executable_path = projectRoot + "/geckodriver")

url='https://www.google.com/recaptcha/api2/demo'

driver.get(url)
driver.maximize_window()

# Move into the first iFrame (checkbox)
driver.switch_to.frame(driver.find_elements_by_tag_name("iframe")[0])

# Wait 10 seconds for checkbox to load
checkBox = WebDriverWait(driver, 5).until(
		EC.presence_of_element_located((By.ID ,"recaptcha-anchor"))
		) 

wait_between(0.5, 0.7)

checkBox.click()

# Move out of iFrame to main window
driver.switch_to.default_content();

# Move into the second iFrame (image captcha)
driver.switch_to.frame(driver.find_elements_by_tag_name("iframe")[1])

# Wait 5 seconds for presence of either the 3x3 or the 4x4 image
# to load failing which try to submit (verified cookie case)
try:
	imageCaptcha = WebDriverWait(driver, 10).until( AnyEc(
		EC.presence_of_element_located(
			(By.XPATH, '//*[@class="rc-image-tile-33"]')
		)
	))
except:
	driver.switch_to.default_content();
	driver.find_element_by_id("recaptcha-demo-submit").click()