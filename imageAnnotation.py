import os
from requests import get
from selenium import webdriver
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


sss_url = "http://swoogle.umbc.edu/SimService/GetSimilarity"

def sss(s1, s2, type='relation', corpus='webbase'):
	try:
		response = get(sss_url, params={'operation':'api','phrase1':s1,'phrase2':s2,'type':type,'corpus':corpus})
		return float(response.text.strip())
	except:
		print 'Error in getting similarity for %s: %s' % ((s1,s2), response)
		return 0.0
