import requests
from base64 import b64encode
import os
import urllib.parse

class RommAPIHelper:
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url        
    
    def login(self, username, password):
        url = self.api_base_url + '/token'
        
        auth_string = f"{username}:{password}"
        self.auth_encoded = b64encode(auth_string.encode()).decode()              

    # Heartbeat
    def getRommHeartbeat(self):
        # Prepare URL
        url = self.api_base_url + '/heartbeat'

        # Prepare Headers
        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {self.auth_encoded}"
        }

        # Do HTTP GET Request
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print("Fehler:", response.status_code, response.text)
    
    
    def getCollections(self):

        # Prepare URL
        url = self.api_base_url + '/collections/'

        # Prepare Headers
        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {self.auth_encoded}"
        }              

        # Do HTTP GET Request
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            # print(response.text)
            return response.json()
        else:
            print("Fehler:", response.status_code, response.text) 

    def getCollectionByID(self, collectionID):

        # Prepare URL
        url = self.api_base_url + '/collections/' + str(collectionID)

        # Prepare Headers
        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {self.auth_encoded}"
        }              

        # Do HTTP GET Request
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            # print(response.text)
            return response.json()
        else:
            print("Fehler:", response.status_code, response.text)  

    
    def getPlatforms(self):
        # Prepare URL
        url = self.api_base_url + '/platforms/'

        # Prepare Headers
        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {self.auth_encoded}"
        }  

        # Do HTTP GET Request
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            # print(response.text)
            return response.json()
        else:
            print("Fehler:", response.status_code, response.text)
    
    def getRomByID(self, romID):
        # Prepare URL
        url = self.api_base_url + '/roms/' + str(romID)

        # Prepare Headers
        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {self.auth_encoded}"
        }  

        # Do HTTP GET Request
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            # print(response.text)
            return response.json()
        else:
            print("Fehler:", response.status_code, response.text)         

    def downloadRom(self, romID, romFilename, download_path):
        # Prepare URL
        url = self.api_base_url + '/roms/' + str(romID) + '/content/' + str(romFilename)

        # Prepare Headers
        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {self.auth_encoded}"
        }  

        # Do HTTP GET Request
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            # Get Filename from HTTP-Request Response
            content_disposition = response.headers.get("content-disposition")
            if content_disposition and "filename=" in content_disposition:
                filename = content_disposition.split("filename=")[1].strip('"')
                filename = urllib.parse.unquote(filename)  # Dekodiert %20 zu Leerzeichen
            else:
                filename = romFilename

            # make sure the Download Folder exists | If not, create it
            os.makedirs(download_path, exist_ok=True)

            # build file-path
            file_path = os.path.join(download_path, filename)

            # Check if File exists
            if os.path.exists(file_path):
                print(f"⚠️ File already exists: {file_path} – Download übersprungen.")
            else:
                # Download File in Chunks and save it
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
        else:
            # Something wrong
            print("Error:", response.status_code, response.text) 
