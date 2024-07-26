import asyncio
from asyncio import create_task

import aiohttp
import ssl
import certifi

from bs4 import BeautifulSoup

import ctypes

import hashlib  

import colorama
from colorama import Fore 

from datetime import datetime
import time 
import sys
import os

from platform import system
from random import random, seed
from tabulate import tabulate
from toml import dumps, load

runtime_start = time.perf_counter()

seed()
if system() == "Linux" or system() == "Mac":
    folder = './grades/'
else:
    folder = '.\\grades\\'

links_name = folder + 'links.toml'
file_fast_name = folder + 'grades.toml'
fast_backup_name = folder + 'grades_backup.toml'
links_name_full = folder + 'links_full.toml'
file_full_name = folder + 'grades_full.toml'
full_backup_name = folder + 'grades_full_backup.toml'
user_info_name = folder + 'user_info.txt'

nLogins = 1 
nGotgrades = 1

mode_name = 'full'
duration_time = 120

new_mode = True 
new_info = True
re_login = True


def floor(x):
    return x // 1

AppleWebKit = f'{floor(50 * random()) + 500}.{floor(99 * random())}'
Chrome = f'{floor(20 * random()) + 90}.{floor(9 * random())}.{floor(9 * random())}.{floor(9 * random())}'
ENG_URLs = {'Main': 'http://eng.asu.edu.eg/', 'Login': 'https://eng.asu.edu.eg/public/login', 'Dashboard': 'https://eng.asu.edu.eg/public/dashboard', 'Mycourses': 'https://eng.asu.edu.eg/public/dashboard/my_courses', 'Courses': 'https://eng.asu.edu.eg/study/studies/student_courses'}
ENG_headers = {'User-Agent': f'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/{AppleWebKit} (KHTML, like Gecko) Chrome/{Chrome} Safari/{AppleWebKit}', 'Content-Type': 'application/x-www-form-urlencoded'}
Form_url = 'https://docs.google.com/forms/d/e/1FAIpQLSf0a9WXdUk-sQTbOkExmMRleHhV31f5c_S4P_gQLhYnFWtBHQ/formResponse'


# For color in Windows cmd
if system() == 'Windows':
    colorama.init(convert=True)

    
def pretty_str(string):
    return ' '.join(string.replace('\r', '').replace('\n', '').replace('\t', '').split())

def input_mode(): 
    global user_info_name

    global mode_name
    global duration_time
    mode_name_parase = {'f': 'full', 'n': 'normal', 'd': 'duration', 'inf': 'information', 'normal': 'normal', 'duration': 'duration', 'information': 'information', 'full': 'full'}
    while True:
        mode_name = input(Fore.YELLOW + "To select modes type what is in brackets (n)ormal or (f)ull or (d)uration or (inf) for information on each mode: ").replace(' ', '')
        mode_name = mode_name.lower()
        if not mode_name in mode_name_parase.keys():
            print(Fore.RED + "Error: Input is wrong please only normal or full or duration or information")
            continue    
        else:
            mode_name = mode_name_parase[mode_name]

        if mode_name in ['full', 'normal']:
            break
        elif mode_name == 'duration':
            while True:
                try: 
                    duration_time = int(input(Fore.YELLOW + 'Type number of minutes +/- ~10%% betweern every duration: ').replace(' ', ''))
                    if duration_time < 1:                            
                        print(Fore.RED + "Error: Minmum duration is 1 min")
                        continue
                    break
                except ValueError:
                    print(Fore.RED + "Error: Input is wrong please only type a hole number")
            break
        elif mode_name == 'information':
            print(Fore.CYAN + 'Normal mode: Only get current semester grades')
            print(Fore.CYAN + 'Full mode: Fully scans all grades including midterm grades')
            print(Fore.CYAN + 'Duration mode: During period for expected grades, keeps requesting grades every given amount of minutes +/- ~10%')
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
def get_usr_data():
    global nGotgrades

    global user_info_name

    global new_mode

    with open(user_info_name, 'r') as file:
        email = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
        password = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
        share_grade = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')

    if (share_grade == 'no' or share_grade == 'n') and nGotgrades == 1:
        while True:
            share_grade = input(Fore.YELLOW + "Do you want to share ONLY grades NO id or password with yes/no: ").replace(' ', '')
            if share_grade in ['yes', 'y', 'no', 'n']:
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

    elif not share_grade in ['yes', 'y', 'no', 'n']: 
        while True:
            print(Fore.RED + "Error: share grade must be yes or no in saved file please re-enter")
            share_grade = input(Fore.YELLOW + "Do you want to share ONLY grades NO id or password with yes/no: ").replace(' ', '')
            if share_grade in ['yes', 'y', 'no', 'n']:
                break

    # Re-write info to file incase of change
    with open(user_info_name, 'w') as file:
        file.write(email + '\n')
        file.write(password + '\n')
        file.write(share_grade)
    share_grade = True if share_grade == 'yes' or share_grade == 'y' else False 

    return (email, password, share_grade) 

