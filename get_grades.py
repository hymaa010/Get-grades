#!/bin/python
import asyncio
from asyncio import create_task
import token
import aiohttp
from bs4 import BeautifulSoup

from hashlib import md5 

from filecmp import cmp

import tkinter as tk
from tkinter import messagebox
import colorama
from colorama import Fore 

import time 
import sys
import os

import platform
from random import random, seed
import math

from toml import dumps, loads, load

runtime_start = time.perf_counter()

seed()

links_name = 'links.toml'
file_name = 'grades.toml'
backup_name = 'grades_backup.toml'
user_info_name = 'user_info.txt'
nLogins = 1 
nGotgrades = 1

mode_name = 'normal'
duration_time = 120
 

AppleWebKit = f'{math.floor(50 * random()) + 500}.{math.floor(99 * random())}'
Chrome = f'{math.floor(20 * random()) + 90}.{math.floor(9 * random())}.{math.floor(9 * random())}.{math.floor(9 * random())}'
ENG_URLs = {'Main': 'https://eng.asu.edu.eg/', 'Login': 'https://eng.asu.edu.eg/public/login', 'Dashboard': 'https://eng.asu.edu.eg/public/dashboard', 'Mycourses': 'https://eng.asu.edu.eg/public/dashboard/my_courses', 'Courses': 'https://eng.asu.edu.eg/study/studies/student_courses'}
ENG_headers = {'User-Agent': f'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/{AppleWebKit} (KHTML, like Gecko) Chrome/{Chrome} Safari/{AppleWebKit}', 'Content-Type': 'application/x-www-form-urlencoded'}
Form_url = 'https://docs.google.com/forms/d/e/1FAIpQLSeP5dXix5NNcIg5gKDhFiG-RBmixi7qy5s1gM6g2WS84GlLMg/formResponse'


# For color in Windows cmd
if platform.system() == 'Windows':
    colorama.init(convert=True)
    
def input_mode(): 
    global user_info_name

    global mode_name
    global duration_time
    mode_name_parase = {'i': 'infinity', 'n': 'normal', 'd': 'duration', 'inf': 'information','normal': 'normal', 'infinity': 'infinity', 'duration': 'duration', 'information': 'information'}
    while True:
            mode_name = input(Fore.YELLOW + "To select modes type what is in brackets (n)ormal or (i)nfinity or (d)uration or (inf) for information on each mode: ").replace(' ', '')
            mode_name = mode_name_parase[mode_name.lower()]
            if mode_name == 'infinity' or mode_name == 'normal':
                break
            elif mode_name == 'duration':
                while True:
                    duration_time = input(Fore.YELLOW + 'Type number of minutes +/- ~10%% betweern every duration: ').replace(' ', '')
                    if duration_time.isdecimal():
                        duration_time = int(duration_time)
                        if duration_time < 10:                            
                            print(Fore.RED + "Error: Minmum duration is 10 min")
                            continue
                        break
                    else:
                        print(Fore.RED + "Error: Input is wrong please only type a hole number")
                break
            elif mode_name == 'i':
                print(Fore.CYAN + 'Normal mode: during normal, time if server is working good')
                print(Fore.CYAN + 'Infinity mode: during heavy server (when grades first apear on website), keeps trying until all grades are found')
                print(Fore.CYAN + 'Duration mode: during period for expected grades, keeps requesting grades every given amount of minutes +/- ~10%%')
                continue
            else:
                print(Fore.RED + "Error: Input is wrong please only normal or infinity or duration")
    
    print(Fore.CYAN + f"Info: running {mode_name} mode")

    

# gets user data from inputting and stores it 
def inputs_usr_data():
    global user_info_name

    

    email = input(Fore.YELLOW + "Input email: ").replace(' ', '')
    password = input(Fore.YELLOW + "Input Password: ")
    share_grade = input(Fore.YELLOW + "Do you want to share ONLY grades NO id or password with yes/no: ").replace(' ', '')
    input_mode()

    with open(user_info_name, 'w') as file:
        file.write(email + '\n')
        file.write(password + '\n')
        file.write(share_grade)
    
    return check_user_data(email, password, share_grade)

