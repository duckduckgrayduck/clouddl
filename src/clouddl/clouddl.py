""" This module allows you to download public files from Google Drive and Dropbox """
import os
import requests
import zipfile
import logging
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
    """ Detects if url belongs to Google Drive folder or file and calls relavent function """
    if 'folder' in url:
        output = get_title(url)[:-15]
        output_path = directory + output
        logging.info(f"---> Downloading Google Drive folder to: {output_path}")
        download_folder(url, output_path)
        return True
    elif 'file' in url:
        temp_output = get_title(url)[:-15]
        output = temp_output.split('.', 1)[0]
        logging.info(f"---> Downloading Google Drive file to {directory + temp_output}")
        download_file(url, directory, temp_output)
        unzip(temp_output, output, directory)
        return True
    else:
        return False

def get_title(url):
    """ Gets file/folder title with requests library """
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for title in soup.find_all('title'):
        return title.get_text()

def compression_type(file_name):
    """ Detects file compression type """
    ext = os.path.splitext(file_name)[-1].lower()
    return ext

def unzip(zipped_file, unzipped_file, directory):
    """ Uncompresses files and then deletes compressed folder """
    if compression_type(zipped_file) == '.zip':
        zip_path = directory + zipped_file
        unzip_path = directory + unzipped_file
        logging.info(f"--> Extracting to: {unzip_path}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(unzip_path)
                zip_ref.close()
        os.remove(zip_path)
    if compression_type(zipped_file) == '.rar':
        zip_path = directory + zipped_file
        unzip_path = directory + unzipped_file
        logging.info(f"---> Extracting to: {unzip_path}")
        patoolib.extract_archive(zip_path, outdir=directory)
        os.remove(zip_path)
    return

def db_download(url, directory):
    """ Downloads files from Dropbox URL """
    url = url[:-1] + '0'
    file_name = get_title(url)[:-21][10:]
    logging.info(f"Dropbox file name: {file_name}")
    suffix1 = file_name.endswith(".zip")
    suffix2 = file_name.endswith(".rar")
    dl_url = url[:-1] + '1'
    filepath = directory + file_name
    logging.info(f"Downloading dropbox file to: {filepath}")
    output = file_name[:-4]
    headers = {'user-agent': 'Wget/1.16 (linux-gnu)'}
    r = requests.get(dl_url, stream=True, headers=headers)
    if r.status_code == 200:
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        if suffix1 or suffix2:
            unzip(file_name, output, directory)
        return True
    else:
        return False
        
    
def grab(url, output_path):
    """
        Detects if url belongs to Google Drive or a Dropbox url and calls the relevant method. 
        You may change logging level by changing ERROR to WARNING, INFO, or DEBUG(all logs).
    """
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.ERROR)
    if GDRIVE_URL in url:
        if (gd_download(url, output_path)):
            return True
        else:
            logging.warning(f"The Google Drive URL {url} is not supported")
            return False
    if DROPBOX_URL in url:
        if(db_download(url, output_path)):
            return True
        else:
            logging.warning(f"The Dropbox URL {url} is not supported")
            return False
    else:
        logging.warning(f"The URL {url} is not supported")
        return False
