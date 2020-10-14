from django.shortcuts import render, redirect
from django.contrib import messages
import requests
import datetime
import json

userPresent = False
user = None
allusers = []
transactions = []
locData = []
lng0 = 0
lat0 = 0
i = None
if i==None:
    i = int(input("Enter Node ID to Connect to : "))


def getNodeAddress(i):
    if i == 1:
        return "http://127.0.0.1:8000"
    elif i == 2:
        return "http://127.0.0.1:8001"
    elif i == 3:
        return "http://127.0.0.1:8002"


def fetchData():
    global i, allusers, transactions, locData, lng0, lat0
    get_chain_address = "{}/chain".format(getNodeAddress(i))
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        allusers = []
        transactions = []
        locData = []
        chain = json.loads(response.content)
        lat0 = 0
        lng0 = 0
        ttp = 0
        for block in chain["chain"]:
            temp = json.loads(block)
            if int(temp['transactionType'])==1:
                temp['transactionType'] = "New Block"
            elif int(temp['transactionType'])==2:
                temp['transactionType'] = "Location Update"
            else:
                temp['transactionType'] = "Transfered Record"

            if int(temp['product']['productType'])==1:
                temp['product']['productType'] = "PPE Kit"
            elif int(temp['product']['productType'])==2:
                temp['product']['productType'] = "Mask"
            else:
                temp['product']['productType'] = "Sanitizer"

            transactions.append(temp)
            locData.append(["BLOCK_"+str(ttp), temp['location']['lat'], temp['location']['lng']])
            lat0 += int(temp['location']['lat'])
            lng0 += int(temp['location']['lng'])
            ttp+=1
        for tuser in chain["users"]:
            temp = json.loads(tuser)
            if int(temp['userType'])==1:
                temp['userType'] = "Manufacturer"
            elif int(temp['userType'])==2:
                temp['userType'] = "Supplier"
            elif int(temp['userType'])==3:
                temp['userType'] = "Seller"
            else:
                temp['userType'] = "Buyer"
            allusers.append(temp)
        transactions.pop(0)
        locData.pop(0)
        print(allusers)
        if ttp>1:
            lat0 = lat0//(ttp-1)
            lng0 = lng0//(ttp-1)


def home(request):
    global user, userPresent, allusers, transactions, locData, lat0, lng0
    fetchData()
    hasAuth = False
    if userPresent:
        if int(user['userType'])==1:
            hasAuth=True
    return render(request, 'SubApp/home.html', {'userPresent': userPresent, 
                                                'hasAuth': hasAuth,
                                                'user': user, 
                                                'transactions': transactions[::-1], 
                                                'users': allusers, 
                                                'loc': json.dumps(locData), 
                                                'lat': json.dumps([lat0]), 
                                                'lng': json.dumps([lng0])})


def viewBlock(request):
    global user, userPresent, allusers, transactions, locData, lat0, lng0
    print(request.POST.get("productId"))
    tempProdId = int(request.POST.get("productId"))
    tLastIndex = 0
    tTransac = []
    tLocData = []
    tAllUsers = []
    tLat = 0
    tLng = 0
    ii=0
    tii = 1
    hasAuth = False
    for ttp in transactions:
        if int(ttp['product']['productId'])==tempProdId:
            tTransac.append(ttp)
            tLastIndex = ii
            tLocData.append(['BLOCK_'+str(tii), float(ttp['location']['lat']), float(ttp['location']['lng'])])
            tLng+=float(ttp['location']['lng'])
            tLat+=float(ttp['location']['lat'])
            tii+=1
        ii+=1
    tLat = tLat//(tii-1)
    tLng = tLng//(tii-1)
    for ttp in allusers:
        if ttp['username']!=transactions[tLastIndex]['ownerRelation']['name']:
            tAllUsers.append(ttp)
    if userPresent:
        if user['username']==transactions[tLastIndex]['ownerRelation']['name']:
            hasAuth=True
    return render(request, 'SubApp/viewBlock.html', {'userPresent': userPresent,
                                                     'hasAuth': hasAuth,
                                                     'user': user,
                                                     'tblock': transactions[tLastIndex], 
                                                     'transactions': tTransac[::-1], 
                                                     'users': tAllUsers, 
                                                     'loc': json.dumps(tLocData), 
                                                     'lat': json.dumps([tLat]), 
                                                     'lng': json.dumps([tLng])})


