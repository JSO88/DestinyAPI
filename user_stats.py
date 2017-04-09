import requests
import json
import sqlite3

#ask for user key
apikey = raw_input('API Key: ')
HEADERS = {"X-API-Key": apikey}

#ask for Destiny user
user=raw_input('User name: ')

#gets Destiny user ID
r = requests.get("http://www.bungie.net/Platform/Destiny/SearchDestinyPlayer/2/"+user+"/", headers=HEADERS);
membership = r.json()
membershipId=membership['Response'][0]['membershipId']

#gets character ID (each user has up to 3 characters)
character = int(raw_input('Character (0,1,2): '))
r = requests.get("http://www.bungie.net/Platform/Destiny/2/Account/"+membershipId+"/Summary/", headers=HEADERS);
summary = r.json()
characterId=summary['Response']['data']['characters'][character]['characterBase']['characterId']

#ask for game mode stats 
allmodes=('None', 'Story', 'Strike', 'Raid', 'AllPvP', 'Patrol', 'AllPvE', 'PvPIntroduction', 'ThreeVsThree', 
'Control', 'Lockdown', 'Team', 'FreeForAll', 'Nightfall', 'Heroic', 'AllStrikes', 'IronBanner', 'AllArena', 
'Arena', 'ArenaChallenge', 'TrialsOfOsiris', 'Elimination', 'Rift', 'Mayhem', 'ZoneControl', 'Racing')

mode=raw_input('Game mode: ')
r=list(mode)
a=r[0].lower()
r[0]=a
mode2="".join(r)
print(mode2)

while mode not in allmodes:
    print('Error, mode not recognized')
    print('Try again!')
    mode=raw_input('Game mode: ')
    r=list(mode)
    a=r[0].lower()
    r[0]=a
    mode2="".join(r)

#ask for periodicity of data
period=raw_input('Period (Daily, Monthly, allTime): ')
r=list(period)
a=r[0].upper()
r[0]=a
period2="".join(r)

#gets data depending on period selected
if period2=='Monthly':
    monthstart=raw_input('Month start (YYYY-MM): ')
    monthend=raw_input('Month end (YYYY-MM): ')
    params={'modes':mode,'periodType':period2 , 'monthstart':monthstart, 'monthend':monthend, 'groups':'General'}
    r = requests.get("http://www.bungie.net/Platform/Destiny/Stats/2/"+membershipId+"/"+characterId+"/", params=params, headers=HEADERS);
    user_stats = r.json()
    
    #the following three lines create a txt file with the json info (not necessary)
    #f=open('userstats.txt','w')
    #f.write(json.dumps(user_stats,indent=4))
    #f.close()
    
    conn = sqlite3.connect('User_Stats_db.sqlite')
    cur = conn.cursor()

    # Creates new table
    cur.executescript('''
    DROP TABLE IF EXISTS User_Stats;

    CREATE TABLE User_Stats (
        id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        p   TEXT,
        k   INTEGER,
        d   INTEGER,
        a   INTEGER,
        kd  REAL,
        kad REAL
    );
    ''')
    
    #Fill new table with data
    j=0
    while j<len(user_stats['Response'][mode2][period]):
        period3=user_stats['Response'][mode2][period][j]['period']
        kills=user_stats['Response'][mode2][period][j]['values']['kills']['basic']['displayValue']
        deaths=user_stats['Response'][mode2][period][j]['values']['deaths']['basic']['displayValue']
        assists=user_stats['Response'][mode2][period][j]['values']['assists']['basic']['displayValue']
        kd1=float(kills)/float(deaths)
        kad1=(float(kills)+float(assists))/float(deaths)
        j=j+1
        cur.execute('''INSERT INTO User_Stats
            (p, k, d, a, kd, kad)
            VALUES ( ?, ?, ?, ?, ?, ? )''',
            ( period3, kills, deaths, assists, kd1, kad1 ) )

        conn.commit()

