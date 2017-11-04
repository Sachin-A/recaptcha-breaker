import os
import math
import random
from PIL import Image
from time import sleep, time
from selenium import webdriver
import selenium.common.exceptions as e
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Sleeps for a random period between a and b
def wait_between(a,b):
	rand = random.uniform(a, b)
	sleep(rand)

def download_image(driver, element, path, numRows):
	loc = element.location
	size = element.size

	driver.save_screenshot(path)

	image = Image.open(path)

	w = size['width']
	h = size['height']
	left = int(loc['x'])
	top = int(loc['y'])
	right = int(loc['x'] + w)
	bottom = int(loc['y'] + h)
	image = image.crop((left, top, right, bottom))
	image.save(path, 'png')

	captchaImage = Image.open(path)

	tWidth = w / numRows
	tHeight = h / numRows

	print "Width: ",  w
	print "Height: ",  h
	print "Tile width: ",  tWidth
	print "Tile height: ",  tHeight

	for i in range(numRows):
		for j in range(numRows):

			print "x-min: ", int(i * tWidth)
			print "y-min: ", int(j * tHeight)
			print "x-max: ", int(w - ((numRows - i - 1) * tWidth))
			print "y-max: ", int(h - ((numRows - j - 1) * tHeight))
			tile = image.crop(
				(
					int(i * tWidth), \
					int(j * tHeight), \
					int(w - ((numRows - i - 1) * tWidth)), \
					int(h - ((numRows - j - 1) * tHeight))
				)
			)
			tilepath = os.path.splitext(path)[0] + "_" + str(i * numRows + j) + ".png"
			tile.save(tilepath, 'png')

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

# Wait for checkbox to load
checkBox = WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.ID ,"recaptcha-anchor"))
		) 

wait_between(0.5, 0.7)

checkBox.click()

# actionChains = ActionChains(driver)

# Move out of iFrame to main window
driver.switch_to.default_content();

# Move into the second iFrame (image captcha)
driver.switch_to.frame(driver.find_elements_by_tag_name("iframe")[1])

challengeNumber = 0

while(1):

	# Wait for presence of either the 3x3 or the 4x4 challenge
	# to load failing which try to submit (verified cookie case)
	try:
		print "Waiting for image captcha"
		WebDriverWait(driver, 10).until(
			EC.presence_of_element_located(
				(By.ID, 'rc-imageselect')
			)
		)
		print "Found!"
	except:
		print "Presence of image captcha undetected. Proceeding."
		driver.switch_to.default_content();
		driver.find_element_by_id("recaptcha-demo-submit").click()
	
	# Wait till previous challenge images are deleted and
	# the new ones are added to dom
	wait_between(2, 3)

	# Gather all the img web elements in the challenge iframe only
	candidateImages = driver.find_elements_by_tag_name("img")
	numRows = int(math.sqrt(len(candidateImages)))
	print "NumRows: ", numRows
	randomIds = random.sample(range(len(candidateImages)), 3)

	for i in range(len(randomIds)):

		# Browser refresh between clicks results in stale elements so
		# update img WebElements between clicks
		candidateImages = driver.find_elements_by_tag_name("img")

		x = randomIds[i]
		print "Image no: ", x
		theChosenOne = candidateImages[x]

		if(i == 0):
			download_image(driver, candidateImages[0], "images/" + str(challengeNumber) + ".png", numRows)
			wait_between(9, 10)
			##
			## Todo: Tag analysis goes here
			##

		# actionChains.context_click(driver.find_elements_by_class_name("rc-image-tile-wrapper")[0]) \
		# .send_keys(Keys.ARROW_DOWN) \
		# .send_keys(Keys.ARROW_DOWN) \
		# .send_keys(Keys.ARROW_DOWN) \
		# .send_keys(Keys.ARROW_DOWN) \
		# .send_keys(Keys.RETURN) \
		# .perform()

		# Handle stale element in the short span between
		# finding element and clicking on it
		try:
			print "1st try"
			theChosenOne.find_element_by_xpath('..').click()

		except e.StaleElementReferenceException:
			print "2nd try"
			candidateImages = driver.find_elements_by_tag_name("img")
			theChosenOne = candidateImages[x]
			theChosenOne.find_element_by_xpath('..').click()

		wait_between(0.5, 0.7)

		# Click on verify after 3 selections
		if (i == 2):
			print "Trying to pass current challenge"
			print "Clicking on verify!"
			driver.find_element_by_id("recaptcha-verify-button").click()
			break

	challengeNumber+=1;
