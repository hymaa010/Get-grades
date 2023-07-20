import asyncio
from asyncio import create_task
import token
import aiohttp
from bs4 import BeautifulSoup

from json import dumps, loads
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

runtime_start = time.perf_counter()

seed()

links_name = 'links.json'
links_backup_name = 'links_backup.json'
file_name = 'grade.json'
backup_name = 'grade_backup.json'
user_info_name = 'user_info.txt'
nLogins = 1 
nGotgrades = 1

new_info = False
re_login = False
mode_name = 'normal'
new_mode = False
duration_time = 120
 

AppleWebKit = f'{math.floor(50 * random()) + 500}.{math.floor(99 * random())}'
Chrome = f'{math.floor(20 * random()) + 90}.{math.floor(9 * random())}.{math.floor(9 * random())}.{math.floor(9 * random())}'
ENG_URLs = {'Main': 'https://eng.asu.edu.eg/', 'Login': 'https://eng.asu.edu.eg/public/login', 'Dashboard': 'https://eng.asu.edu.eg/public/dashboard', 'Mycourses': 'https://eng.asu.edu.eg/public/dashboard/my_courses', 'Courses': 'https://eng.asu.edu.eg/study/studies/student_courses'}
ENG_headers = {'User-Agent': f'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/{AppleWebKit} (KHTML, like Gecko) Chrome/{Chrome} Safari/{AppleWebKit}', 'Content-Type': 'application/x-www-form-urlencoded'}
Form_url = 'https://docs.google.com/forms/d/e/1FAIpQLSeP5dXix5NNcIg5gKDhFiG-RBmixi7qy5s1gM6g2WS84GlLMg/formResponse'


# For color in Windows cmd
if platform.system() == 'Windows':
    colorama.init(convert=True)
    
def input_mode(use_backup_links):
    global nGotgrades
    global nLogins

    global user_info_name
    global file_name
    global backup_name
    global links_name
    global links_backup_name

    global new_info
    global re_login
    global mode_name
    global new_mode  
    global duration_time


    if os.path.isfile(links_backup_name) and not use_backup_links and os.path.isfile(links_backup_name):
        use_backup_links = input(Fore.YELLOW + "Use fast mode? type fast or leave empty: ").replace(' ', '')

    if nGotgrades == 1 or new_mode:
        while True:
                mode_name = input(Fore.YELLOW + "To select modes type normal or infinity or duration or i for information on each mode: ").replace(' ', '')
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

    return use_backup_links

# gets user data from inputting and stores it 
def inputs_usr_data():
    global nGotgrades
    global nLogins

    global user_info_name
    global file_name
    global backup_name
    global links_name
    global links_backup_name

    global new_info
    global re_login
    global mode_name
    global new_mode  
    global duration_time
    

    email = input(Fore.YELLOW + "Input email: ").replace(' ', '')
    password = input(Fore.YELLOW + "Input Password: ")
    share_grade = input(Fore.YELLOW + "Do you want to share ONLY grades NO id or password with yes/no: ").replace(' ', '')
    use_backup_links = input_mode('')

    with open(user_info_name, 'w') as file:
        file.write(email + '\n')
        file.write(password + '\n')
        file.write(share_grade + '\n')
        file.write(mode_name + '\n')
        file.write(use_backup_links)
    
    return check_user_data(email, password, share_grade, use_backup_links)

# gets user data from saved file
def get_usr_data():
    global nGotgrades
    global nLogins

    global user_info_name
    global file_name
    global backup_name
    global links_name
    global links_backup_name

    global new_info
    global re_login
    global mode_name
    global new_mode  
    global duration_time


    with open(user_info_name, 'r') as file:
        email = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
        password = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
        share_grade = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
        mode_name = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
        use_backup_links = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
    if share_grade == 'no' and nGotgrades == 1:
        while True:
            share_grade = input(Fore.YELLOW + "Do you want to share ONLY grades NO id or password with yes/no: ").replace(' ', '')
            if share_grade == 'yes' or share_grade == 'no':
                break
            else:
                print(Fore.RED + "Error: share grade must be yes or no in saved file please re-enter")

    if new_mode:
        use_backup_links = input_mode(use_backup_links)
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

    if mode_name != 'normal' and mode_name != 'infinity' and mode_name != 'duration':
        print(Fore.RED + "Error: mode  in saved file please re-enter")
        new_mode = True
        use_backup_links = input_mode(use_backup_links)
        new_mode = False
    
    if use_backup_links != 'fast' and use_backup_links != '':
        print(Fore.RED + "Error: fast mode must be fast or empty in saved file please re-enter")
        use_backup_links = input_mode(use_backup_links)


    # Re-write info to file incase of change
    with open(user_info_name, 'w') as file:
        file.write(email + '\n')
        file.write(password + '\n')
        file.write(share_grade + '\n')
        file.write(mode_name + '\n')
        file.write(use_backup_links)
        
    use_backup_links = True if use_backup_links == 'fast' else False 
    share_grade = True if share_grade == 'yes' else False 
    
    if use_backup_links:
        print(Fore.CYAN + "Info: running fast")
    else:
        print(Fore.CYAN + "Info: running slow")

    return (email, password, share_grade, use_backup_links)

