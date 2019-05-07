import getopt
import getpass
import signal
import time
from sys import argv
from random import randint
from datetime import datetime
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

def sig_int(signal, frame):
	print('quiting...')
	driver.quit()
	exit()

def setup():
	helpmsg = '''autoclick.py - a python script that answers multiple choices questions automatically on irs.zuvio.com.tw
Usage: python3 autoclick.py [url] [-n seconds]
Author: Andy Chen

Options:
  -n  SECONDS        refresh the website every SECONDS seconds (default: 3)
  --no-sign-in       the script will not try to sign in the course'''
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


sec, need_sign_in, url = setup()

email = input('Enter your email: ')
password = getpass.getpass()

screen_size=(960,4320)
display = Display(size=screen_size)
display.start()

options = webdriver.firefox.options.Options()
options.add_argument('--headless') #hide the browser window
driver = webdriver.Firefox(options= options)

driver.set_window_size(*screen_size)
driver.get('https://irs.zuvio.com.tw')
signal.signal(signal.SIGINT, sig_int)

login = False
while not login:
	driver.find_element_by_id('email').send_keys(email)
	driver.find_element_by_id('password').send_keys(password)
	driver.find_element_by_id('login_btn').click()
	driver.implicitly_wait(1)
	try:
		driver.find_element_by_id('login_btn')
	except NoSuchElementException: #if it does not exist the login button, which means you have logged in
		login=True
	else:
		print('Wrong email or password. Please try again.')
		email = input('Enter your email: ')
		password = getpass.getpass()

del password
print('Logged in successfully')
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
		except NoSuchElementException:
			pass

	driver.refresh()
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
					option_list=driver.find_elements_by_class_name('i-a-c-q-t-q-b-b-b-o-b-text')
					chose_option=randint(0,len(option_list)-1)
					option_list[chose_option].click() #click the random option
					driver.find_element_by_class_name('i-a-c-f-b-submit-btn').click() #click 'confirm'
					print('{{{'+str(datetime.now().time())[:8]+'}}} answered',chose_option+1, 'to a question successfully')
					driver.get(url)
				except NoSuchElementException: #if there are no unanswered questions
					pass
			
