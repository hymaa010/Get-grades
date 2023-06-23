import asyncio
from asyncio import create_task
import aiohttp
from bs4 import BeautifulSoup

from json import dumps, loads
from hashlib import md5 

from filecmp import cmp

import tkinter as tk
from tkinter import messagebox
from colorama import init, Fore

import time 
import sys
import os
import platform

from random import random
import math

# runtime_start = time.perf_counter()

links_name = 'links.json'
links_backup_name = 'links_backup.json'
file_name = 'grade.json'
backup_name = 'grade_backup.json'
user_info_name = 'user_info.text'
nLogins = 1 
nGotgrades = 1 
AppleWebKit = f'{math.floor(50 * random()) + 500}.{math.floor(99 * random())}'
Chrome = f'{math.floor(20 * random()) + 90}.{math.floor(9 * random())}.{math.floor(9 * random())}.{math.floor(9 * random())}'
ENG_URLs = {'Main': 'https://eng.asu.edu.eg/', 'Login': 'https://eng.asu.edu.eg/public/login', 'Dashboard': 'https://eng.asu.edu.eg/public/dashboard', 'Mycourses': 'https://eng.asu.edu.eg/public/dashboard/my_courses'}
ENG_headers = {'User-Agent': f'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/{AppleWebKit} (KHTML, like Gecko) Chrome/{Chrome} Safari/{AppleWebKit}', 'Content-Type': 'application/x-www-form-urlencoded'}
Form_url = 'https://docs.google.com/forms/d/e/1FAIpQLSe-14O0Sey9zhDw4EKDAbjyifmcrdt8ZihH6vyezozM_Gc6Iw/formResponse'

# For color in windos cmd
if platform.system() == 'Windows':
    init(convert=True)

# gets user data from inputing and stores it 
def inputs_usr_data():
    email = input(Fore.YELLOW + "Input email: ")
    password = input(Fore.YELLOW + "Input Password: ")
    share_grade = input(Fore.YELLOW + "Do you want to share ONLY grades NO id or password with yes/no : ")
    use_backup_links = ''
    with open(user_info_name, 'w') as file:
        file.write(email + '\n')
        file.write(password + '\n')
        file.write(share_grade)
    
    return check_user_data(email, password, share_grade, use_backup_links)

# gets user data from saved file
def get_usr_data():
    with open(user_info_name, 'r') as file:
        email = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
        password = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
        share_grade = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
        use_backup_links = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')

        if email == '' or password == '' or share_grade == '' or (not (share_grade == 'yes' or share_grade == 'no')) or (use_backup_links != 'fast' and len(use_backup_links) != 0):
            print(Fore.RED + "Error: Problem with saved daa re-enter them")
            return inputs_usr_data()
    
    use_backup_links = True if use_backup_links == 'fast' else False 
    share_grade = True if share_grade == 'yes' else False 

    return (email, password, share_grade, use_backup_links)

# makse sure user data is corerect
def check_user_data(email, password, share_grade, use_backup_links):
    
    if email == '':
        print(Fore.RED + "Error: Please enter Email and password")
        return inputs_usr_data()
    if password == '':
        print(Fore.RED + "Error: Please enter password")
        return inputs_usr_data()
        
    if share_grade == '' or not (share_grade == 'yes' or share_grade == 'no'):
        print(Fore.RED + "Error: Please choose to give only Grades info with 'yes' or if you don't want to with 'no' NO id or password only hash(encrypted id) and Grades")
        return inputs_usr_data()

    if use_backup_links == '':
        print(Fore.WHITE + f"Info: runnig slow for fast use fast at end of {user_info_name} file after first use")
    elif use_backup_links != 'fast':
        print(Fore.RED + f"Error: 4th line in {user_info_name} either must be fast or empty or delete file")
        input(Fore.YELLOW + 'Press any key to exit')
        sys.exit()
    else:
        print(Fore.WHITE + "Info: running fast")

    use_backup_links = True if use_backup_links == 'fast' else False 
    share_grade = True if share_grade == 'yes' else False 
    
    return (email, password, share_grade, use_backup_links)

