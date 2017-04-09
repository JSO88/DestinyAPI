import requests
import json
import sqlite3
import os
import sys
import time

apikey = raw_input('API Key: ')
HEADERS = {"X-API-Key": apikey}

user=raw_input('User name: ')

r = requests.get("http://www.bungie.net/Platform/Destiny/SearchDestinyPlayer/2/"+user+"/", headers=HEADERS);
membership = r.json()
membershipId=membership['Response'][0]['membershipId']
displayName=membership['Response'][0]['displayName']
membershipType=str(membership['Response'][0]['membershipType'])

r = requests.get("http://www.bungie.net/Platform/Destiny/"+membershipType+"/Account/"+membershipId+"/Summary/", headers=HEADERS);
summary = r.json()

character=int(raw_input('Character (0,1,2): '))

grimoireScore=summary['Response']['data']['grimoireScore']
baseCharacterLevel=summary['Response']['data']['characters'][character]['baseCharacterLevel']
characterId=summary['Response']['data']['characters'][character]['characterBase']['characterId']
light=summary['Response']['data']['characters'][character]['characterBase']['stats']['STAT_LIGHT']['value']
intellect=summary['Response']['data']['characters'][character]['characterBase']['stats']['STAT_INTELLECT']['value']
discipline=summary['Response']['data']['characters'][character]['characterBase']['stats']['STAT_DISCIPLINE']['value']
strength=summary['Response']['data']['characters'][character]['characterBase']['stats']['STAT_STRENGTH']['value']
armor=summary['Response']['data']['characters'][character]['characterBase']['stats']['STAT_ARMOR']['value']
agility=summary['Response']['data']['characters'][character]['characterBase']['stats']['STAT_AGILITY']['value']
recovery=summary['Response']['data']['characters'][character]['characterBase']['stats']['STAT_RECOVERY']['value']
optics=summary['Response']['data']['characters'][character]['characterBase']['stats']['STAT_OPTICS']['value']
defense=summary['Response']['data']['characters'][character]['characterBase']['stats']['STAT_DEFENSE']['value']
classHash=summary['Response']['data']['characters'][character]['characterBase']['classHash']
subclassHash=summary['Response']['data']['characters'][character]['characterBase']['peerView']['equipment'][0]['itemHash']
genderHash=summary['Response']['data']['characters'][character]['characterBase']['genderHash']
genderType=summary['Response']['data']['characters'][character]['characterBase']['genderType']
powerLevel=summary['Response']['data']['characters'][character]['characterBase']['powerLevel']
minutesPlayedTotal=summary['Response']['data']['characters'][character]['characterBase']['minutesPlayedTotal']
dateLastPlayed=summary['Response']['data']['characters'][character]['characterBase']['dateLastPlayed']

r = requests.get("http://www.bungie.net/Platform/Destiny/"+membershipType+"/Account/"+membershipId+"/Character/"+characterId+"/Inventory/Summary/", headers=HEADERS);
char_inv = r.json()

hash_dict = {'DestinyInventoryItemDefinition': 'itemHash'}
def build_dict(hash_dict):
    #connect to the manifest
    con = sqlite3.connect('Manifest.content')
    print 'Connected'
    #create a cursor object
    cur = con.cursor()

    all_data = {}
    #for every table name in the dictionary
    for table_name in hash_dict.keys():
        #get a list of all the jsons from the table
        cur.execute('SELECT json from '+table_name)
        print 'Generating '+table_name+' dictionary....'

        #this returns a list of tuples: the first item in each tuple is our json
        items = cur.fetchall()

        #create a list of jsons
        item_jsons = [json.loads(item[0]) for item in items]

        #create a dictionary with the hashes as keys
        #and the jsons as values
        item_dict = {}
        hash = hash_dict[table_name]
        for item in item_jsons:
            item_dict[item[hash]] = item

        #add that dictionary to our all_data using the name of the table
        #as a key.
        all_data[table_name] = item_dict
    print 'Dictionary Generated!'
    return all_data
all_data=build_dict(hash_dict)

print 'User: ', displayName
print 'Grimoire: ', grimoireScore
print 'Subclass: ', all_data['DestinyInventoryItemDefinition'][subclassHash]['itemName']
print 'Level: ', baseCharacterLevel
print 'Light: ', light
print 'Intellect: ', intellect, 'Discipline: ', discipline, 'Strength: ', strength
print 'Armor: ', armor, 'Agility: ', agility, 'Recovery: ', recovery, 'Optics: ', optics, 'Defense: ', defense
print 'Hours played: ', "{:.2f}".format(float(minutesPlayedTotal)/1440)
print 'Last date played: ', dateLastPlayed
time.sleep(10)

#subclass icon jpg
ur=all_data['DestinyInventoryItemDefinition'][subclassHash]['icon']
img = requests.get("http://www.bungie.net"+ur, headers=HEADERS)
jpg=all_data['DestinyInventoryItemDefinition'][subclassHash]['itemName']

#set the location of the image
newpath = os.path.join('C:\Documents', jpg)
f=open(newpath, "wb")
f.write(img.content)


#loop for all items jpg
i=0
while i<len(char_inv['Response']['data']['items']):
    print i
    print char_inv['Response']['data']['items'][i]['itemId']
    hash=char_inv['Response']['data']['items'][i]['itemHash']
    inv=all_data['DestinyInventoryItemDefinition'][hash]
    print inv['itemName']
    ur=all_data['DestinyInventoryItemDefinition'][hash]['icon']
    img = requests.get("http://www.bungie.net"+ur, headers=HEADERS)
    jpg=inv['itemName']+'.jpg'
    try:
        newpath = os.path.join('C:\Documents', jpg)
        f=open(newpath, "wb")
        f.write(img.content)
    except:
        q=list(jpg)
        q[0]=''
        q[len(q)-5]=''
        jpg="".join(q)
        newpath = os.path.join('C:\Documents', jpg)
        f=open(newpath, "wb")
        f.write(img.content)
    i=i+1
