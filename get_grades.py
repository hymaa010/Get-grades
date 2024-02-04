import asyncio
from asyncio import create_task

import aiohttp
import ssl
import certifi

from bs4 import BeautifulSoup

import hashlib  


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
from tabulate import tabulate
from toml import dumps, load

runtime_start = time.perf_counter()

seed()
if platform.system() == "Linux" or platform.system() == "Mac":
    folder = './grades/'
else:
    folder = '.\grades\\'

links_name = folder + 'links.toml'
file_fast_name = folder + 'grades.toml'
fast_backup_name = folder + 'grades_backup.toml'
file_full_name = folder + 'grades_full.toml'
full_backup_name = folder + 'grades_full_backup.toml'
user_info_name = folder + 'user_info.txt'

nLogins = 1 
nGotgrades = 1

mode_name = 'full'
duration_time = 120
 

AppleWebKit = f'{math.floor(50 * random()) + 500}.{math.floor(99 * random())}'
Chrome = f'{math.floor(20 * random()) + 90}.{math.floor(9 * random())}.{math.floor(9 * random())}.{math.floor(9 * random())}'
ENG_URLs = {'Main': 'http://eng.asu.edu.eg/', 'Login': 'https://eng.asu.edu.eg/public/login', 'Dashboard': 'https://eng.asu.edu.eg/public/dashboard', 'Mycourses': 'https://eng.asu.edu.eg/public/dashboard/my_courses', 'Courses': 'https://eng.asu.edu.eg/study/studies/student_courses'}
ENG_headers = {'User-Agent': f'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/{AppleWebKit} (KHTML, like Gecko) Chrome/{Chrome} Safari/{AppleWebKit}', 'Content-Type': 'application/x-www-form-urlencoded'}
Form_url = 'https://docs.google.com/forms/d/e/1FAIpQLSfIrtrXvGU5nMzhJDTmCrXChwXhPaYCUwqETF_Zd7RpbHyOFg/formResponse'


# For color in Windows cmd
if platform.system() == 'Windows':
    colorama.init(convert=True)
    


def pretty_str(string):
    return ' '.join(string.replace('\r', '').replace('\n', '').replace('\t', '').split())

def input_mode(): 
    global user_info_name

    global mode_name
    global duration_time
    mode_name_parase = {'f': 'full', 'i': 'infinity', 'n': 'normal', 'd': 'duration', 'inf': 'information','normal': 'normal', 'infinity': 'infinity', 'duration': 'duration', 'information': 'information', 'full': 'full'}
    while True:
            mode_name = input(Fore.YELLOW + "To select modes type what is in brackets (f)ull or (n)ormal or (i)nfinity or (d)uration or (inf) for information on each mode: ").replace(' ', '')
            mode_name = mode_name.lower()
            if not mode_name in mode_name_parase.keys():
                print(Fore.RED + "Error: Input is wrong please only normal or infinity or duration")
                continue    
            else:
                mode_name = mode_name_parase[mode_name]
            
            if mode_name in ['full', 'infinity', 'normal']:
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
            elif mode_name == 'information':
                print(Fore.CYAN + 'Full mode: fully scans all grades including midterm grades')
                print(Fore.CYAN + 'Normal mode: use when server is working good or a little slow')
                print(Fore.CYAN + 'Infinity mode: during heavy server (when grades first apear on website), keeps trying until all grades are found')
                print(Fore.CYAN + 'Duration mode: during period for expected grades, keeps requesting grades every given amount of minutes +/- ~10%')
                continue
    
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
            print(Fore.RED +'Error: Username or Password wrong, reopen program and don\'t use saved!')
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

    urls = {}
    soup = BeautifulSoup(await get_html(session, ENG_URLs["Mycourses"], email, password), 'lxml')
    years = soup.select('select.form-control.form-control-lg > option')
    years = years[1:]
    for year in years:
        year = year.attrs['value']
        soup = BeautifulSoup(await get_html(session, ENG_URLs["Mycourses"] + '?years=' + year, email, password), 'lxml')
        
        allas = soup.select('div.card-header > a')
        for a in allas:
            urls[a.text] = a.attrs["href"] 
    with open(links_name, 'w') as links:
        links.write(str(dumps(urls).encode('utf8').decode()))
    return urls