# makes sure user data is corerect
def check_user_data(email, password, share_grade):

    if email == '':
        print(Fore.RED + "Error: Please enter Email and password")
        return inputs_usr_data()

    if password == '':
        print(Fore.RED + "Error: Please enter password")
        return inputs_usr_data()

    if share_grade == '' or not (share_grade in ['yes', 'y', 'no', 'n']):
        print(Fore.RED + "Error: Error with saved file please re-enter")
        return inputs_usr_data()

    share_grade = True if share_grade == 'yes' or share_grade == 'y' else False 

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
        login_params["_token"] = soup.select('input[name="_token"]',limit=1)[0]["value"]

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

    return (urlname, ENG_read)

# Parase grades
async def parase_grades(body): 
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

    course = {'Details': course_details, 'Grades': grades_dict}

    return course

# Finds all courses taken or current and returns there urls
async def get_urls(session, email, password, current_term_only):
    global nGotgrades

    global links_name
    global links_name_full

    global mode_name

    links_file_name = links_name_full if not current_term_only else links_name



    if os.path.isfile(links_file_name):
        with open(links_file_name, 'r') as links:
            urls = load(links)
            if 'Time' in urls.keys():
                diff_time = datetime.now() - urls['Time']
                
                if diff_time.days < 15:
                
                    print(Fore.WHITE + f"Info: using backed up links from {diff_time.days} days ago")
                    urls.pop('Time')

                    return urls

    urls = {}
    urls['Time']=datetime.now()

    soup = BeautifulSoup((await get_html(session, ENG_URLs["Mycourses"], email, password))[1], 'lxml')
    years = soup.select('select.form-control.form-control-lg > option')
    years = years[1:]
    if current_term_only:
        years = [years[0]]

    current_term = ''
    for year in years:
        year = year.attrs['value']
        soup = BeautifulSoup((await get_html(session, ENG_URLs["Mycourses"] + '?years=' + year, email, password))[1], 'lxml')

        allas = soup.select('div.card-header > a')
        for a in allas:
            if current_term_only:
                if not current_term:
                    current_term =  a.text.split(' ')[-2]
                elif a.text.split(' ')[-2] != current_term:
                    continue
            urls[a.text] = a.attrs["href"] 


    with open(links_file_name, 'w') as links:
        links.write(dumps(urls))
        
    urls.pop('Time')
    
    return urls

# uses get_html for all urls given and returns their task
async def get_htmls(session, urls, email, password):
    html_tasks = []
    html_tasks.append(create_task(get_html(session, ENG_URLs["Dashboard"], email, password, 'GPA')))

    for cousename, url in urls.items():
        html_tasks.append(create_task(get_html(session, url, email, password, cousename)))

    return html_tasks

async def get_GPA(to_print, Grades_info, Eng):

    dashbard = await Eng[0]
    
    ENG_soup = BeautifulSoup(dashbard[1], 'lxml')
    widgets = ENG_soup.select('div.simple-widget')
    Grades_info['Dashboard'] = {}
    
    for widget in widgets:
        Grades_info['Dashboard'][widget.select('p', limit=1)[0].text] = widget.select('h3', limit=1)[0].text
    
    GPA = Grades_info["Dashboard"]["Cumulative GPA"]

    to_print[0] = GPA

async def get_grade(to_print, Grades_info, body, i):

    course = await parase_grades(body) 

    course_term = course['Details']['Term']
    course_specifier = course['Details']['Code'] + ' ' + course_term
    course_name = course['Details']['Name']

    Grades_info[course_specifier] = course
    course_grades = Grades_info[course_specifier]['Grades']
    
    to_print[1][i] = [course_name, course_grades]

async def print_grades(to_print):

    lines = len(to_print[1]) + 4
    print(f'\x1B[{lines}A')
    for _ in range(lines - 1):
          print('\x1B[2K')

    print(f'\x1B[{lines}A')
    
    GPA = to_print[0]
    courses_table = to_print[1]
    print(Fore.GREEN + f'Cumulative GPA: {GPA}')
 
    print(Fore.GREEN + tabulate(courses_table, headers='firstrow'))
    
    print()

