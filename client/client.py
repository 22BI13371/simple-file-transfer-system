import requests

paths = ["client/a.txt", "client/b.txt", "client/c.txt"]
url = 'http://127.0.0.1:5000'

def upload():
    files = []
    for path in paths:
        with open(path, 'rb') as file:
            files = [('files', file)]
            response = requests.post(url + "/upload", files=files)
            print(response.json())
        
if __name__ == "__main__":
    upload()