# uses get_html for all urls given and returns their task
async def get_htmls(session, urls, email, password):
    html_tasks = []
    html_tasks.append(create_task(get_html(session, ENG_URLs["Dashboard"], email, password, 'GPA')))
    for cousename, url in urls.items():
        html_tasks.append(create_task(get_html(session, url, email, password, cousename)))
  #  html_tasks.append(create_task(get_html(session, ENG_URLs['Courses'], email, password, 'Old')))
    return html_tasks

# uses beautiful soup to find needed information in all urls given in the form of array of tasks and returns a dictionary containing the name and value of a grade.
async def return_Grads_Info(Eng):
    
    global file_full_name

    Grades_info={}
    Semester = ''
    dashbard = await Eng[0]
    ENG_soup = BeautifulSoup(dashbard[1], 'lxml')
    widgets = ENG_soup.select('div.simple-widget')
    Grades_info['Dashboard'] = {}
    for widget in widgets:
        Grades_info['Dashboard'][widget.find('p').text] = widget.find('h3').text

    print(Fore.GREEN + f'Cumulative GPA: {Grades_info["Dashboard"]["Cumulative GPA"]}')
    
    courses_table = [['Course Name', 'All Grades']] 
    for body in Eng[1:]:  
        body = await body
        ENG_soup = BeautifulSoup(body[1], 'lxml')
        
        course_code = body[0].split(':')[0] 
        course_name = ' '.join(body[0].split()[1:-2])
        course_term = body[0].split('(')[-1].replace(')', '')
        
        det_table = ENG_soup.select('table.table.table-striped.m-0 > tbody > tr > td')
        course_code = pretty_str(det_table[0].text)
        course_name = pretty_str(det_table[1].text) 
        course_dep = pretty_str(det_table[4].text) 
        course_bylaw = pretty_str(det_table[5].text) 
        course_grades_ = pretty_str(det_table[8].text) 
        course_hours_ = pretty_str(det_table[9].text) 
        
        course_details = {'Code': course_code,'Name': course_name, 'Term': course_term, 'Department': course_dep, 'Bylaw': course_bylaw, 'Grades (W/O/E)': course_grades_, 'Hours (L/O/W)': course_hours_} 
        
        all_grades = ENG_soup.select('div.stats-widget-body > ul')
        grades_dict = {}
        
        for each_grade in all_grades:
            pair = each_grade.select('li')
            grades_dict[pretty_str(pair[0].text)] = pretty_str(pair[1].text)

        Grades_info[course_code + ' ' + course_term] = {'Details': course_details, 'Grades': grades_dict}
        
        

        if Semester  == '':
            Semester = course_term
            print(Fore.GREEN + f'Showing Term: {Semester}')
        if Semester == course_term:
            course_grade = Grades_info[course_code + ' ' + course_term]['Grades']
            courses_table.append([course_name, course_grade])
    print(Fore.GREEN + tabulate(courses_table, headers='firstrow'))

    print(Fore.CYAN + f'Info: only showing current semester for more see {file_full_name} file')
    return Grades_info

