import pandas as pd
from json import loads
import matplotlib.pyplot as plt
import asyncio
from asyncio import create_task, gather
from sys import exit
from multiprocessing import Process
from math import ceil
from matplotlib import style
import requests
import numpy as np
import time

GRADES = ['F', 'F*', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+']
GRADES_PF = ['F','P']
MINMUM_RECORDS = 20
plt.style.use('dark_background')

def grouping(duplicate_id):
    saved_columns = duplicate_id.columns
    duplicate_id_list = duplicate_id.values.tolist()

    # Base
    duplicate_id_list_final = duplicate_id_list[0]
    # remove base
    duplicate_id_list.pop(0)
    
    if len(duplicate_id_list) > 0:

        for list in duplicate_id_list:
            for index, data in enumerate(list):
                final_data = duplicate_id_list_final[index] 
                if data == data and data != final_data:
                    duplicate_id_list_final[index] = data
                    if final_data == final_data and index > 2:
                        print(f"Changed id: {duplicate_id_list_final[0]} index {index} data {final_data}, {duplicate_id_list_final[index]}")

    datafram_return = pd.DataFrame([duplicate_id_list_final])
    datafram_return.columns = saved_columns
    return datafram_return
def total_apply(grade, out_of):
    # Check for Nan
    if grade != grade:
        return grade
    new_grade = grade.split('(')[0]
    if out_of == 12:
        new_grade = GRADES.index(new_grade)
    else:
        new_grade = GRADES_PF.index(new_grade)
    return new_grade

def non_total_apply(grade, out_of):
    if grade != grade:
        return grade
    new_grade = int(grade.split('/')[0].replace('-', '0'))
    if out_of == 0:
        out_of = int(grade.split('/')[1])
    elif int(grade.split('/')[1]) != out_of:
        print(f"error should use out off {grade.split('/')[1]} not {out_of}")
    return new_grade


async def plot_column(column_name, column_data, out_of):
    global MINMUM_RECORDS

    column_data = column_data.dropna() 
   
    # only plot if abouve MINMUM_RECORDS limit 
    N_records = column_data.count()
    if N_records < MINMUM_RECORDS:
        plt.close(plot.figure)
        return
        

    # Adding 2 for each arange because one for 0 one for maximum 
    if 'GPA' in column_name:
        if '0.1' in column_name:
            bins = np.arange(0, out_of+ 0.2, 0.1)
        elif '1' in column_name:
            bins = np.arange(0, out_of+ 2, 1)
        elif 'full' in column_name:
            bins = np.arange(0, out_of + 0.02, 0.01)
        else:
            # Plots with diffrent percesion
            await plot_column('GPA full precision', column_data, out_of)
            await plot_column('GPA 0.1 precision', column_data, out_of)
            await plot_column('GPA 1 precision', column_data, out_of)
            return
    elif 'Need_to_pay' in column_name:
        return
    else:
        bins = np.arange(0, out_of + 2)
    plot = plt.figure().add_subplot(1, 1, 1)
    plot.hist(column_data, bins=bins, edgecolor='black')

    
    # Mean line
    plot.axvline(x=column_data.mean(), label='Mean')
    # Standard deviation
    # plot.axvline(x=column_data.mean() + column_data.std())
    # plot.axvline(x=column_data.mean() - column_data.std())
    
    plot.set_title(f"{column_name} ({column_data.count()})")
    if 'Total' in column_name:
        plot.set_xlabel('Grades')
    elif 'GPA' in column_name:
        plot.set_xlabel(f'GPA')
    else:
        plot.set_xlabel('Grades out of ' + str(out_of))

    plot.set_ylabel('No. of people')

    # Making sure integer for x or y accordingly
    plot.yaxis.get_major_locator().set_params(integer=True)
    if  'GPA 1' in column_name or  ('Total' not in column_name and 'GPA' not in column_name):
        plot.xaxis.get_major_locator().set_params(integer=True)

    if 'Total' in column_name:
        if out_of == 12:
            plot.set_xticks(range(13), GRADES)
        else:
            plot.set_xticks(range(2), GRADES_PF)

    plot.set_xlim(0)
    plot.set_ylim(0)
    
    plot.figure.savefig(f'./curves/{column_name.replace("/", "_")}.png', dpi=300)
    plt.close(plot.figure)
    # except:
        # print(f'error with {column_name}')
        # error.write(f'error with {column_name}\n')

async def plotting_range(start, end, final, columns, out_ofs):    
    tasks = []
    for col in columns[start:end]:
        tasks.append(create_task(plot_column(col, final[col], out_ofs[col])))
    await gather(*tasks)

def get_spreedsheet():
    grades = requests.get('https://docs.google.com/spreadsheets/d/e/2PACX-1vRhXWnxr_3DNyGz_s5w4kAqz0DkPotW_-Yb-On-SCa5MCd-9439iZ0CF5rNeHProAhpv-vMvrQ1jGhv/pub?gid=1467080841&single=true&output=tsv')
    assert grades.status_code == 200, 'Wrong status code'
    grades = grades.content
    grades_all = requests.get('https://docs.google.com/spreadsheets/d/e/2PACX-1vSwY2h1I7fFEAR9cEmjBQRSd8uIzuKsssP9nLQFerloECPzHrx0cGGriWy1toGF9hR9MpYfOTpR_Qpg/pub?gid=2047641198&single=true&output=tsv')
    assert grades_all.status_code == 200, 'Wrong status code'
    grades_all = grades_all.content
    with open('Grades.tsv', 'w') as grades_file:
        grades_file.write(grades.decode())
        grades_file.write('\n')
        grades_file.write('\n'.join(grades_all.decode().split('\n')[1:]))
    return

def create_final():
    counting = time.perf_counter()
    data = pd.read_csv('Grades.tsv', sep='\t')
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])
    data.sort_values(by='Timestamp', inplace = True)
    useful = data[['Tracking Id', 'Grades']]
    ds = useful.drop_duplicates()

    # Proccesing from form format to useful data
    all = ds.values.tolist()
    all_list = []

    for [a, b] in all:
        if b == b:
            b_dict = loads(b)
        else:
            b = ''
        b_dict_new = {}
        b_dict_new['id'] = a 
        for subject, grades in b_dict.items():
            
            # If forwarded to student fees removes extra \n
            if subject == 'https://eng.asu.edu.eg/public/payments/student_fees':
                subject = 'Need_to_pay_fees'
                for grade_name , grade in grades.items():
                    b_dict_new[grade_name + ' ' + subject] = grade.replace('\n', '')
                    # To support old form where Fall and spring wasn't accounted for
                    b_dict_new[grade_name + ' ' + subject.split(' ')[0]] = grade.replace('\n', '')

            # check if a subject
            elif isinstance(grades, dict):
                for grade_name , grade in grades.items():
                    b_dict_new[grade_name + ' ' + subject] = grade
                    b_dict_new[grade_name + ' ' + subject.split(' ')[0]] = grade
                # If empty just continue
                if len(grades) == 0:
                    continue

                    
            else:
                if subject == 'GPA':
                    b_dict_new['GPA'] = float(grades)
                else:
                    print('Somthing weired happened')
                    b_dict_new[subject] = grades

        all_list.append(b_dict_new)

    need_grouping = pd.DataFrame(all_list)
    final = need_grouping.groupby('id', as_index=False).apply(grouping).reset_index(drop=True)
    # print(final.loc[final['GPA 0.1 precision'] == 3.0])

 
    # Useful when need to check non nan for certain user 
    # index = final.loc[final['id'] == '1bbc9a7cdb233aedccd4020729a3d591'].index.values.astype(int)[0]
    # help = final[final.columns[(final.iloc[index] == final.iloc[index])]]
    # print(help.loc[help['id'] == '1bbc9a7cdb233aedccd4020729a3d591'])
    # print(final.loc[final['id'] == '82880ce39eb8e961af0f5df5638c946d'])


    with open('Grades.txt', 'w') as grades_columns:
        columns = final.columns.to_list()
        for col in columns:
            grades_columns.write(col + '\n')
    out_ofs = {}
    # Formatting all and skipping id, is first 1:
    for column_name in columns[1:]:
        if 'Total' in column_name:
            if 'P' in final[column_name].to_list():
                out_ofs[column_name] = 1
            else:
                out_ofs[column_name] = 12
            
            final[column_name] = final[column_name].apply(total_apply, args=(out_ofs[column_name],))

        elif 'GPA' in column_name:
            out_ofs[column_name] = 4
        elif 'Need_to_pay_fees' in column_name:
            out_ofs[column_name] = len(final[column_name])
            # TODO: needs fixing
            pass
        else:     
            out_ofs[column_name] = int(final[column_name].loc[final[column_name].first_valid_index()].split('/')[1])
            final[column_name] = final[column_name].apply(non_total_apply, args=(out_ofs[column_name],))

    print(f'Grouping / formating {str(round(time.perf_counter() - counting, 3))} {time.ctime()} \t')
    return (final, columns, out_ofs)

