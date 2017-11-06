import os
import math
import random
from PIL import Image
from time import sleep, time
from selenium import webdriver
from operator import itemgetter
from imageAnnotation import *
import selenium.common.exceptions as e
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from multiprocessing.dummy import Pool as ThreadPool
poolSize = 2
pool = ThreadPool(poolSize)

# Sleeps for a random period between a and b
def wait_between(a,b):
	rand = random.uniform(a, b)
	sleep(rand)

def download_single(driver, element, path, numRows):
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

	# print "Width: ",  w
	# print "Height: ",  h
	# print "Tile width: ",  tWidth
	# print "Tile height: ",  tHeight

	for j in range(numRows):
		for i in range(numRows):

			# print "x-min: ", int(i * tWidth)
			# print "y-min: ", int(j * tHeight)
			# print "x-max: ", int(w - ((numRows - i - 1) * tWidth))
			# print "y-max: ", int(h - ((numRows - j - 1) * tHeight))
			tile = image.crop(
				(
					int(i * tWidth), \
					int(j * tHeight), \
					int(w - ((numRows - i - 1) * tWidth)), \
					int(h - ((numRows - j - 1) * tHeight))
				)
			)
			tile = tile.resize((int(w), int(h)), 1)
			tilepath = os.path.splitext(path)[0] + "_" + str(j * numRows + i) + ".png"
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

drivers = [] #[1]*poolSize
for i in range(poolSize):
    drivers.append(webdriver.Firefox(executable_path = projectRoot + "/geckodriver"))

url='https://www.google.com/recaptcha/api2/demo'

driver.get(url)
# driver.maximize_window()

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

challenge_type = "squares" # squares or images
solved_cache = [False]*16

if not os.path.exists(projectRoot + '/images') :
	os.makedirs(projectRoot + '/images')

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
		driver.switch_to.default_content()
		driver.find_element_by_id("recaptcha-demo-submit").click()
		print "Success!"
		break

	# Wait till previous challenge images are deleted and
	# the new ones are added to dom
	wait_between(2, 3)

	hint = driver.find_elements_by_tag_name("strong")[0].text

	# Gather all the img web elements in the challenge iframe only
	candidateImages = driver.find_elements_by_tag_name("img")
	numRows = int(math.sqrt(len(candidateImages)))
	# print "NumRows: ", numRows
	# randomIds = random.sample(range(len(candidateImages)), 3)

	print "Hint provided: ", hint

        if driver.find_elements_by_tag_name("html")[0].text.find("Select all images with") != -1:
            challenge_type = "images"

	download_image(driver, candidateImages[0], "images/" + str(challengeNumber) + ".png", numRows)

	#tags = []
	scores = []

	for j in range(len(candidateImages)):
                if j % poolSize != 0:
                    continue

                tilepaths = []
                tmpSolved = []
                for t in range(poolSize):
                    if j+t>=15:
                        break
                    tilepaths.append(projectRoot + "/images/" + str(challengeNumber) + "_" + str(j+t) + ".png")
                    tmpSolved.append(solved_cache[j+t])

                args = zip(drivers, tilepaths, tmpSolved, [hint]*len(drivers))
                results = pool.map(gris, args)

                for t in range(poolSize):
                    if j+t>=15:
                        break
                    solved_cache[j+t] = results[t][0]
                    scores[j+t] = results[t][1]
                    print "Search result: ", solved_cache[j+t], scores[j+t]

		#tags.extend(results)
                #for t in range(poolSize):
                #    if j+t>=15:
                #        break
                #    print "Search result: ", tags[j+t]

                #for t in range(poolSize):
                #    if j+t>=15:
                #        break
                #    scores.append([j+t, sss(hint, tags[j+t])])
                #    print "Similarity score: ", scores[j+t][1]

	scores = sorted(scores, key = itemgetter(1), reverse=True)
	print scores

	for i, score in enumerate(scores):

		# Browser refresh between clicks results in stale elements so
		# update img WebElements between clicks
		candidateImages = driver.find_elements_by_tag_name("img")

		theChosenOne = candidateImages[score[0]]

		# Handle stale element in the short span between
		# finding element and clicking on it
		try:
			print "1st try"
			theChosenOne.find_element_by_xpath('..').click()
                        if challenge_type == "images":
                            wait_between(1, 1.5)
                            candidateImages = driver.find_elements_by_tag_name("img")
                            download_single(driver, candidateImages[i], "images/" + str(challengeNumber) + "_" + str(i) + ".png", numRows)
                            solved_cache[i] = False

		except e.StaleElementReferenceException:
			print "2nd try"
			candidateImages = driver.find_elements_by_tag_name("img")
			theChosenOne = candidateImages[score[0]]
			theChosenOne.find_element_by_xpath('..').click()
                        if challenge_type == "images":
                            wait_between(1, 1.5)
                            candidateImages = driver.find_elements_by_tag_name("img")
                            download_single(driver, candidateImages[i], "images/" + str(challengeNumber) + "_" + str(i) + ".png", numRows)
                            solved_cache[i] = False

		wait_between(0.5, 0.7)

		# Click on verify after 3 selections
		if (i == numRows - 1 and challenge_type != "images") or (challenge_type == "images" and max([x[1] for x in scores]) < 0.01):
			print "Trying to pass current challenge"
			print "Clicking on verify!"
			driver.find_element_by_id("recaptcha-verify-button").click()
                        #if challenge_type != "images":
                        solved_cache = [False]*16
			break

	challengeNumber+=1;
