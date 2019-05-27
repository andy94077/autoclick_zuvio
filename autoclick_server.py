#!/usr/bin/env python3
import getopt
import getpass
import signal
import time
import re
from sys import argv
import random
from datetime import datetime
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

def sig_int(signal, frame):
	print('quiting...')
	driver.quit()
	display.stop()
	exit()

def setup():
	helpmsg = '''autoclick.py - a python script that answers multiple choices questions automatically on irs.zuvio.com.tw
Usage: python3 autoclick.py [url] [-n seconds]
Author: Andy Chen

Options:
  -n  SECONDS		 refresh the website every SECONDS seconds (default: 3)
  --no-sign-in		 the script will not try to sign in the course'''
	sec = 3
	need_sign_in = True
	try:
		opts, args = getopt.getopt(argv[1:], 'n:', ['help','no-sign-in'])
		for opt, arg in opts:
			if opt == '--help':
				print(helpmsg)
				exit()
			elif opt == '-n':
				sec = arg
			elif opt == '--no-sign-in':
				need_sign_in = False
	except getopt.GetoptError:
		print(helpmsg)
		exit(1)
	
	if len(args) > 1:
		print('Error: too many urls')
		print(helpmsg)
		exit(2)
	elif len(args) < 1:
		print('Error: missing the url')
		print(helpmsg)
		exit(3)
	return sec, need_sign_in, args[0]

def login(driver):
	driver.get('https://irs.zuvio.com.tw')
	email = input('Enter your email: ')
	password = getpass.getpass()
	logged_in = False
	while not logged_in:
		driver.find_element_by_id('email').send_keys(email)
		driver.find_element_by_id('password').send_keys(password)
		driver.find_element_by_id('login_btn').click()
		driver.implicitly_wait(1)
		try:
			driver.find_element_by_id('login_btn')
		except NoSuchElementException: #if it does not exist the login button, which means you have logged in
			logged_in=True
		else:
			print('Wrong email or password. Please try again.')
			email = input('Enter your email: ')
			password = getpass.getpass()
	print('Logged in successfully')


sec, need_sign_in, url = setup()

options = webdriver.firefox.options.Options()
options.add_argument('--headless') #hide the browser window
driver = webdriver.Firefox(options= options)

screen_size=(960,4320)
display = Display(size=screen_size)
display.start()

driver.set_window_size(*screen_size)
signal.signal(signal.SIGINT, sig_int)

login(driver)
driver.get(url)

signed_in = not need_sign_in
sign_in_url=url.replace('clickers','rollcall')
while True:
	if not signed_in:
		driver.get(sign_in_url)
		time.sleep(sec)
		try:
			driver.find_element_by_id('submit-make-rollcall').click()
			print('{{{'+str(datetime.now().time())[:8]+'}}} signed in')
			signed_in = True
			driver.get(url)
			time.sleep(3)
		except NoSuchElementException:
			pass
	try:
		driver.refresh()
	except:
		print('{{{'+str(datetime.now().time())[:8]+'}}} connection timeout')
		time.sleep(30)
		continue
	time.sleep(sec)

	#find some available questions
	questions_n = len(driver.find_elements_by_class_name("i-c-l-q-question-box"))
	if questions_n > 0:
		for i in range(questions_n):
			q = driver.find_elements_by_class_name('i-c-l-q-question-box')[i]
			if q.find_element_by_class_name('i-c-l-q-q-b-t-t-b-text').text in (u'單選題',u'多選題'):
				try:
					q.find_element_by_class_name('i-c-l-q-q-b-b-mini-box-gray') #choose the unanswered question
					q.click()

					#check if there is any constraints of the number of answers
					try:
						tag = driver.find_element_by_class_name('i-a-c-q-t-q-b-m-b-t-b-tag')
						opt_num_to_choose=int(re.search(r'\d+',tag.text[4]).group()) #應選n選項, 最多n選項
					except NoSuchElementException:
						opt_num_to_choose=1

					option_list=driver.find_elements_by_class_name('i-a-c-q-t-q-b-b-b-o-b-text')
					chosen_option_list = list(random.sample(range(len(option_list)),opt_num_to_choose))
					for j, chosen_option in enumerate(chosen_option_list):
						option_list[chosen_option].click() #click the random option
						chosen_option_list[j]+=1
					

					#if we choose the 'other' option, we have to type something
					try:
						driver.find_element_by_class_name('i-a-c-q-t-q-b-b-b-textareas').send_keys('CaCha!')
					except NoSuchElementException:
						pass

					driver.find_element_by_class_name('i-a-c-f-b-submit-btn').click() #click 'confirm'
					print('{{{'+str(datetime.now().time())[:8]+'}}} answered',', '.join(chosen_option_list), 'to a question successfully')
					driver.get(url)
				except NoSuchElementException: #if there are no unanswered questions
					pass
			
