import requests
import zipfile
import os

apikey = raw_input('API Key: ')
HEADERS = {"X-API-Key": apikey}

r = requests.get("http://www.bungie.net/Platform/Destiny/Manifest/", headers=HEADERS);
manifest = r.json()

mani_url = 'http://www.bungie.net'+manifest['Response']['mobileWorldContentPaths']['en']

#Download the file, write it to 'MANZIP'
r = requests.get(mani_url)
with open("MANZIP", "wb") as zip:
    zip.write(r.content)
print "Download Complete!"

#Extract the file contents, and rename the extracted file
# to 'Manifest.content'
with zipfile.ZipFile('MANZIP') as zip:
    name = zip.namelist()
    zip.extractall()
os.rename(name[0], 'Manifest.content')
print 'Done!'
