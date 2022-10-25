""" This module allows you to download public files from Google Drive and Dropbox """ 
import os
import requests
import zipfile
import patoolib
from bs4 import BeautifulSoup
import gdrivedl

# Define urls to filter by cloud service
GDRIVE_URL = 'drive.google.com'
DROPBOX_URL = 'dropbox.com'

def download_folder(url, output_folder, filename=None):
    """Download Google Drive folders"""
    dl = gdrivedl.GDriveDL(quiet=True, overwrite=False, mtimes=False)
    dl.process_url(url, output_folder, filename=None)
    
def download_file(url, output_folder, filename):
    """ Download Google Drive files"""
    dl = gdrivedl.GDriveDL(quiet=True, overwrite=False, mtimes=False)
    dl.process_url(url, output_folder, filename)

def gd_download(url, directory):
    """ Detects if url belongs to Google Drive folder or file and calls relavent function"""
    if 'folder' in url:
        output = get_title(url)[:-15]
        output_path = directory + output
        #print("---> Downloading to: " + output_path)
        download_folder(url, output_path)
    elif 'file' in url:
        temp_output = get_title(url)[:-15]
        output = temp_output.split('.', 1)[0]
        #print("---> Downloading to: " + directory + temp_output)
        download_file(url, directory, temp_output)
        unzip(temp_output, output, directory)
    else: 
        print('The url: '+ url + ' is not supported, sorry.')
        return False

def get_title(url):
    """Gets file/folder title with requests library"""
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for title in soup.find_all('title'):
        return title.get_text()
    
def compression_type(file_name):
    """ Detects file compression type"""
    ext = os.path.splitext(file_name)[-1].lower()
    # print(ext)
    return ext

def unzip(zipped_file, unzipped_file, directory):
    """Uncompresses files and then deletes compressed folder"""
    if compression_type(zipped_file) == '.zip':
        zip_path = directory + zipped_file
        unzip_path = directory + unzipped_file
        #print('--> Extracting to: ' + unzip_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(unzip_path)
                zip_ref.close()
        os.remove(zip_path)
    if compression_type(zipped_file) == '.rar':
        zip_path = directory + zipped_file
        unzip_path = directory + unzipped_file
        #print('---> Extracting to: ' + unzip_path)
        patoolib.extract_archive(zip_path, outdir=directory)
        os.remove(zip_path)
    return

def db_download(url, directory):
    """ Downloads files from Dropbox url"""
    url = url[:-1] + '0'
    file_name = get_title(url)[:-21][10:]
    #print(file_name)
    suffix1 = file_name.endswith(".zip")
    suffix2 = file_name.endswith(".rar")
    dl_url = url[:-1] + '1'
    filepath = directory + file_name
    #print("---> Downloading to: " + filepath)
    output = file_name[:-4]
    headers = {'user-agent': 'Wget/1.16 (linux-gnu)'}
    r = requests.get(dl_url, stream=True, headers=headers)
    with open(filepath, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk:
                f.write(chunk)
    if suffix1 or suffix2:
        unzip(file_name, output, directory)

def grab(url, output_path):
    """ Detects if url belongs to Google Drive or a Dropbox url and calls the relavent function"""
    if GDRIVE_URL in url:
        gd_download(url, output_path)
    if DROPBOX_URL in url:
        db_download(url, output_path)
        return True
    else: 
        return False
