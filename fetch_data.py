import os
import io
import json
import requests
from tqdm import tqdm
from netCDF4 import Dataset
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

save_downloaded = False
file_data = []

def get_all_hrefs(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')
    hrefs = [a.get('href') for a in soup.find_all('a', href=True)]
    return hrefs

def download_file(url):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check for download errors
        return response
    except requests.exceptions.RequestException as e:
            print(f"Failed to download {url}: {e}")

def remove_junk(values):
    result = []
    for item in values:
        if '?C' not in item and item!='/gridclim/':
            result.append(item)
    return result

def get_netCdf_Data(file_content):
    item_data = {}
    data_stream = io.BytesIO(file_content)
    # Use netCDF4 to read the dataset directly from the in-memory binary stream
    dataset = Dataset('in_memory', mode='r', memory=data_stream.read())
    # Example: Print all variables in the dataset
    variable = dataset.variables
    keys = variable.keys()
    print("Keys : ",keys)
    for key in keys:
        value = variable[key]
        if isinstance(value, dict):
            item_data[key] = {}
            for i in value.keys():
                item_data[key][i] = value[i]
        else:
            item_data[key] = variable[key]
    file_data.append(item_data)

def download_file_structure(base_url, download_path):
    # List of files to download (Replace with an actual list of file URLs or logic to scrape them)
    file_urls = [
        urljoin(base_url, 'hurs/'),
        urljoin(base_url, 'pr/'),
        urljoin(base_url, 'snd/'),
        urljoin(base_url, 'tas/'),
        urljoin(base_url, 'tasmax/'),
        urljoin(base_url, 'tasmin/')
    ]

    # Loop through each file URL and download it
    for file_url in file_urls:
        # Parse file path to maintain directory structure
        file_path = urlparse(file_url).path
        # local_path = os.path.join(download_path, file_path)
        local_path = os.path.join('D:\Downloads\Datasets', file_path)
        
        print("Local Path : ",local_path)
        # print("File Path : ",file_path)

        # Ensure the directory structure exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        # Download the file
        item_urls = []
        try:
            response = download_file(file_url)
            item_urls = get_all_hrefs(response.content)[5::-1]
            item_urls = remove_junk(item_urls)

            for item in tqdm(item_urls, desc='Item Download Progress ('+file_url+')'):
            # for item in item_urls:
                if '?C' not in item:
                    item_url = file_url+str(item)
                    item_path = os.path.join(local_path,str(item))
                    # print("Save Path : ",item_path)
                    item_file = download_file(item_url)
                    if save_downloaded:
                        with open(item_path, 'wb') as f:
                            for chunk in tqdm(item_file.iter_content(chunk_size=8192), desc='Item Write Progress ('+item+')'):
                                f.write(chunk)
                    else:
                        get_netCdf_Data(item_file.content)

            print_val = type(file_data[0].values())
            print("\nGathered Data (",len(file_data),"): ",print_val,'\n')
            
            # print(f"Downloaded: {file_url} -> {local_path}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {file_url}: {e}")
        print("Item List (", len(item_urls),') : ',item_urls[0])

# Example usage:
base_url = "https://opendata-download-metanalys.smhi.se/gridclim/"
download_path = "./weather_data/"
download_file_structure(base_url, download_path)