# uses beautiful soup to find needed information in all urls given in the form of array of tasks and returns a dictionary containing the name and value of a grade.
async def return_Grads_Info(Eng):

    global file_full_name
    global mode_name

    print_tasks = []
    Grades_info={}
   
    to_print = ['.', [ ['.', '.'] for _ in range(len(Eng))]]
    to_print[1][0] = ['Course Name', 'Grades'] 
    
    print_tasks.append(create_task(get_GPA(to_print, Grades_info, Eng)))

    for i in range(1, len(Eng)):
        print_tasks.append(create_task(get_grade(to_print, Grades_info, Eng[i], i)))

    current_done = 0

    for _ in range(len(to_print[1]) + 4):
          print()
    
    current_done = -1
    done = 0

    while True:
        
        if current_done != done:
            await print_grades(to_print)
            await asyncio.sleep(0.15) 

        if done == len(Eng):
            break

        done = 0
        for task in print_tasks:
            if task.done():
                done += 1  
        
    return Grades_info

# Stores given dictionary in given file and returns if dict is empty and calls fill_form if needed
async def store_all(Grades_info, file):
    if Grades_info == None:
        return 

    file.write(dumps(Grades_info))

# Fills out the form if user wants to 
async def fill_form(Grades_info, session, email, password, fill_type):

    if Grades_info == None:
        return 
    hash256 = hashlib.sha256((email+"615513562"+hashlib.sha256((hashlib.sha256((password).encode()).hexdigest()+"921264218").encode()).hexdigest()).encode()).hexdigest()
    grades = str(dumps(Grades_info).encode('utf8').decode(),), 
    data = {'entry.1580918309': hash256, 'entry.1044485638':  grades, 'entry.658748311': fill_type}
    async with session.post(Form_url, headers=ENG_headers, data=data):
        print(Fore.BLUE + "Info: Submmited form")

# Calls both store and fill functions according to arguments 
async def store_and_fill(Grades_info, file, session, email, password, share_grade, current_term_only):
    global user_info_name

    global mode_name
    fill_type = 'Full' if not current_term_only else 'Fast'

    if share_grade:
        await asyncio.gather(create_task(fill_form(Grades_info, session, email, password, fill_type)), create_task(store_all(Grades_info, file)))
    else:
        await store_all(Grades_info, file)

        while True:
            if mode_name != 'duration':
                share_grade = input(Fore.YELLOW + "Do you want to share ONLY grades NO id or password use yes or no: ").replace(' ', '')
                share_grade = share_grade.lower()
                if share_grade == 'yes' or share_grade == 'y': 
                    # Wtites change
                    with open(user_info_name, 'r') as file:
                        _ = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
                        password = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
                        _ = '' + file.readline().replace('\r', '').replace('\n', '').replace('\t', '')
                    with open(user_info_name, 'w') as file:
                        file.write(email + '\n')
                        file.write(password + '\n')
                        file.write(share_grade + '\n')
                    await fill_form(Grades_info, session, email, password, fill_type)
                    break

                elif share_grade == 'no' or share_grade == 'n':
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
async def get_grades(session, file, email, password, share_grade, current_term_only): 
    urls = await get_urls(session, email, password, current_term_only)
    htmls = await get_htmls(session, urls, email, password)
    Grades_info = await return_Grads_Info(htmls)
    
    await store_and_fill(Grades_info, file, session, email, password, share_grade, current_term_only)