# gets user data from saved file
def get_usr_data(new_mode):
    global nGotgrades

    global user_info_name



    with open(user_info_name, 'r') as file:
        email = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
        password = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
        share_grade = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
    
    if share_grade == 'no' and nGotgrades == 1:
        while True:
            share_grade = input(Fore.YELLOW + "Do you want to share ONLY grades NO id or password with yes/no: ").replace(' ', '')
            if share_grade == 'yes' or share_grade == 'no':
                break
            else:
                print(Fore.RED + "Error: share grade must be yes or no in saved file please re-enter")

    if new_mode or nGotgrades == 1:
        input_mode()
        new_mode = False
    
    # Error checking
    if email == '' or password == '' or share_grade == '':
        print(Fore.RED + "Error: Email/Password/share grade is empty in saved file please re-enter them")
        return inputs_usr_data()
    
    elif share_grade != 'yes' and share_grade != 'no': 
        while True:
            print(Fore.RED + "Error: share grade must be yes or no in saved file please re-enter")
            share_grade = input(Fore.YELLOW + "Do you want to share ONLY grades NO id or password with yes/no: ").replace(' ', '')
            if share_grade == 'yes' or share_grade == 'no':
                break

    # Re-write info to file incase of change
    with open(user_info_name, 'w') as file:
        file.write(email + '\n')
        file.write(password + '\n')
        file.write(share_grade)
    share_grade = True if share_grade == 'yes' else False 
    

    return (email, password, share_grade) 
# makes sure user data is corerect
def check_user_data(email, password, share_grade):

    if email == '':
        print(Fore.RED + "Error: Please enter Email and password")
        return inputs_usr_data()

    if password == '':
        print(Fore.RED + "Error: Please enter password")
        return inputs_usr_data()
    
    if share_grade == '' or not (share_grade == 'yes' or share_grade == 'no'):
        print(Fore.RED + "Error: Error with saved file please re-enter")
        return inputs_usr_data()

    share_grade = True if share_grade == 'yes' else False 
        
    
    return (email, password, share_grade)

# Logs into website and returns the cookies to stay logged in
async def Login(session, email, password):    
    global nGotgrades
    global nLogins


    login_start = time.perf_counter()
    login_params = {'email': email, 'password': password}
    
    # Get website to get token
    async with session.get(ENG_URLs["Login"], headers=ENG_headers) as Eng:
        soup = BeautifulSoup(await Eng.read(), 'lxml')
        print(Fore.WHITE + f'Info: login number {nLogins} first step')
        login_params["_token"] = soup.find('input', {'name': '_token'})["value"]
    
    # Posts for actual login 
    async with session.post(ENG_URLs["Login"], headers=ENG_headers, data=login_params) as Eng:
        soup = BeautifulSoup(await Eng.read(), 'lxml')
        print(Fore.WHITE + f'Info: login number {nLogins} second step')
        if not soup.find('div', {'class': 'alert alert-danger'}) is None:
            print(Fore.RED +'Error: Username or password wrong')
            input(Fore.YELLOW + 'Press Enter to exit')
            sys.exit()
        
    nLogins += 1
    print(Fore.WHITE + f'Info: Login Took {round(time.perf_counter() - login_start, 3)}s ')

# Gets Url and logs in if needed 
async def get_html(session, URL, email, password, urlname=''):
    async with session.get(URL, headers=ENG_headers, allow_redirects=False) as Eng:
        ENG_read= await Eng.read()
        ENG_status = Eng.status
        if ENG_status == 302 and Eng.headers["Location"] ==  ENG_URLs["Login"]:
            await Login(session, email, password)
            print(Fore.WHITE + 'Info: Done Login')
            return await get_html(session, URL, email, password, urlname)
        elif ENG_status == 302:
            print(Fore.WHITE +   f'Info: redirecting {URL} to {Eng.headers["Location"]}')
            return await get_html(session, Eng.headers["Location"], email, password, Eng.headers["Location"])

    if urlname != '':
        return (urlname, ENG_read)
    else:
        return ENG_read