# same as return_grade_info but for Courses parasing
async def return_Grads_Info_fast(full_grades):
    global file_fast_name


    full_grades = await full_grades
    full_grades_soup = BeautifulSoup(full_grades[1], 'lxml')
    tables = full_grades_soup.select('div.card-body')
    grades = tables[-2].select('tr[style="display: none;"]')

    Semester_order = {'Spring': 0 , 'Summer': 1, 'Fall': 2}
    courses_table = [['Course Name', 'Grade']]
    courses_table_temp = []
    Semester = ''
    
    Full_grades = {}
    for grade in grades:
        gras = grade.select('table.table.table-sm.m-0 > tbody > tr')
        for gra in gras:
            elements = gra.select('td')
            course_code = pretty_str(elements[0].text)
            course_name = pretty_str(elements[1].text)
            course_term = pretty_str(elements[2].text)
            course_grade = pretty_str(elements[3].text)
            course_gpa = pretty_str(elements[4].text)
            course_credit = pretty_str(elements[5].text)
            
            Full_grades[course_code + ' ' + course_term] = {'Course Code': course_code, 'Course Name': course_name, 'Term': course_term, 'Grade': course_grade, 'GPA': course_gpa, 'Credit Hours': course_credit}
            if Semester  == '':
                Semester = course_term 
            elif Semester != course_term:
                (sem_term, sem_year) = Semester.split()
                sem_year = int(sem_year)
                sem_term = Semester_order[sem_term]

                (cor_term, cor_year) = course_term.split()
                cor_year = int(cor_year)
                cor_term = Semester_order[cor_term]

                if (cor_year > sem_year) or (cor_year == sem_year and cor_term > sem_term):
                    courses_table_temp = []
                    Semester = course_term

            if Semester == course_term:
                courses_table_temp.append([course_name, f'{course_grade} ({course_gpa})'])
  
    print(Fore.GREEN + f'Showing Term: {Semester}')
    
    courses_table +=courses_table_temp
    print(Fore.GREEN + tabulate(courses_table, headers='firstrow'))

    terms = tables[-1].select('table.table.m-0:not(table.table-sm) > tbody > tr:not(tr[style="display: none;"])')
    for term in terms:
        elements = term.select('td')
        study_plan = pretty_str(elements[0].text)
        term_name = pretty_str(elements[1].text)
        study_year = pretty_str(elements[2].text)
        term_level = pretty_str(elements[3].text)
        term_gpa = pretty_str(elements[4].text)
        cum_gpa = pretty_str(elements[5].text)
        passed_h = elements[6].text.replace('\r', '').replace('\n', '').replace('\t', '').strip()
        Full_grades[term_name] = {'Study Plan': study_plan, 'Term': term_name, 'Study Year': study_year, 'Level': term_level, 'Term GPA / Hours': term_gpa, 'Cumulative GPA / Hours': cum_gpa,'Passed Hours': passed_h}
        if Semester == term_name:
            print(Fore.GREEN + f'GPA Accumlative: {Full_grades[term_name]["Cumulative GPA / Hours"]}')
            print(Fore.GREEN + f'GPA {term_name}: {Full_grades[term_name]["Term GPA / Hours"]}')

    print(Fore.CYAN + f'Info: only showing current semester for more see {file_fast_name} file')

    return Full_grades

# Stores given dictionary in given file and returns if dict is empty and calls fill_form if needed
async def store_all(Grades_info, file):
    if Grades_info == None:
        return 
    
    file.write(dumps(Grades_info))

# Fills out the form if user wants to 
async def fill_form(Grades_info, session, email, fill_type):
   
    if Grades_info == None:
        return 
    hash256 = hashlib.sha256(email.encode()).hexdigest()
    hashmd5 = hashlib.md5(email.encode()).hexdigest() 
    grades = str(dumps(Grades_info).encode('utf8').decode(),), 
    data = {'entry.496493016': hashmd5, 'entry.1214088606': hash256, 'entry.1453140975':  grades, 'entry.891805954': fill_type}
    async with session.post(Form_url, headers=ENG_headers, data=data):
        print(Fore.BLUE + "Info: Submmited form")

# Calls both store and fill functions according to arguments 
async def store_and_fill(Grades_info, file, session, email, share_grade, fill_type):
    global user_info_name

    global mode_name

    if share_grade:
        await asyncio.gather(create_task(fill_form(Grades_info, session, email, fill_type)), create_task(store_all(Grades_info, file)))
    else:
        await store_all(Grades_info, file)

        while True:
            if mode_name == 'normal':
                share_grade = input(Fore.YELLOW + "Do you want to share ONLY grades NO id or password use yes or no: ").replace(' ', '')
                share_grade = share_grade.lower()
                if share_grade == 'yes': 
                    # Wtites change
                    with open(user_info_name, 'r') as file:
                        _ = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
                        password = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
                        _ = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
                    with open(user_info_name, 'w') as file:
                        file.write(email + '\n')
                        file.write(password + '\n')
                        file.write(share_grade + '\n')
                    await fill_form(Grades_info, session, email, fill_type)
                    break

                elif share_grade == 'no':
                    print(Fore.CYAN + "Info: Not sharing grade, Please share next time")
                    break
                else:
                    print(Fore.RED + "Error: Input is wrong please use only yes or no")
            else:
                print(Fore.CYAN + "Info: Not sharing grade, Please share next time")
                break