def run_asyn_plot_range(start, end, final, columns, out_ofs):
    if end > len(columns):
        end = len(columns)
    asyncio.run(plotting_range(start, end, final, columns, out_ofs))


# Takes number of cores and split them on each
def plot_all(N_CORES, final, columns, out_ofs): 
    segment = ceil(len(columns) / N_CORES)
    process = []
    for i in range(N_CORES):
        # Note skips first beacase is id
        process.append(Process(target=run_asyn_plot_range, args=(segment * i + 1, segment * (i +1), final, columns, out_ofs)))

    for i in range(N_CORES):
        process[i].start()

    for i in range(N_CORES):
        process[i].join()



if __name__ == '__main__':
    times = open('time.txt', 'a')
    # ! use to get new data don't delete
    # get_spreedsheet()
    counting = time.perf_counter()
    (final, columns, out_ofs) = create_final()
    print(f'getting final {str(round(time.perf_counter() - counting, 3))} {time.ctime()}s \t')
    
    # columns = columns[:10]
    counting = time.perf_counter()    
    # run_asyn_plot_range(1, 20, final, columns, out_ofs)
    column = 'Freshman GPA 1 precision'
    Freshman = final.loc[final['Total PHM013s'] == final['Total PHM013s']]
    out_of = 4
    asyncio.run(plot_column(column, Freshman['GPA'], out_of))
    # column = 'Total ASU101s'
    # asyncio.run(plot_column(column, final[column], out_ofs[column]))
    # plot_all(6, final, columns, out_ofs)
       
    times.write(f'run Program in {round(time.perf_counter() - counting, 3)}s \n')