# finds all courses taken or current and returns there urls
async def get_urls(session, email, password): #, use_backup_links):
    global nGotgrades

    global links_name

    global mode_name

       #!!! TDOD 
    if (mode_name != 'duration' and nGotgrades != 1) or not os.path.isfile(links_name):
        urls = {}
        soup = BeautifulSoup(await get_html(session, ENG_URLs["Mycourses"], email, password), 'lxml')
        allas = soup.select('div.card-header > a')
        for a in allas:
            urls[a.text.split(':')[0] + ' ' + a.text.split('(')[-1].replace(')', '')] = a.attrs["href"] 

        with open(links_name, 'w') as links:
            #print(Fore.WHITE + "Info: Using generated links")
            links.write(str(dumps(urls).encode('utf8').decode()))
    else:
           with open(links_name, 'r') as links:
                print(Fore.WHITE + "Info: Using saved links")
                urls = loads(links.read())        
            #!!! TODO: check if loads is correct not load

    print(Fore.GREEN + f'Found Courses: {list(urls.keys())}')
    return urls

# uses get_html for all urls given and returns their task
async def get_htmls(session, urls, email, password):
    urls = await urls
    html_tasks = []
    html_tasks.append(create_task(get_html(session, ENG_URLs["Dashboard"], email, password, 'GPA')))
    for cousename, url in urls.items():
        html_tasks.append(create_task(get_html(session, url, email, password, cousename)))
    html_tasks.append(create_task(get_html(session, ENG_URLs['Courses'], email, password, 'Old')))
    return html_tasks

#  uses beautiful soup to find needed information in all urls given in the form of array of tasks and returns a dictionary containing the name and value of a grade.
async def return_Grads_Info(Eng):

    Grades_info={}
    Semester = ''
    for body in Eng[0:-1]:  
        body = await body
        ENG_soup = BeautifulSoup(body[1], 'lxml')
        if body[0] == 'GPA':
            Grades_info[body[0]] = ENG_soup.find('h3').text
            print(Fore.GREEN + f'Found GPA: {body[0]}: {Grades_info[body[0]]}')
        else:
            all_grades = ENG_soup.select('div.stats-widget-body > ul')
            grades_dict = {}
            for each_grade in all_grades:
                pair = each_grade.select('li')
                grades_dict[pair[0].text.replace('\r', '').replace('\n', '').replace('\t', '')] = pair[1].text.replace(' ', '')
            Grades_info[body[0]] = grades_dict
            if Semester  == '':
                Semester = body[0].split()[-2]
            if Semester in body[0]:
                print(Fore.GREEN + f'Found {body[0]}: {Grades_info[body[0]]}')

    old_grades = await Eng[-1]
    old_grades_soup = BeautifulSoup(old_grades[1], 'lxml')
    tables = old_grades_soup.select('div.card-body')
    grades = tables[-2].select('tr[style="display: none;"]')
    Old = {}
    for grade in grades:
        elements = grade.select('table.table.table-sm.m-0 > tbody > tr > td')
        Old[elements[0].text.replace('\r', '').replace('\n', '').replace('\t', '') + ' ' + elements[2].text.replace('\r', '').replace('\n', '').replace('\t', '')[:-1]] = {'Grade': elements[3].text.replace('\r', '').replace('\n', '').replace('\t', '')}

    terms = tables[-1].select('table.table.m-0:not(table.table-sm) > tbody > tr:not(tr[style="display: none;"])')
    for term in terms:
        elements = term.select('td')
        Old[elements[0].text.replace('\r', '').replace('\n', '').replace('\t', '') + ' ' + elements[1].text.replace('\r', '').replace('\n', '').replace('\t', '')] = {'Level': elements[3].text.replace('\r', '').replace('\n', '').replace('\t', ''), 'Term GPA / Hours': ' '.join(elements[4].text.replace('\r', '').replace('\n', '').replace('\t', '').split()), 'Cumulative GPA / Hours': ' '.join(elements[5].text.replace('\r', '').replace('\n', '').replace('\t', '').split()), 'Passed Hours':  elements[6].text.replace('\r', '').replace('\n', '').replace('\t', '')[0:-1]}
    print(Fore.CYAN + 'Info: only shoing current semester for more see grades.toml file')
    return (Grades_info , Old)

