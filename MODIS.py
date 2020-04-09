# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 17:00:27 2020

@author: 16785
"""

import datetime
import time
import urllib
import os
import shutil
import requests
from pyhdf.SD import SD, SDC
from netCDF4 import Dataset

def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))
def DownloadList_MODIS(username , password ,date_start , date_end , earthData_name):



	dateList = []
	dateList_to_download = []

	year, month, day = map(int, date_start.split('-'))
	date_start = datetime.date(year, month, day)  # start date

	year, month, day = map(int, date_end.split('-'))
	date_end = datetime.date(year, month, day)  # end date



	earthData_version = '006'
	if earthData_name[:3]=='MCD':
		sattelite = 'MOTA'
	elif earthData_name[:3]=='MYD':
		sattelite = 'MOLA'
	elif earthData_name[:3]=='MOD':
		sattelite = 'MOLT'   

	filex = 'https://e4ftl01.cr.usgs.gov/'+sattelite+'/'+ earthData_name +'.'+ earthData_version +'/'
	print(filex)
	file_downloaded = 0
	while file_downloaded == 0:
		try:
			with urllib.request.urlopen(filex) as f:
				r = f.read().decode('utf-8')
			file_downloaded = 1
		except:

			print("Connection refused by the server..")
			print("Let me sleep for 5 seconds")
			print("ZZzzzz...")
			time.sleep(10)
			print("Was a nice sleep, now let me continue...")
			continue
				
	KK = r.split('\n')
	match    = [s for s in KK if "folder.gif" in s]
	start_ind = match[0].find('href="') + 6
	end_ind   = start_ind + 4 + 2 + 2 + 2 
	for i in match:
		i = i[start_ind:end_ind]
		year, month, day = map(int, i.split('.'))
		d = datetime.date(year, month, day)
		dateList.append(d)

	first_date = nearest(dateList, date_start)

	last_date  = nearest(dateList, date_end)
	
	k = dateList.index(first_date)
	#print(dateList)
	while first_date + (dateList[k]-first_date) <= last_date:
		dateList_to_download.append(dateList[k])
		k += 1
		if k==len(dateList):
			break



	count=0
	for date in dateList_to_download:
		mylist = []		
		
		filex = 'https://e4ftl01.cr.usgs.gov/'+sattelite+'/'+ earthData_name +'.'+ earthData_version +'/' + str(date).replace('-','.') + '/'
			
			
			#
		file_downloaded = 0
		while file_downloaded == 0:
			try:
				with urllib.request.urlopen(filex) as f:
					r = f.read().decode('utf-8')
				file_downloaded = 1
			except:

				print("Connection refused by the server..")
				print("Let me sleep for 5 seconds")
				print("ZZzzzz...")
				time.sleep(10)
				print("Was a nice sleep, now let me continue...")
				continue
		#

		KK = r.split('\n')
		match    = [s for s in KK if "hdf" in s]

		matching = [s for s in match if "h08v04" in s]
		matching.extend([s for s in match if "h08v05" in s])
		matching.extend([s for s in match if "h08v06" in s])
		matching.extend([s for s in match if "h09v04" in s])
		matching.extend([s for s in match if "h09v05" in s])
		matching.extend([s for s in match if "h09v06" in s])
		matching.extend([s for s in match if "h10v04" in s])
		matching.extend([s for s in match if "h10v05" in s])
		matching.extend([s for s in match if "h10v06" in s])
		matching.extend([s for s in match if "h11v04" in s])
		matching.extend([s for s in match if "h11v05" in s])
		matching.extend([s for s in match if "h12v04" in s])
		matching.extend([s for s in match if "h12v05" in s])
		matching.extend([s for s in match if "h13v04" in s])

		if matching==[]:
			print('NO DATA AVAILABLE for %s'%date)
			count+=1
			continue
		
		start_ind = matching[0].find(earthData_name)
		end_ind   = matching[0].find('.hdf') + 4


		for i in matching:
			mylist.append(filex + i[start_ind:end_ind])
		URLs = list(set(mylist))
		download(username , password , date_start , date_end , earthData_name,URLs)
		print('    ',str((count+1)/len(dateList_to_download)*100)[:5] + ' % Completed')
		count+=1
	#return URLs
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
	#	print(i)
	

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
def dl_MODIS(username , password , date_start , date_end , earthData_name):
    DownloadList_MODIS(username , password ,date_start , date_end , earthData_name)
    #download(username , password , date_start , date_end , earthData_name,fileList)
    