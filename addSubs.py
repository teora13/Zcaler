import http.client
import requests
import time
import json
from tqdm.auto import tqdm

# creating timestamp and obfuscate key from API key
def obfuscateApiKey():
    seed = 'key'
    global timeStamp
    timeStamp = int(time.time() * 1000)
    n = str(timeStamp)[-6:]
    r = str(int(n) >> 1).zfill(6)
    global key
    key = ""
    for i in range(0, len(str(n)), 1):
        key += seed[int(str(n)[i])]
    for j in range(0, len(str(r)), 1):
        key += seed[int(str(r)[j]) + 2]
obfuscateApiKey()

# autenticates a new session from key, timestamp and logpass to get a sessionID
def autenticateSession():
    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache"
    }
    response = requests.post('https://admin.zscaler.net/api/v1/authenticatedSession', json={"username": "username", "password": "password", "apiKey": key, "timestamp": timeStamp}, headers=headers)
    global jsID
    jsID = response.cookies['JSESSIONID']
autenticateSession()

# activates session with sessionID
def activateSession():
    global conn
    conn = http.client.HTTPSConnection("admin.zscaler.net",  443, timeout=10)
    global headers
    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache",
        'cookie': 'JSESSIONID={}'.format(jsID)
    }
    conn.request("POST", "/api/v1/status/activate", headers=headers)
activateSession()


def postSubLocations():
# creates a new file to write there info about existed sublocations
    fileExistedOffices = 'Existed_Offices_log.txt'
    fileEx = open(fileExistedOffices, 'w')
# makes a new connection
    conn.request("GET", "/api/v1/locations", headers=headers)
# gets info about all locations
    allOffices = json.loads(str(conn.getresponse().read().decode("utf-8")))
# filter locations
    filOffices = (list(filter(lambda store: 'ONTARIO-OFFICE' in store['name'], allOffices)))
# makes a new list with their ids
    idOffices = []
    for i in filOffices:
        idOffices.append(i['id'])
# makes a progress bar in a command line
    pbar = tqdm(total=len(idOffices), desc='ONTARIO OFFICES')
# creates a new iteration for each id in a list to get its sublocations list
    for position, id in enumerate(idOffices):
        conn.request("GET", "/api/v1/locations/{}".format(id), headers=headers)
# keeps its name in variable to use it in a future
        currentName = json.loads(str(conn.getresponse().read().decode("utf-8")))['name']
        conn.request("GET ", "/api/v1/locations/{}/sublocations".format(id), headers=headers)
        subconn = http.client.HTTPSConnection("admin.zscaler.net", 443, timeout=10)
        subsInternal = json.loads(str(conn.getresponse().read().decode("utf-8")))
# payload we need to send with needed settings
        payload = {
            "parentId": id,
            "name": "INTERNAL-ONTARIO-OFFICE",
            "ipAddresses": ["127.0.0.1-127.0.0.5"],
            "upBandwidth": -1,
            "dnBandwidth": -1,
            "ofwEnabled": True,
            "ipsControl": True
        }
        pbar.update()
# checks every sublocation for parent location
        for sub in subsInternal:
# if location has sublocation with necessary name than skip it and writes its name in a txt file
            if 'INTERNAL'.lower() in [str(s).lower() for s in sub.values()]:
                    fileEx = open(fileExistedOffices, 'a+')
                    fileEx.write((currentName)+'\n')
# if location has not this sub than send POST request to create a new one
            elif (list(filter(lambda store: 'INTERNAL'.lower() not in store['name'.lower()], subsInternal))):
                while True:
                    try:
                        subconn.request("POST", "/api/v1/locations", json.dumps(payload), headers)
                        break
                    except Exception:
                        subconn.close()
        fileEx.close()
    pbar.close()

postSubLocations()