# Stores given dictionary in given file and returns if dict is empty and calls fill_form if needed
async def store_all(Grades_info, file):
    if Grades_info == None:
        return 
    
    file.write(dumps(Grades_info[0]))
# TODO: fix using old
   # file.write(dumps(Grades_info[1]))

# Fills out the form if user wants to 
async def fill_form(Grades_info, session, email):
    (Grades_info, Old) = Grades_info
    if Grades_info == None:
        return 
    
    data = {'entry.237252631': md5(email.encode()).hexdigest(), 'entry.2114208704': str(dumps(Grades_info).encode('utf8').decode(),), 'entry.757494702': str(dumps(Old).encode('utf8').decode(),)}
    async with session.post(Form_url, headers=ENG_headers, data=data):
        print(Fore.BLUE + "Info: Submmited form")

# Calls both store and fill functions according to arguments 
async def store_and_fill(Grades_info, file, session, email, share_grade):
    global user_info_name

    global mode_name

    if share_grade:
        await asyncio.gather(create_task(fill_form(Grades_info, session, email)), create_task(store_all(Grades_info, file)))
    else:
        await store_all(Grades_info, file)

        while True:
            if mode_name == 'normal':
                share_grade = input(Fore.YELLOW + "Do you want to share ONLY grades NO id or password use yes or no: ").replace(' ', '')
                share_grade = share_grade.lower()
                if share_grade == 'yes': 
                   # with open(user_info_name, 'r') as file:
                   #     _ = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
                   #     password = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
                   #     _ = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
                   #     mode_name = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
                   # with open(user_info_name, 'w') as file:
                   #     file.write(email + '\n')
                   #     file.write(password + '\n')
                   #     file.write(share_grade + '\n')
                    await fill_form(Grades_info, session, email)
                    break
                elif share_grade == 'no':
                    print(Fore.CYAN + "Info: Not sharing grade, Please share next time")
                    break
                else:
                    print(Fore.RED + "Error: Input is wrong please use only yes or no")
            else:
                print(Fore.CYAN + "Info: Not sharing grade, Please share next time")
                break
# Compares if to files are the same json
def compare_backup(file1, file2):
    with open(file1, 'r') as json1:
        grades1 = load(json1)
    with open(file2, 'r') as json2:
        grades2 = load(json2)
    if grades1 == grades2:
        return True
    else:
        return False

# Handels tasks and orders calling of functions
async def get_grades(session, file, email, password, share_grade): 
    tasks1 = create_task(get_urls(session, email, password))
    # TODO: makesure awaitng htmls properly 
    htmls = await get_htmls(session, tasks1, email, password)
    Grades_info = await return_Grads_Info(htmls)
    await store_and_fill(Grades_info, file, session, email, share_grade)