# makes sure user data is corerect
def check_user_data(email, password, share_grade, use_backup_links):
    
    if email == '':
        print(Fore.RED + "Error: Please enter Email and password")
        return inputs_usr_data()

    if password == '':
        print(Fore.RED + "Error: Please enter password")
        return inputs_usr_data()
    
    if share_grade == '' or not (share_grade == 'yes' or share_grade == 'no'):
        print(Fore.RED + "Error: Error with saved file please re-enter")
        return inputs_usr_data()

    if use_backup_links != 'fast' and use_backup_links != '':
        print(Fore.RED + f"Error: to use fast mode only type fast or leave empty")
        return inputs_usr_data()

    use_backup_links = True if use_backup_links == 'fast' else False 
    share_grade = True if share_grade == 'yes' else False 
        
    if use_backup_links:
        print(Fore.CYAN + "Info: running fast")
    else:
        print(Fore.CYAN + "Info: running slow")
    
    return (email, password, share_grade, use_backup_links)

# Logs into website and returns the cookies to stay logged in
async def Login(session, email, password):    
    global nGotgrades
    global nLogins

    global user_info_name
    global file_name
    global backup_name
    global links_name
    global links_backup_name

    global new_info
    global re_login
    global mode_name
    global new_mode  
    global duration_time

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
async def get_urls(session, email, password, use_backup_links):
    global nGotgrades
    global nLogins

    global user_info_name
    global file_name
    global backup_name
    global links_name
    global links_backup_name

    global new_info
    global re_login
    global mode_name
    global new_mode  
    global duration_time

        
    if not use_backup_links:
        urls = {}
        soup = BeautifulSoup(await get_html(session, ENG_URLs["Mycourses"], email, password), 'lxml')
        allas = soup.select('div.card-header > a')
        for a in allas:
            urls[a.text.split(':')[0] + ' ' + a.text.split('(')[-1].replace(')', '')] = a.attrs["href"] 

        with open(links_name, 'w') as links:
            print(Fore.WHITE + "Info: Using generated links")
            links.write(str(dumps(urls, ensure_ascii=False).encode('utf8').decode()))
        
        # Checks if backup file exesit if not makes one 
        print(Fore.WHITE + 'Info: Creating backup for links')
        if platform.system() == "Linux" or platform.system() == "Mac":
            os.popen(f'cp {links_name} {links_backup_name}').read()
        else:
            os.popen(f'copy /y {links_name} {links_backup_name}').read()

    else:
        if (not nGotgrades > 1) or (not mode_name == 'infinity') or (not mode_name == 'duration'):
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
            input(Fore.YELLOW + 'Press Enter to exit')
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
    html_tasks.append(create_task(get_html(session, ENG_URLs['Courses'], email, password, 'Old')))
    return html_tasks

#  uses beautiful soup to find needed information in all urls given in the form of array of tasks and returns a dictionary containing the name and value of a grade.
async def return_Grads_Info(ENG_task):

    Eng = await ENG_task
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
                print(Fore.GREEN + f'Found Grade: {body[0]}: {Grades_info[body[0]]}')

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
    print(Fore.CYAN + 'Info: only shoing current semester for more see grades.json file')
    return (Grades_info , Old)

# Stores given dictionary in given file and returns if dict is empty and calls fill_form if needed
async def store_all(Grades_info_task, file):
    await Grades_info_task
    Grades_info = Grades_info_task.result()[0]
    
    if Grades_info == None:
        return 
    
    file.write('\n'+str(dumps(Grades_info, ensure_ascii=False).encode('utf8').decode())+',')

# Fills out the form if user wants to 
async def fill_form(Grades_info_task, session, email):
    await Grades_info_task
    (Grades_info, Old) = Grades_info_task.result()
    
    if Grades_info == None:
        return 
    
    data = {'entry.237252631': md5(email.encode()).hexdigest(), 'entry.2114208704': str(dumps(Grades_info, ensure_ascii=False).encode('utf8').decode(),), 'entry.757494702': str(dumps(Old, ensure_ascii=False).encode('utf8').decode(),)}
    async with session.post(Form_url, headers=ENG_headers, data=data) as Eng:
        print(Fore.BLUE + "Info: Submmited form")