def viewUser(request):
    global allusers, transactions, locData, lat0, lng0
    tempUserName = request.POST.get("username")
    tTransac = []
    tLocData = []
    tUser = None
    tLat = 0
    tLng = 0
    ii=0
    tii = 1
    for ttp in allusers:
        if ttp['username']==tempUserName:
            tUser = ttp
            break
    for ttp in transactions:
        if ttp['ownerRelation']['name']==tempUserName:
            tTransac.append(ttp)
            tLocData.append(['BLOCK_'+str(tii), float(ttp['location']['lat']), float(ttp['location']['lng'])])
            tLng+=float(ttp['location']['lng'])
            tLat+=float(ttp['location']['lat'])
            tii+=1
        ii+=1
    if tii>1:
        tLat = tLat//(tii-1)
        tLng = tLng//(tii-1)
    print(tTransac)
    return render(request, 'SubApp/viewUser.html', { 'user': tUser,
                                                     'transactions': tTransac[::-1], 
                                                     'loc': json.dumps(tLocData), 
                                                     'lat': json.dumps([tLat]), 
                                                     'lng': json.dumps([tLng])})


def addBlock(request):
    global user, userPresent
    return render(request, 'SubApp/addBlock.html', {'userPresent': userPresent, 'user': user})
    

def addNewBlock(request):
    global i, user
    productType = request.POST.get("productType")
    lat = request.POST.get("latitude")
    lng = request.POST.get("longitude")
    postObject = {
        'prodId': 0,
        'productType': productType,
        'latitude': lat,
        'longitude': lng,
        'username': user['username'],
        'transacType': 1
    }
    newTxAddress = "{}/newTransaction".format(getNodeAddress(i))
    requests.post(newTxAddress,
                  json=postObject,
                  headers={'Content-type': 'application/json'})
    mineAddress = "{}/mine".format(getNodeAddress(i))
    requests.get(mineAddress,
                  headers={'Content-type': 'application/json'})
    return redirect('/')


def updateBlock(request):
    global i, user
    productId = request.POST.get("productId")
    productType = request.POST.get("productType")
    lat = request.POST.get("latitude")
    lng = request.POST.get("longitude")
    postObject = {
        'prodId': productId,
        'productType': productType,
        'latitude': lat,
        'longitude': lng,
        'username' : user['username'],
        'transacType': 2
    }
    print(postObject)
    newTxAddress = "{}/newTransaction".format(getNodeAddress(i))
    requests.post(newTxAddress,
                  json=postObject,
                  headers={'Content-type': 'application/json'})
    mineAddress = "{}/mine".format(getNodeAddress(i))
    requests.get(mineAddress,
                  headers={'Content-type': 'application/json'})
    return redirect('/')


def transferBlock(request):
    global i, user
    productId = request.POST.get("productId")
    productType = request.POST.get("productType")
    lat = request.POST.get("latitude")
    lng = request.POST.get("longitude")
    tpUserName = request.POST.get("username")
    postObject = {
        'prodId': productId,
        'productType': productType,
        'latitude': lat,
        'longitude': lng,
        'username' : tpUserName,
        'transacType': 3
    }
    newTxAddress = "{}/newTransaction".format(getNodeAddress(i))
    requests.post(newTxAddress,
                  json=postObject,
                  headers={'Content-type': 'application/json'})
    mineAddress = "{}/mine".format(getNodeAddress(i))
    requests.get(mineAddress,
                  headers={'Content-type': 'application/json'})
    return redirect('/')


def signup(request):
    global userPresent
    if userPresent:
        messages.info(request, f'You need to first Log Out of this Account to create a new Account ...')
        return redirect('/home')
    else:
        return render(request, 'SubApp/signup.html')


def signUpUser(request):
    global userPresent
    if userPresent:
        messages.info(request, f'You need to first Log Out of this Account to create a new Account ...')
        return redirect('/home')
    else:
        data = {"username": request.POST.get('username'),
                "password" : request.POST.get('password'),
                "name": request.POST.get('first_name') + " " + request.POST.get('last_name'),
                "type": int(request.POST.get('userType'))}
        headers = {'Content-Type': "application/json"}
        response = requests.post(getNodeAddress(i) + "/addUser", data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            userPresent = False
            return render(request, 'SubApp/login.html')
        messages.error(request, f'Something went Wrong')
        return redirect('/')


def login(request):
    return render(request, 'SubApp/login.html')


def loginUser(request):
    global userPresent, i, user
    data = {"username": request.POST.get('username'), "password" : request.POST.get('password')}
    headers = {'Content-Type': "application/json"}
    response = requests.post(getNodeAddress(i) + "/loginUser", data=json.dumps(data), headers=headers)
    if response.status_code == 200:
        userPresent = True
        user = json.loads(response.json()['user'])
        return redirect('/home')
    userPresent = False
    return render(request, 'SubApp/login.html')


def logout(request):
    global userPresent
    userPresent = False
    return redirect('/home')


def profile(request):
    global userPresent, user
    if userPresent:
        return render(request, 'SubApp/profile.html', {'user': user})
    else:
        messages.error(request, 'You need to first Log In to View your Profile Page')
        return redirect('/login')