# TODO fix Need_to_pay_fees graphs

# TODO: better style
# TODO: add mulitple graph on same plot

# TODO remove all try expt
# TODO add density to histogram opteion to gt precentage of each
# TODO fix mean calulating in Total
# TODO make histogram axis better and centered try bar graph









 # ! deprecated
# plotting = pd.DataFrame(final[column_name].value_counts())
# # print(final[column_name])

# plotting = plotting.reset_index(level=[column_name])

# # check if column is empty 
# if len(plotting) == 0 or len(plotting[column_name]) == 0:
#     print(f'column {column_name} is empty')
#     return
# # editing data
# # print(len(plotting))
# try:
#     if 'Total' in column_name:
#         plotting[column_name] = plotting[column_name].apply(total_apply)
        
#     elif 'GPA' not in column_name:
#         out_of = int(plotting[column_name][0].split('/')[1])
#         plotting[column_name] = plotting[column_name].apply(non_total_apply, args=(out_of,))
# except KeyboardInterrupt:
#     exit()
# except:
#     # _TODO: fix
#     print(f'error with {column_name}')
    
# max_count = plotting['count'].max()

# if plotting['count'].sum() == 1:
#     return
# plotting.columns = [column_name, 'count']

# # filling empty and sorting
# if 'Total' in column_name:
#     (plotting, pass_fail) = total_fill(plotting, column_name)
#     plotting = plotting.sort_values(by='sort')
# elif 'GPA' in column_name:
#     plotting = gpa_fill_all(plotting, column_name)
#     plotting = plotting.sort_values(by=column_name)
# else:
#     plotting = not_total_fill(plotting, column_name, out_of)
#     plotting = plotting.sort_values(by=column_name)
# plot = plotting.hist(x=column_name, y='count')
# plot = plotting[column_name].hist(bins=bins, weights=plotting['count'])
# ! end of deprecated

# ! deprecated
# elif 'GPA' in column_name:
#     plot.set_xticks(range(5))
# else:
#     steps = 0
#     out_of_tmp = out_of
#     out_of_tmp //= 20
#     steps = out_of_tmp if out_of_tmp != 0 else 1
#     plot.set_xticks(range(0, out_of + 1, steps))

# # make sure not to crowded y axis
# steps = 0
# max_count_tmp = max_count
# max_count_tmp //= 15
# steps = max_count_tmp if max_count_tmp != 0 else 1
# plot.set_yticks(range(0, max_count + 1, steps))
# ! end of deprecated

# ! deprecated
# def total_fill(plotting, column_name):
#     global GRADES
#     global GRADES_PF

#     sort = []
#     col = plotting[column_name].tolist()
#     if 'P' not in col:
#         for i in GRADES:
#             if i not in col:
#                 plotting.loc[len(plotting.index)] = [i, 0]
#         for grad in plotting[column_name].tolist():
#             sort.append(GRADES.index(grad))
#         pass_fail = False
#     else:
#         for i in GRADES_PF:
#             if i not in col:
#                 plotting.loc[len(plotting.index)] = [i, 0]
#         for grad in plotting[column_name].tolist():
#             sort.append(GRADES_PF.index(grad))
#         pass_fail = True
#     plotting['sort'] = sort
#     return (plotting, pass_fail)


# def gpa_fill_all(plotting, column_name):
#     col = plotting[column_name].tolist()
#     if '1' in column_name:
#         steps = 1
#     elif '2' in column_name:
#         steps = 10
#     else:
#         steps = 100 
#     for i in range(4*steps + 1):
#         if i / steps not in col:
#             plotting.loc[len(plotting.index)] = [i / steps, 0]
#     return plotting

# def not_total_fill(plotting, column_name, out_of):
  
#     col = plotting[column_name].tolist()
#     for i in range(out_of + 1):
#         if i not in col:
#             plotting.loc[len(plotting.index)] = [i, 0]
#     return plotting
# ! end of deprecated