#need to fix the daily part
#works with lapse=single and periods within a month
elif period2=='Daily':
    lapse=raw_input('Lapse (all or single): ')
    if lapse=='all':
        w={'2015':{'10':'31','11':'30','12':'31'},
        '2016':{'01':'31','02':'29','03':'31','04':'30','05':'31','06':'30','07':'31'}}
        for ykey in w:
            for mkey in w[ykey]:
                print ykey, "-",mkey, w[ykey][mkey]
                daystart=ykey+'-'+mkey+'-01'
                dayend=ykey+'-'+mkey+'-'+w[ykey][mkey]
                params={'modes':mode,'periodType':period2 , 'daystart':daystart, 'dayend':dayend, 'groups':'General'}
                r = requests.get("http://www.bungie.net/Platform/Destiny/Stats/2/"+membershipId+"/"+characterId+"/", params=params, headers=HEADERS);
                user_stats = r.json()
                conn = sqlite3.connect('User_Stats_db.sqlite')
                cur = conn.cursor()

                # Make new table
                try:
                    cur.executescript('''CREATE TABLE User_Stats (
                    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                    p   TEXT,
                    k   INTEGER,
                    d   INTEGER,
                    a   INTEGER,
                    kd  REAL,
                    kad REAL);
                    ''')
                except:
                    print 'already'

                #fill table
                j=0
                while j<len(user_stats['Response'][mode2][period]):
                    period3=user_stats['Response'][mode2][period][j]['period']
                    kills=user_stats['Response'][mode2][period][j]['values']['kills']['basic']['displayValue']
                    deaths=user_stats['Response'][mode2][period][j]['values']['deaths']['basic']['displayValue']
                    assists=user_stats['Response'][mode2][period][j]['values']['assists']['basic']['displayValue']
                    try:
                        kd1=float(kills)/float(deaths)
                    except:
                        kd1=float(kills)
                    try:
                        kad1=(float(kills)+float(assists))/float(deaths)
                    except:
                        kad1=float(kills)+float(assists)
                    j=j+1
                    cur.execute('''INSERT INTO User_Stats
                        (p, k, d, a, kd, kad)
                        VALUES ( ?, ?, ?, ?, ?, ? )''',
                        ( period3, kills, deaths, assists, kd1, kad1 ) )

                    conn.commit()
    else:
        daystart=raw_input('Day start (YYYY-MM-DD): ')
        dayend=raw_input('Day end (YYYY-MM_DD): ')
        params={'modes':mode,'periodType':period2 , 'daystart':daystart, 'dayend':dayend, 'groups':'General'}
        r = requests.get("http://www.bungie.net/Platform/Destiny/Stats/2/"+membershipId+"/"+characterId+"/", params=params, headers=HEADERS);
        user_stats = r.json()
        
        conn = sqlite3.connect('User_Stats_db.sqlite')
        cur = conn.cursor()

        # Make new table
        cur.executescript('''
        DROP TABLE IF EXISTS User_Stats;

        CREATE TABLE User_Stats (
            id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            p   TEXT,
            k   INTEGER,
            d   INTEGER,
            a   INTEGER,
            kd  REAL,
            kad REAL
        );
        ''')
        
        #Fill table with data
        j=0
        while j<len(user_stats['Response'][mode2][period]):
            period3=user_stats['Response'][mode2][period][j]['period']
            kills=user_stats['Response'][mode2][period][j]['values']['kills']['basic']['displayValue']
            deaths=user_stats['Response'][mode2][period][j]['values']['deaths']['basic']['displayValue']
            assists=user_stats['Response'][mode2][period][j]['values']['assists']['basic']['displayValue']
            kd1=float(kills)/float(deaths)
            kad1=(float(kills)+float(assists))/float(deaths)
            j=j+1
            cur.execute('''INSERT INTO User_Stats
                (p, k, d, a, kd, kad)
                VALUES ( ?, ?, ?, ?, ?, ? )''',
                ( period3, kills, deaths, assists, kd1, kad1 ) )

            conn.commit()
            
else:
    period='allTime'
    params={'modes':mode,'periodType':'AllTime', 'groups':'General'}
    r = requests.get("http://www.bungie.net/Platform/Destiny/Stats/2/"+membershipId+"/"+characterId+"/", params=params, headers=HEADERS);
    user_stats = r.json()
    print 'All Time'
    print 'Kills: ', user_stats['Response'][mode2][period]['kills']['basic']['displayValue']
    print 'Deaths: ', user_stats['Response'][mode2][period]['deaths']['basic']['displayValue']
    print 'Assists: ', user_stats['Response'][mode2][period]['assists']['basic']['displayValue']
    print 'K/D: ', "{:.2f}".format(float(user_stats['Response'][mode2][period]['kills']['basic']['displayValue'])/float(user_stats['Response'][mode2][period]['deaths']['basic']['displayValue']))
    print '(K+A)/D: ', "{:.2f}".format((float(user_stats['Response'][mode2][period]['kills']['basic']['displayValue'])+float(user_stats['Response'][mode2][period]['assists']['basic']['displayValue']))/float(user_stats['Response'][mode2][period]['deaths']['basic']['displayValue']))

##Some parameters description

#modes	      Game modes to return. Values: None, Story, Strike, Raid, AllPvP, Patrol, AllPvE, PvPIntroduction, ThreeVsThree, Control, Lockdown, Team, FreeForAll, Nightfall, Heroic, AllStrikes, IronBanner, AllArena, Arena, ArenaChallenge, TrialsOfOsiris, Elimination, Rift, Mayhem, ZoneControl, Racing
#characterId  The id of the character to retrieve. You can omit this character ID or set it to 0 to get aggregate stats across all characters.
#periodType	  Indicates a specific period type to return. Optional. May be: Daily, Monthly, AllTime, or Activity
#groups	      Group of stats to include, otherwise only general stats are returned. Comma separated list is allowed. Values: General, Weapons, Medals, Enemies
#monthstart	  First month to return when monthly stats are requested. Use the format YYYY-MM.
#monthend	    Last month to return when monthly stats are requested. Use the format YYYY-MM.
#daystart	    First day to return when daily stats are requested. Use the format YYYY-MM-DD
#dayend	      Last day to return when daily stats are requested. Use the format YYYY-MM-DD.