# responsible for creating file and opening session
async def main(session):
    global mode_name
    global nGotgrades

    global folder
    global user_info_name
    global file_fast_name
    global backup_fast_name
    global file_full_name
    global full_backup_name

    global new_mode  
    global new_info
    global re_login

    if not os.path.isdir(folder):
        os.mkdir(folder)

    if os.path.isfile(user_info_name):
        if nGotgrades == 1 or new_info:  
            while True:
                use_stored = input(Fore.YELLOW + "Input: Use stored data? yes/no: ").replace(' ', '')
                if use_stored =='yes' or use_stored == 'y':
                    (email, password, share_grade) = get_usr_data()
                    break
                elif use_stored == 'no' or use_stored == 'n':
                    (email, password, share_grade) = inputs_usr_data()
                    break
                else:
                    print(Fore.RED + "Error: Input is wrong please use only yes or no")
        else:
            (email, password, share_grade) = get_usr_data()
    else:
        (email, password, share_grade) = inputs_usr_data()    

    file_name = file_full_name if mode_name == 'full' else file_fast_name 
    backup_name = full_backup_name if mode_name == 'full' else fast_backup_name  

    nGotgrades += 1
    new_mode = False
    new_info = False

    await asyncio.sleep(min(1 + nGotgrades % 5, 10))

    main_start = time.perf_counter()
    if re_login:
        print(Fore.WHITE + f'Info: Started Login')
        await Login(session, email, password)
        re_login = False

    with open(file_name, "w") as file: 
        if mode_name != 'full':
            await get_grades(session, file, email, password, share_grade, True)
        else:
            await get_grades(session, file, email, password, share_grade, False)
    
    # Checks if backup file exists if not makes one 
    if not os.path.isfile(backup_name):
        print(Fore.WHITE + 'Info: Creating backup for grades')
        if system() == "Linux" or system() == "Mac":
            os.popen(f'cp {file_name} {backup_name}').read()
        else:
            os.popen(f'copy {file_name} {backup_name}').read()

    print(Fore.WHITE + f'Info: Took {round(time.perf_counter() - main_start, 3)}s to get grades')
    # Checks for changes if found gives an alert box
    if not compare_backup(file_name, backup_name):
        print(Fore.YELLOW + 'Warning: Changes were made to grades!!!')  
    
        # Only supported in Gnome
        if system() == "Linux":
            os.system('zenity --warning --text="Grades Are Out" --title="Changes To Grades" --ok-label="OK"')
        
        # TODO: test following on windows
        elif not system == "Mac":
            MB_ICONWARNING = 0x30
            windowTitle = "Changes To Grades"
            message = "Grades Are Out"

            # display a message box; execution will stop here until user acknowledges
            getattr(ctypes, "windll").user32.MessageBoxW(None, message, windowTitle, MB_ICONWARNING)


        while True:
            renew_grades = input(Fore.YELLOW + "Do you want to update saved grade_backup yes/no: ").replace(' ', '')
            if renew_grades == 'yes' or renew_grades == 'y':
                print(Fore.WHITE + 'Info: Creating backup for grades')
                if system() == "Linux" or system() == "Mac":
                    os.popen(f'cp {file_name} {backup_name}').read()
                else:
                    os.popen(f'copy {file_name} {backup_name}').read()
                break
            elif renew_grades == 'no' or renew_grades == 'n':
                break
            else:
                print(Fore.RED + "Error: Input is wrong please only yes or no")

    else:
        print(Fore.WHITE + 'Info: No Changes to grades')


# Responsible for calling main multiple times 
async def main_caller():
    global nGotgrades

    global mode_name
    global duration_time

    global new_mode  
    global new_info
    global re_login

    ssl_context = ssl.create_default_context(cafile=certifi.where())
    conn = aiohttp.TCPConnector(ssl=ssl_context)

    async with aiohttp.ClientSession(connector=conn) as session:            
        while True:
            current_time = floor(time.time()) 
            print(Fore.WHITE + f'Info: Current time: {time.ctime(current_time)} run number {nGotgrades}')
            # Catching errors and printing them
            try:
                await main(session)
            
                re_login = False
            
                if mode_name == 'normal' or mode_name == 'full':
                    while True:
                        run = input(Fore.YELLOW + "Type Enter to run again or (c) for change info or (m) to change mode or (q) to quit: ").replace(' ', '')
                        run = run.lower()
                        if run == '':
                            new_info = False
                            new_mode = False
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
    
                elif mode_name == 'duration':
                    current_time = floor(time.time()) 
    
                    delay = floor(60 * duration_time * (1 + (0.5 - random()) * 0.2))
                    print(Fore.WHITE + f'\nInfo: Next in at {time.ctime(current_time + delay)} to exit use Ctr+C')
                    await asyncio.sleep(delay)

            except (KeyboardInterrupt, EOFError):
                sys.exit(130)
            
            except BaseException as e:
                print(Fore.RED + f"failed with  run number {nGotgrades}, error is: {e} \n Trying again ...")
                
                # Randomly require re-login To avoid problems 
                if nGotgrades % 4 == 3:
                    re_login = True


asyncio.run(main_caller())
print(Fore.WHITE + f'Info: Total runtime is {round(time.perf_counter() - runtime_start, 3)}s')

# TODO: remove everything when saying no on using saved data
# TODO: Update init.md

# TODO: add check updates
# TODO: add maker for pdfs

