import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def gris(driver, filepath):

	driver.get("https://images.google.com")

	# Click on file upload icon
	driver.find_element_by_id("qbi").click()

	# Upload file through key press simulation
	driver.find_element_by_id("qbfile").send_keys(filepath)

	# Wait for search to complete and suggestion to appear
	WebDriverWait(driver, 10).until(
		EC.presence_of_element_located(
			(By.CLASS_NAME, '_gUb')
		)
	)

	return driver.find_elements_by_class_name("_gUb")[0].text
