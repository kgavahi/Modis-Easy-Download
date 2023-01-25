"""
Created on Sun Jan 26 17:00:27 2020

@author: kayhangavahi@gmail.com
"""

import datetime
import time
import urllib
import os
import shutil
import requests
from pyhdf.SD import SD, SDC
#from netCDF4 import Dataset

def readCredentials(file):
    with open(file) as f:
        lines = f.readlines()
    return lines
def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))
def read_webpage(filex):
    while True:
        try:
            with urllib.request.urlopen(filex) as f:
                r = f.read().decode('utf-8')
            break
        except:
            print("Connection refused by the server..")
            print("Let me sleep for 5 seconds")
            print("ZZzzzz...")
            time.sleep(10)
            print("Was a nice sleep, now let me continue...")
    return r
def DownloadList_MODIS(username, password, date_start, date_end, earthData_name, earthData_version):

    # Convert dates to datetime objects
    date_start = datetime.datetime.strptime(date_start, '%Y-%m-%d').date()
    date_end = datetime.datetime.strptime(date_end, '%Y-%m-%d').date()

    
    
    sattelite_mapping = {
        'MCD': 'MOTA',
        'MYD': 'MOLA',
        'MOD': 'MOLT'
    }

    sattelite = sattelite_mapping.get(earthData_name[:3], 'unknown')
        
    filex = f"https://e4ftl01.cr.usgs.gov/{sattelite}/{earthData_name}.{earthData_version}/"
    page = read_webpage(filex)
    
       
    lines = page.split('\n')
    matches = [s for s in lines if "folder.gif" in s]
    date_strings = [s[s.find('href="') + 6: s.find('href="') + 6 + 4 + 2 + 2 + 2] for s in matches]
    dateList = [datetime.datetime.strptime(s, '%Y.%m.%d').date() for s in date_strings]
    


    # Only select available dates for the dataset
    first_date = nearest(dateList, date_start)
    last_date  = nearest(dateList, date_end)
      
    dateList_to_download = [date for date in dateList if first_date <= date <= last_date]

    
    # 14 tiles that cover the CONUS
    conus_tiles = ["h08v04","h08v05","h08v06",
                    "h09v04","h09v05","h09v06",
                     "h10v04","h10v05","h10v06",
                     "h11v04","h11v05","h12v04",
                     "h12v05","h13v04"]    

    count=0
    for date in dateList_to_download:           
        date_str = date.strftime("%Y.%m.%d")
        filex = f"https://e4ftl01.cr.usgs.gov/{sattelite}/{earthData_name}.{earthData_version}/{date_str}/"
        page = read_webpage(filex)
        page_lines = page.split('\n')
        hdf_files  = [line for line in page_lines if "hdf" in line]
        
        conus_files = [s for s in hdf_files if \
                any(substring in s for substring in conus_tiles)]

        if not conus_files:
            print(f'NO DATA AVAILABLE for {date}')
            count += 1
            continue

        start_ind = conus_files[0].find(earthData_name)
        end_ind   = conus_files[0].find('.hdf') + 4
        mylist = [filex + i[start_ind:end_ind] for i in conus_files]
        URLs = list(set(mylist))
           
        download(username , password , date_start , date_end , earthData_name,URLs)
        print('    ',str((count+1)/len(dateList_to_download)*100)[:5] + ' % Completed')
        count+=1

def download(username , password , date_start , date_end , earthData_name,fileList):
    if not os.path.exists('./'+earthData_name):
        os.mkdir('./'+earthData_name)
    saveDir = './' +  earthData_name # Set local directory to download to
    
    
    pathNetrc = os.path.join(os.path.expanduser("~"),'.netrc')
    if os.path.exists(pathNetrc):
        os.remove(pathNetrc)
        
    netrcFile = ['machine urs.earthdata.nasa.gov','login ' + username,'password '+password]
    with open('.netrc', 'w') as f:
        for item in netrcFile:
            f.write("%s\n" % item)
        
    shutil.copy('.netrc',os.path.expanduser("~"))
    
    
    
    #fileList = DownloadList(date_start , date_end,earthData_name)
    fileList = sorted(fileList)
    #for i in fileList:
    #    print(i)
    

    # -----------------------------------------DOWNLOAD FILE(S)-------------------------------------- #
    # Loop through and download all files to the directory specified above, and keeping same filenames
    count = 0
    for f in fileList:
        #print('    ',str((count+1)/len(fileList)*100)[:5] + ' % Completed')
        date_of_file = f.split('/')[5].replace('.','-')
        path = os.path.join(saveDir,date_of_file)
        if not os.path.exists(path):
            os.mkdir(path)
        saveName = os.path.join(path, f.split('/')[-1].strip())
        if os.path.exists(saveName):
            try:
                if not earthData_name=='IMERG':
                    f = SD( saveName , SDC.READ)
                    f.end()
                else:
                    f = Dataset( saveName , 'r')
                    f.close()
                count += 1
                continue
            except:
                print('Damgeged file encountered, redownloading...')
    # Create and submit request and download file
        file_downloaded = 0
        while file_downloaded == 0:
            try:
                with requests.get(f.strip(), stream=True) as response:
                    if response.status_code != 200:
                        print("Verify that your username and password are correct")
                    else:
                        response.raw.decode_content = True
                        content = response.raw
                        with open(saveName, 'wb') as d:
                            while True:
                                chunk = content.read(16 * 1024)
                                if not chunk:
                                    break
                                d.write(chunk)
                        print('Downloaded file: {}'.format(saveName))
                        file_downloaded = 1
            except:
                print("Connection refused by the server..")
                print("Let me sleep for 5 seconds")
                print("ZZzzzz...")
                time.sleep(10)
                print("Was a nice sleep, now let me continue...")
                continue
        count += 1
        
        
def main():
    
    
    cred = readCredentials('credentials.txt')
    username   = cred[0]
    password   = cred[1]
    start_date = '2018-01-01'
    end_date   = '2018-01-01'
    product    = 'MCD12Q1'
    version    = '006'

    
    
       
    DownloadList_MODIS(username , password ,start_date , end_date , product, version)
    

if __name__ == '__main__':

    main()