# Logs into website and returns the cookies to stay loged in
async def Login(session, email, password):    
    login_start = time.perf_counter()
    global nLogins
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
            input(Fore.YELLOW + 'Press any key to exit')
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
            print(Fore.WHITE + f'Info: redirecting {URL} to {Eng.headers["Location"]}')
            return await get_html(session, Eng.headers["Location"], email, password, Eng.headers["Location"])

    if urlname != '':
        return (urlname, ENG_read)
    else:
        return ENG_read

# finds all courses taken or current and returns there urls
async def get_urls(session, email, password, use_backuplinks):
    global links_name
    global links_backup_name
    
    if not use_backuplinks:
        urls = {}
        soup = BeautifulSoup(await get_html(session, ENG_URLs["Mycourses"], email, password), 'lxml')
        allas = soup.select('div.card-header > a')
        for a in allas:
            urls[a.text.split(':')[0]] = a.attrs["href"] 

        with open(links_name, 'w') as links:
            print(Fore.WHITE + "Info: Using generated links")
            links.write(str(dumps(urls, ensure_ascii=False).encode('utf8').decode()))
        
        # Checks if backup file exesit if not makes one 
        if not os.path.isfile(links_backup_name):
            print(Fore.WHITE + 'Info: Creating backup for links')
            if platform.system() == "Linux" or platform.system() == "Mac":
                os.popen(f'cp {links_name} {links_backup_name}').read()
            else:
                os.popen(f'copy {links_name} {links_backup_name}').read()

    else:
        await Login(session, email, password)

        if os.path.isfile(links_backup_name):
            with open(links_backup_name, 'r') as links_backup:
                print(Fore.WHITE + "Info: Using backedup links")
                urls = loads(links_backup.read())
        elif os.path.isfile(links_name):
            with open(links_name, 'r') as links:
                print(Fore.WHITE + "Info: Using saved links")
                urls = loads(links.read())        
        else:
            print(Fore.RED + "Error: Don't use fast now try without and then try again")
            input(Fore.YELLOW + 'Press any key to exit')
            sys.exit()

    print(Fore.GREEN + f'Found Courses: {list(urls.keys())}')
    return urls

# uses get_html for all urls given and returns their task
async def get_htmls(session, urls, email, password):
    urls = await urls
    html_tasks = []
    html_tasks.append(create_task(get_html(session, ENG_URLs["Dashboard"], email, password, 'GPA')))
    for cousename, url in urls.items():
        html_tasks.append(create_task(get_html(session, url, email, password, cousename)))
    return html_tasks

#  uses beautiful soup to find neded information in all urls given in form of array of tasks and returns a dictionary contating the name and value of a grade.
async def return_Grads_Info(ENG_task):
    Eng = await asyncio.gather(*(await ENG_task))
    Grades_info={}

    for body in Eng:  
        ENG_soup = BeautifulSoup(body[1], 'lxml')
        if body[0] == 'GPA':
            Grades_info[body[0]] = ENG_soup.find('h3').text
        else:
            all_grades = ENG_soup.select('div.stats-widget-body > ul')
            grades_dict = {}
            for each_grade in all_grades:
                pair = each_grade.select('li')
                grades_dict[pair[0].text.replace('\r', '').replace('\n', '').replace('\t', '')] = pair[1].text.replace(' ', '')
            Grades_info[body[0]] = grades_dict
        print(Fore.GREEN + f'Found Grade: {body[0]}: {Grades_info[body[0]]}')
    return Grades_info

# Stores given dictionary in given file and returns if dict is empty and calls fill_form if needed
async def store_all(Grades_info_task, file):

    await Grades_info_task
    Grades_info = Grades_info_task.result()
    if Grades_info == None:
        return 
    file.write('\n'+str(dumps(Grades_info, ensure_ascii=False).encode('utf8').decode())+',')

