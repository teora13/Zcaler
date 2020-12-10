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


def deleteSubLocations():
# makes a new connection
    conn.request("GET", "/api/v1/locations", headers=headers)
# gets info about all locations
    allOffices = json.loads(str(conn.getresponse().read().decode("utf-8")))
# filter locations
    filtredOffices = (list(filter(lambda store: 'OFFICE' in store['name'] and 'LAB' not in store['name'], allOffices)))
# makes a new list with locations ids
    idStores = []
    for i in filtredOffices:
        idStores.append(i['id'])
# makes a new list with sublocations ids
    idSubs = []

# makes a progress bar for filtering sublocations
    pbar1 = tqdm(total=len(idStores), desc='Filtering')
# creates a new iteration for each id in a list to get its sublocations list
    for position, id in enumerate(idStores):
        conn.request("GET ", "/api/v1/locations/{}/sublocations".format(id), headers=headers)
        subLocs = json.loads(str(conn.getresponse().read().decode("utf-8")))
# list of names that should be deleted
        deleteOffices = ['TORONTO', 'ETOBICOKE', 'MISSISSAUGA', 'BRAMPTON']
        pbar1.update()
        for sub in subLocs:
            for name in sub.values():
                if name in deleteOffices:
                    idSubs.append(sub['id'])
    pbar1.close()
    time.sleep(2)

# makes a progress bar for deleting sublocations
    pbar2 = tqdm(total=len(idSubs), desc='Deleting')
# makes a new connection and sends request for each number in idSubs where we store list of sublocations for deleting them
    for position, id in enumerate(idSubs):
        subconn = http.client.HTTPSConnection("admin.zscaler.net",  443, timeout=10)
        subconn.request("DELETE ", "/api/v1/locations/{}".format(id), headers=headers)
        subconn.close()
# time sleep because API server has restrictions on sending requests
        time.sleep(2)
        pbar2.update()
    pbar2.close()

deleteSubLocations()