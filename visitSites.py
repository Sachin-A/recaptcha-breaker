import os
import pickle
from selenium import webdriver

projectRoot = os.path.dirname(os.path.realpath(__file__))
driver = webdriver.Firefox(executable_path = projectRoot + "/geckodriver")

websites = ["http://www.google.com", "http://www.youtube.com"]
cookies = []

for website in websites:
	driver.get(website)
	cookies.extend(driver.get_cookies())

print cookies

# Store our cookies in a file
pickle.dump(cookies, open("cookies.pkl", "wb"))