# Calls both store and fill functions according to arguments 
async def store_and_fill(Grades_info_task, file, session, email, share_grade):
    global nGotgrades
    global nLogins

    global user_info_name
    global file_name
    global backup_name
    global links_name
    global links_backup_name

    global new_info
    global re_login
    global mode_name
    global new_mode  
    global duration_time

    if share_grade:
        await asyncio.gather(create_task(fill_form(Grades_info_task, session, email)), create_task(store_all(Grades_info_task, file)))
    else:
        await store_all(Grades_info_task, file)

        while True:
            if mode_name == 'normal':
                share_grade = input(Fore.YELLOW + "Do you want to share ONLY grades NO id or password with yes/no: ").replace(' ', '')
            
                if share_grade == 'yes': 
                    with open(user_info_name, 'r') as file:
                        _ = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
                        password = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
                        _ = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
                        mode_name = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
                        use_backup_links = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
                    with open(user_info_name, 'w') as file:
                        file.write(email + '\n')
                        file.write(password + '\n')
                        file.write(share_grade + '\n')
                        file.write(mode_name + '\n')
                        file.write(use_backup_links)
                    await fill_form(Grades_info_task, session, email)
                    break
                elif share_grade == 'no':
                    print(Fore.CYAN + "Info: Not sharing grade, Please share next time")
                    break
                else:
                    print(Fore.RED + "Error: Input is wrong please use only yes or no")
            else:
                print(Fore.CYAN + "Info: Not sharing grade, Please share next time")
                break

# Handels tasks and orders calling of functions
async def get_grades(session, file, email, password, share_grade, use_backup_links):
    tasks1 = create_task(get_urls(session, email, password, use_backup_links))
    tasks2 = create_task(get_htmls(session, tasks1, email, password))
    tasks3 = create_task(return_Grads_Info(tasks2))
    tasks4 = create_task(store_and_fill(tasks3, file, session, email, share_grade))
    return tasks4

# responsible for creating file and opening session
async def main(session):
    global nGotgrades
    global nLogins

    global user_info_name
    global file_name
    global backup_name
    global links_name
    global links_backup_name

    global new_info
    global re_login
    global mode_name
    global new_mode  
    global duration_time

    if os.path.isfile(user_info_name):
        if nGotgrades == 1 or new_info: 
            while True:
                use_stored = input(Fore.YELLOW + "Input: Use stored data? yes/no: ").replace(' ', '')
                if use_stored =='yes':
                    new_mode = True
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
        tasks = await get_grades(session, file, email, password, share_grade, use_backup_links)
        await tasks
        file.seek(file.tell() - 1, os.SEEK_SET)
        file.truncate()
        file.write('\n]}')
        file.close()
    
    # Checks if backup file exists if not makes one 
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
    global nLogins

    global user_info_name
    global file_name
    global backup_name
    global links_name
    global links_backup_name

    global new_info
    global re_login
    global mode_name
    global new_mode  
    global duration_time

    async with aiohttp.ClientSession() as session:            
        while True: 
            current_time = math.floor(time.time()) 
            print(Fore.WHITE + f'Info: Current time: {time.ctime(current_time)} run number {nGotgrades}')
            
            # Catching errors and printing them
            try: 
                await main(session)
                if mode_name == 'infinity': 
                    mode_name = 'normal'
            except (KeyboardInterrupt, EOFError):
                sys.exit(130)
            except Exception as e:
                print(Fore.RED + f"failed with  run number {nGotgrades}, error is:  {e}")
            if mode_name == 'normal':
                while True:
                    run = input(Fore.YELLOW + "Type Enter to run again or type l/L to re-login (if errors apear) or c/C for change info or m/M to change mode or q/Q to quit: ").replace(' ', '')
                    if run == '':
                        new_info = False
                        re_login = False
                        new_mode = False
                        if nGotgrades > 3:
                            print(Fore.RED + "Error: Too many requests wait 1 min")
                            await asyncio.sleep(60)
                        break
                    elif run == 'c' or run == 'C':
                        new_info = True
                        re_login = False
                        new_mode = False
                        break
                    elif run == 'l' or run == 'L':
                        new_info = False
                        re_login = True
                        new_mode = False
                        break
                    elif run == 'm' or run == 'M':
                        new_info = False
                        re_login = False
                        new_mode = True
                        break
                    elif run == 'q' or run == 'Q':
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

# TODO: add choose   
# TODO: add check updates