# Compares if to files are the same toml 
def compare_backup(file1, file2):
    with open(file1, 'r') as toml1:
        grades1 = load(toml1)
    with open(file2, 'r') as toml2:
        grades2 = load(toml2)
    if grades1 == grades2:
        return True
    else:
        return False

# Handels tasks and orders calling of functions
async def get_grades_full(session, file, email, password, share_grade): 
    urls = await get_urls(session, email, password)
    htmls = await get_htmls(session, urls, email, password)
    Grades_info = await return_Grads_Info(htmls)
    await store_and_fill(Grades_info, file, session, email, share_grade, 'Fast')

async def get_grades_fast(session, file, email, password, share_grade):
    html_task = get_html(session, ENG_URLs['Courses'], email, password, 'Full')
    Grades_info_fast = await return_Grads_Info_fast(html_task)
    await store_and_fill(Grades_info_fast, file, session, email, share_grade, 'Full')
    


# responsible for creating file and opening session
async def main(session, new_info, new_mode, re_login):
    global mode_name
    global nGotgrades

    global folder
    global user_info_name
    global file_fast_name
    global backup_fast_name
    global file_full_name
    global full_backup_name

    if not os.path.isdir(folder):
        os.mkdir(folder)

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
    
    file_name = file_full_name if mode_name == 'full' else file_fast_name 
    backup_name = full_backup_name if mode_name == 'full' else fast_backup_name  
    
    main_start = time.perf_counter()
    if re_login:
       await Login(session, email, password)

    with open(file_name, "w") as file: 
        if mode_name != 'full':
            await get_grades_fast(session, file, email, password, share_grade)
        else:
            await get_grades_full(session, file, email, password, share_grade)

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

    ssl_context = ssl.create_default_context(cafile=certifi.where())
    conn = aiohttp.TCPConnector(ssl=ssl_context)

    async with aiohttp.ClientSession(connector=conn) as session:            
        while True: 
            current_time = math.floor(time.time()) 
            print(Fore.WHITE + f'Info: Current time: {time.ctime(current_time)} run number {nGotgrades}')
#TODO
            # Catching errors and printing them
            await main(session, new_info, new_mode, re_login)
            try:
                if mode_name == 'infinity': 
                    mode_name = 'normal'
                re_login = False
            except (KeyboardInterrupt, EOFError):
                sys.exit(130)
            except Exception as e:
                print(Fore.RED + f"failed with  run number {nGotgrades}, error is: {e} \n please Try again by pressing Enter")
                if mode_name != 'infinty':
                    re_login = True

            if mode_name == 'normal' or mode_name == 'full':
                while True:
                    run = input(Fore.YELLOW + "Type Enter to run again or c for change info or m to change mode or q to quit: ").replace(' ', '')
                    run = run.lower()
                    if run == '':
                        new_info = False
                        new_mode = False
                        if nGotgrades > 3:
                            print(Fore.RED + "Error: Too many requests wait 1 min")
                            await asyncio.sleep(60)
                        break
                    elif run == 'c':
                        new_info = True
                        new_mode = False
                        break
                    elif run == 'm':
                        new_info = False
                        new_mode = True
                        break
                    elif run == 'q':
                        return
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


# TODO: Update init.md

# TODO: add choose
# TODO: add check updates
# python.exe -m nuitka --standalone --enable-plugin=tk-inter .\get_grades.py -o Get_Grades_v5.1.exe