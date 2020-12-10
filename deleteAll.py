import http.client
import requests
import time
import json

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

# deleting parent locations also deletes their sublocations, that why we only send  1 DELETE request for each
def deleteLocations():
    conn.request("GET", "/api/v1/locations", headers=headers)
    allOffices = (json.loads(str(conn.getresponse().read().decode("utf-8"))))
# filters location by name to find all 'offices' and skip all 'labs'
    filtredOffices = (list(filter(lambda store: 'OFFICE' in store['name'] and 'LAB' not in store['name'], allOffices)))
# keeps their ids in a list
    idList = []
    for i in filtredOffices:
        idList.append(i['id'])
# sends request for each id in a idList
    for position, id in enumerate(idList):
        conn.request("DELETE ", "/api/v1/locations/{}".format(id), headers=headers)

deleteLocations()