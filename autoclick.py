#!/usr/bin/env python3
import os
import argparse
import getpass
import signal
import time
import re
from sys import argv
import random
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


def sig_int(signal, frame):
    print('quiting...')
    driver.quit()
    exit()


def color_str(s, color):
    cmap = {'g': '32', 'green': '32', 'r': '31', 'red': '31'}
    if color in cmap and 'TERM' in os.environ:
        return f'\033[1;{cmap[color]}m{s}\033[0m'
    return s


def parse_args():
    parser = argparse.ArgumentParser(description='a python script that answers multiple choices questions automatically on irs.zuvio.com.tw')
    parser.add_argument('url')
    parser.add_argument('-s', '--seconds', type=int, default=3, help='refresh the website every SECONDS seconds (default: %(default)s)')
    parser.add_argument('--no-sign-in', action='store_true', help='The script will not try to sign in the course')
    parser.add_argument('-g', '--gps', action='store_true', help='enable gps. Enabling gps feature will open the browser window.')
    parser.add_argument('-k', '--keep-signing-in', action='store_true', help='The program will keep trying to sign in even it has signed in.')
    args = parser.parse_args()
    return args


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
        except NoSuchElementException:  # if it does not exist the login button, which means you have logged in
            logged_in = True
        else:
            print('Wrong email or password. Please try again.')
            email = input('Enter your email: ')
            password = getpass.getpass()
    print(color_str('Logged in successfully', 'g'))


if __name__ == '__main__':
    args = parse_args()
    sec = args.seconds
    need_sign_in = not args.no_sign_in
    url = args.url
    gps = args.gps
    keep_signing_in = args.keep_signing_in

    options = webdriver.ChromeOptions()
    if gps:
        options.add_experimental_option('prefs', {'geolocation': True})
    else:
        options.add_argument('--headless')  # hide the browser window
    options.add_argument("--log-level=3")  # only show fatal messages
    driver = webdriver.Chrome(options=options)

    signal.signal(signal.SIGINT, sig_int)

    login(driver)

    driver.get(url)

    signed_in = not need_sign_in
    sign_in_url = url.replace('clickers', 'rollcall')
    while True:
        if keep_signing_in or not signed_in:
            driver.get(sign_in_url)
            time.sleep(sec)
            try:
                driver.find_element_by_id('submit-make-rollcall').click()
                print(f'[{str(datetime.now().time())[:8]}] {color_str("signed in", "g")}')
                print('\a', end='')
                signed_in = True
                driver.get(url)
                time.sleep(3)
            except NoSuchElementException:
                pass
        try:
            driver.refresh()
        except:
            print(f'[{str(datetime.now().time())[:8]}] {color_str("connection timeout", "r")}')
            time.sleep(30)
            continue
        time.sleep(sec)

        # find some available questions
        questions_n = len(driver.find_elements_by_class_name("i-c-l-q-question-box"))
        if questions_n > 0:
            for i in range(questions_n):
                q = driver.find_elements_by_class_name('i-c-l-q-question-box')[i]
                if q.find_element_by_class_name('i-c-l-q-q-b-t-t-b-text').text in (u'單選題', u'多選題'):
                    try:
                        q.find_element_by_class_name('i-c-l-q-q-b-b-mini-box-gray')  # choose the unanswered question
                        q.click()

                        # check if there is any constraints of the number of answers
                        try:
                            tag = driver.find_element_by_class_name('i-a-c-q-t-q-b-m-b-t-b-tag')
                            print(tag.text)
                            opt_num_to_choose = int(re.search(r'\d+', tag.text).group())  # 應選n選項, 最多n選項
                        except NoSuchElementException:
                            opt_num_to_choose = 1

                        option_list = driver.find_elements_by_class_name('i-a-c-q-t-q-b-b-b-o-b-text')
                        chosen_option_list = sorted(random.sample(range(len(option_list)), opt_num_to_choose))
                        for j, chosen_option in enumerate(chosen_option_list):
                            option_list[chosen_option].click()  # click the random option
                            chosen_option_list[j] += 1

                        # if we choose the 'other' option, we have to type something
                        try:
                            driver.find_element_by_class_name('i-a-c-q-t-q-b-b-b-textareas').find_element_by_xpath('.//textarea').send_keys('CaCha!')
                        except NoSuchElementException:
                            pass

                        driver.find_element_by_class_name('i-a-c-f-b-submit-btn').click()  # click 'confirm'
                        print('{{{' + str(datetime.now().time())[:8] + '}}} answered', ', '.join(map(str, chosen_option_list)), 'to a question successfully')
                        driver.get(url)
                    except NoSuchElementException:  # if there are no unanswered questions
                        pass