# responsible for creating file and opening session
async def main(session, new_info, new_mode, re_login):
    global nGotgrades

    global user_info_name
    global file_name
    global backup_name


    if os.path.isfile(user_info_name):
        if nGotgrades == 1 or new_info: 
            while True:
                use_stored = input(Fore.YELLOW + "Input: Use stored data? yes/no: ").replace(' ', '')
                if use_stored =='yes':
                    (email, password, share_grade) = get_usr_data(True)
                    break
                elif use_stored == 'no':
                    (email, password, share_grade) = inputs_usr_data()
                    break
                else:
                    print(Fore.RED + "Error: Input is wrong please use only yes or no")
        else:
            (email, password, share_grade) = get_usr_data(new_mode)
    else:
        (email, password, share_grade) = inputs_usr_data()    
    
    main_start = time.perf_counter()
    if re_login:
       await Login(session, email, password)

    with open(file_name, "w") as file: 
        await get_grades(session, file, email, password, share_grade)
    
    # Checks if backup file exists if not makes one 
    if not os.path.isfile(backup_name):
        print(Fore.WHITE + 'Info: Creating backup for grades')
        if platform.system() == "Linux" or platform.system() == "Mac":
            os.popen(f'cp {file_name} {backup_name}').read()
        else:
            os.popen(f'copy {file_name} {backup_name}').read()

    # Checks for changes if found gives an alert box
    if not compare_backup(file_name, backup_name):
        print(Fore.YELLOW + 'Warning: Changes were made to grades!!!')  
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning('New Grades', 'Check out changes!')
        while True:
                renew_grades = input(Fore.YELLOW + "Do you want to update saved grade_backup yes/no: ").replace(' ', '')
                if renew_grades == 'yes':
                    print(Fore.WHITE + 'Info: Creating backup for grades')
                    if platform.system() == "Linux" or platform.system() == "Mac":
                        os.popen(f'cp {file_name} {backup_name}').read()
                    else:
                        os.popen(f'copy {file_name} {backup_name}').read()
                    break
                elif renew_grades == 'no':
                    break
                else:
                    print(Fore.RED + "Error: Input is wrong please only yes or no")
        
    else:
        print(Fore.WHITE + 'Info: No Changes to grades')
    
    print(Fore.WHITE + f'Info: Took {round(time.perf_counter() - main_start, 3)}s to get grades')

# Responsible for calling main multiple times 
async def main_caller():
    global nGotgrades

    global mode_name
    global duration_time

    new_mode = True 
    new_info = True
    re_login = True

    async with aiohttp.ClientSession() as session:            
        while True: 
            current_time = math.floor(time.time()) 
            print(Fore.WHITE + f'Info: Current time: {time.ctime(current_time)} run number {nGotgrades}')
            
            # Catching errors and printing them
            try:
                await main(session, new_info, new_mode, re_login)
                if mode_name == 'infinity': 
                    mode_name = 'normal'
            except (KeyboardInterrupt, EOFError):
                sys.exit(130)
            except Exception as e:
                print(Fore.RED + f"failed with  run number {nGotgrades}, error is:  {e}")
            if mode_name == 'normal':
                while True:
                    run = input(Fore.YELLOW + "Type Enter to run again or type l to re-login (if errors apear) or c for change info or m to change mode or q to quit: ").replace(' ', '')
                    run = run.lower()
                    if run == '':
                        new_info = False
                        re_login = False
                        new_mode = False
                        if nGotgrades > 3:
                            print(Fore.RED + "Error: Too many requests wait 1 min")
                            await asyncio.sleep(60)
                        break
                    elif run == 'c':
                        new_info = True
                        re_login = False
                        new_mode = False
                        break
                    elif run == 'l':
                        new_info = False
                        re_login = True
                        new_mode = False
                        break
                    elif run == 'm':
                        new_info = False
                        re_login = False
                        new_mode = True
                        break
                    elif run == 'q':
                        sys.exit()
                    else:
                        print(Fore.RED + "Error: Input is wrong please use only c or l or m or type Enter or q only")

            nGotgrades += 1
            current_time = math.floor(time.time()) 

            if mode_name == 'duration':
                delay = math.floor(60 * duration_time * (1 + (0.5 - random()) * 0.2))
                print(Fore.WHITE + f'Info: Next in at {time.ctime(current_time + delay)} to exit use Ctr+C')
                await asyncio.sleep(delay)

asyncio.run(main_caller())
print(Fore.WHITE + f'Info: Total runtime is {round(time.perf_counter() - runtime_start, 3)}s')

# TODO: add course name for veiowng
# TODO: fix grades info old and new
# TODO: better formating of grades infor and year and name etc....

# TODO: add full scan option with seprate toml

# TODO: remove unwanted improts
# TODO: test everything


# TODO: use both md5 hash and sha 256

# TODO: add choose
# TODO: add check updates