# Fills out the form if user wants to 
async def fill_form(Grades_info_task, session, email):
    await Grades_info_task
    Grades_info = Grades_info_task.result()
    if Grades_info == None:
        return 
    data = {'entry.1962996296': md5(email.encode()).hexdigest(), 'entry.826194171': str(dumps(Grades_info, ensure_ascii=False).encode('utf8').decode())}
    async with session.post(Form_url, headers=ENG_headers, data=data) as Eng:
        print(Fore.WHITE + "Info: Submmited form")

#calls both store and fill functions according to arguments 
async def store_and_fill (Grades_info_task, file, session, email, share_grade):

    if share_grade:
        await asyncio.gather(create_task(fill_form(Grades_info_task, session, email)), create_task(store_all(Grades_info_task, file)))
    else:
        await store_all(Grades_info_task, file)

# Handels tasks and orders calling of functions
async def get_grades(session, file, email, password, share_grade, use_backup_links):
    tasks1 = create_task(get_urls(session, email, password, use_backup_links))
    tasks2 = create_task(get_htmls(session, tasks1, email, password))
    tasks3 = create_task(return_Grads_Info(tasks2))
    tasks4 = create_task(store_and_fill(tasks3, file, session, email, share_grade))
    return tasks4

# responsible for creating file and opening session
async def main():
    global nGotgrades
    global file_name
    global backup_name

    if os.path.isfile(user_info_name):
        if nGotgrades == 1: 
            while True:
                use_stored = input(Fore.YELLOW + "Used stored data? yes/no: ")
                if use_stored =='yes':
                    (email, password, share_grade, use_backup_links) = get_usr_data()
                    break
                elif use_stored == 'no':
                    (email, password, share_grade, use_backup_links) = inputs_usr_data()
                    break
                else:
                    print(Fore.RED + "Error: Input is wrong please use only yes or no")
        else:
            (email, password, share_grade, use_backup_links) = get_usr_data()
    else:
        (email, password, share_grade, use_backup_links) = inputs_usr_data()
    
    main_start = time.perf_counter()

    with open(file_name, "w") as file: 
        file.write('{"Grades":[')
        async with aiohttp.ClientSession() as session:            
                tasks  = await get_grades(session, file, email, password, share_grade, use_backup_links)
                await tasks
        file.seek(file.tell() - 1, os.SEEK_SET)
        file.truncate()
        file.write('\n]}')
        file.close()
    
    # Checks if backup file exesit if not makes one 
    if not os.path.isfile(backup_name):
        print(Fore.WHITE + 'Info: Creating backup for grades')
        if platform.system() == "Linux" or platform.system() == "Mac":
            os.popen(f'cp {file_name} {backup_name}').read()
        else:
            os.popen(f'copy {file_name} {backup_name}').read()

    # Checks for changes if found gives an alert box
    if not cmp(file_name, backup_name):
        print(Fore.YELLOW + 'Warning: Changes were made to grades!!!')  
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning('New Grades', 'Check out changes!')
    else:
        print(Fore.WHITE + 'Info: No Changes to grades')
    
    print(Fore.WHITE + f'Info: Took {round(time.perf_counter() - main_start, 3)}s to get grades')

# Responsible for calling main multiple times 
async def main_caller():
    global nGotgrades
    while True: 
        current_time = math.floor(time.time()) 
        print(Fore.WHITE + f'Info: Current time: {time.ctime(current_time)}')
        
        await main()
        nGotgrades += 1
        # delay = math.floor(60 * 60 * 5 * random() + 60 * 30)
        input(Fore.YELLOW + 'Type Enter to close')
        sys.exit()
        # print(Fore.WHITE + f'Info: Next in at {time.ctime(current_time + delay)} to exit use Ctr+C')
        # await asyncio.sleep(delay)

asyncio.run(main_caller())
# print(Fore.WHITE + f'Info: Total runtime is {round(time.perf_counter() - runtime_start, 3)}s')
