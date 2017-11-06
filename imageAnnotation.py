import os
from config import keys
from requests import get
from selenium import webdriver
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

grisUrl="https://images.google.com"

def gris(args):
	driver = args[0]
	filepath = args[1]
        hint = args[2]

	if not os.path.isfile(filepath):
		return "z"

	driver.get(grisUrl)

	# Click on file upload icon
	driver.find_element_by_id("qbi").click()

	# Upload file through key press simulation
	driver.find_element_by_id("qbfile").send_keys(filepath)

	# Wait for search to complete and suggestion to appear
	try:
		WebDriverWait(driver, 20).until(
			EC.presence_of_element_located(
				(By.CLASS_NAME, '_gUb')
			)
		)
	except:
		return "z"

	tag = driver.find_elements_by_class_name("_gUb")[0].text
        score = sss(hint, tag)
        return (tag, score)

def clarifai(args):

	driver = args[0]
	filepath = args[1]
        hint = args[2]

	app = ClarifaiApp(api_key=keys['clarifai_key'])
	model = app.models.get("general-v1.3")

	image = ClImage(file_obj=open(filepath, 'rb'))
	response =  model.predict([image])

	tags = ''

	for x in response['outputs'][0]['data']['concepts']:
            print x
	    tags += ' '
	    tags += x['name']

	#return tags
	#tags = driver.find_elements_by_class_name("_gUb")[0].text
        score = sss(hint, tags)
        return (tags, score)

sss_url = "http://swoogle.umbc.edu/SimService/GetSimilarity"

def sss(s1, s2, type='relation', corpus='webbase'):
	try:
		response = get(sss_url, params={'operation':'api','phrase1':s1,'phrase2':s2,'type':type,'corpus':corpus})
		return float(response.text.strip())
	except:
		print 'Error in getting similarity for %s: %s' % ((s1,s2), response)
		return 0.0
