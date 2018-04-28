from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import *
from bs4 import BeautifulSoup
import requests
import json
import urllib
import ast
from Crypto.Cipher import AES
import binascii

#encryption key and initialization vector
ENCRYPTION_KEY = '' #enter key here
ENCRYPTION_IV = '' #enter initialization vector here


#######################################
#these methods are responsible for doing custom AES decryption of the passphrase from the database
#to aid the login authentication process

def decrypt_string(string):
    obj2 = AES.new(ENCRYPTION_KEY, AES.MODE_CBC, ENCRYPTION_IV)
    return obj2.decrypt(string)
    
def decrypt_passphrase(encrypted_byte):
    encOrig_unhexlified_decoded = ast.literal_eval(binascii.unhexlify(encrypted_byte).decode('utf-8'))
    decrypted_passphrase = ""
    length = len(encOrig_unhexlified_decoded)
    for i in range(0,length):
        if i != length-1:
            decrypted_passphrase += decrypt_string(encOrig_unhexlified_decoded[i]).decode('utf-8').replace(" ","") + " "
        else:
            decrypted_passphrase += decrypt_string(encOrig_unhexlified_decoded[i]).decode('utf-8').replace(" ","")
    return decrypted_passphrase

#########################################

#Simply translates date from the format specified in my custom Google Drive JSON file to a
#human friendly version
def translateDate(date):
    year = date[0:4]
    month = date[4:6]
    day = date[6:8]
    minute = date[10:12]
    second = date[12:14]
    hour = date[8:10]
    return "{}/{}/{} {}:{}:{}".format(month,day,year,hour,minute,second)
#Gathers infromation from a google drive
def getRecordsArray():
    recordsFileUrl = 'https://drive.google.com/uc?export=download&id=ENTERIDHERE'
    response = urllib.request.urlopen(recordsFileUrl)
    responseData = response.read().decode('utf-8')
    responseJson = json.loads(responseData)
    recordsArray = []
    
    for a in responseJson.items():
        date = a[0]
        data = ast.literal_eval(a[1])
        if data == []:
            pass
        else:
            recordsArray += [[translateDate(date)]+data]
    recordsArray.sort()
    return recordsArray
#WEBPAGE OPERATIONS::::

#Checks to see if the user has entered a valid username, password and passphrase
#If the attempt is unsuccessful, an error will be displayed
#If the attempt is successful, the user will be logged in and gain access to
#the member pages
def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        passphrase = request.POST.get('passphrase')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                try:
                    decrypted_result = decrypt_passphrase(UserProfile.objects.get(user=user).passphraseData)
                except:
                    return render(request, 'cryptocurrency/login.html', {'error_message': 'Invalid login'})
                if decrypted_result != passphrase:
                    return render(request, 'cryptocurrency/login.html', {'error_message': 'Invalid login'})
                login(request, user)
                if 'next' in request.POST:
                    return redirect(request.POST.get('next'))
                return render(request, 'cryptocurrency/home.html')
        else:
            return render(request, 'cryptocurrency/login.html', {'error_message': 'Invalid login'})
    else:
        if request.user.is_authenticated is True:
            return render(request, 'cryptocurrency/home.html')
        elif request.GET.get('next'):
            return render(request, 'cryptocurrency/login.html', {'error_message': 'You must log in to see this page' })
    return render(request, 'cryptocurrency/login.html')
    

def logout_user(request):
    logout(request)
    return render(request, 'cryptocurrency/home.html')
    
#Webpages:
#Visitor pages: these simply point to templates
    
def home(request):
    return render(request, 'cryptocurrency/home.html')
    
def blog(request):
    return render(request, 'cryptocurrency/blog.html')
    
def faq(request):
    return render(request, 'cryptocurrency/faq.html')
    
def journey(request):
    return render(request, 'cryptocurrency/journey.html')
    
def sources(request):
    return render(request, 'cryptocurrency/sources.html')
    
def prices(request):
    return render(request, 'cryptocurrency/prices.html')

#Pages that require authorized login:


#This is the tracker. It gathers information from the nanopool.org API such as
# - balance
# - machine names
# - machine hashrates (including 24hr average)
# - payout limit
#
#This view also gathers information from a JSON file located on Google Drive
#relating to records using the getRecordsArray() method

@login_required(login_url='/login/')
def tracker(request):
    zecSoupContent = []
        
    ZECMININGADDRESS = "" #Enter mining ZEC address here
    
    zecUrls = [ "https://api.nanopool.org/v1/zec/user/{}".format(ZECMININGADDRESS),
                "https://api.nanopool.org/v1/zec/usersettings/{}".format(ZECMININGADDRESS),
                "https://api.nanopool.org/v1/zec/history/{}".format(ZECMININGADDRESS)]
                
    zecSoupContents = []
    for url in zecUrls:
        zecSoupContents += [BeautifulSoup(requests.get(url).content, 'html.parser').text]
        
    zecJsons = []
    for zecSoupContent in zecSoupContents:
        zecJsons += [json.loads(zecSoupContent)]
        
    zecWorkers = []
    for a in zecJsons[0]['data']['workers']:
        zecWorkers += [[a['id'],float(a['hashrate'])]]
    
    zecBalance = round(float(zecJsons[0]['data']['balance']), 4)
    zecHashrate = zecJsons[0]['data']['hashrate']
    zecHashrate24 = zecJsons[0]['data']['avgHashrate']['h24']
    zecPayoutLimit = zecJsons[1]['data']['payout']
    zecBalancePercent = round(zecBalance/zecPayoutLimit*100, 2)
    zecProfitLink = "https://www.cryptocompare.com/mining/calculator/zec?HashingPower={}&HashingUnit=H%2Fs&PowerConsumption=0&CostPerkWh=0".format(zecHashrate24)
    
    x = {}
    x['recordsArray'] = getRecordsArray()[::-1][0:13]
    x['zecWorkers'] = zecWorkers
    x['zecNumWorkers'] = len(zecWorkers)
    x['zecBalance'] = zecBalance
    x['zecBalancePercent'] = zecBalancePercent
    x['zecHashrate'] = zecHashrate
    x['zecHashrate24'] = zecHashrate24
    x['zecWorkers'] = zecWorkers
    x['zecProfitLink'] = zecProfitLink
    return render(request, 'cryptocurrency/tracker.html', x)

#This simply gathers the full record and displays it
@login_required(login_url='/login/') 
def records(request):
    x = {}
    x['recordsArray'] = getRecordsArray()[::-1]
    return render(request, 'cryptocurrency/records.html', x)

#This displays the payment information for members involved from
#the database models.
@login_required(login_url='/login/')
def payments(request):
    phases = Phase.objects.all()
    paymentsArray = []
    for a in phases:
        payoutPeriods = PayoutPeriod.objects.filter(phase=a)
        payoutPeriodInfoArray = []
        for b in payoutPeriods:
            periods = Period.objects.filter(payoutPeriod=b).order_by('num')
            payoutPeriodTotal = 0
            for c in periods:
                payoutPeriodTotal += c.amount
            payoutPeriodInfoArray += [[b.num,[periods[::-1]],round(payoutPeriodTotal,4),b.notes]]
        paymentsArray += [[a.num,payoutPeriodInfoArray[::-1]]]
    x = {}
    x['paymentsArray'] = paymentsArray[::-1]
    return render(request, 'cryptocurrency/payments.html', x)

#This sinply displays the user's information (username, first and last name)
@login_required(login_url='/login/')
def userProfile(request):
    username = request.user
    userObject = User.objects.get(username=username)
    userProfile = UserProfile.objects.get(user=userObject)
    x = {}
    x['userProfile'] = userProfile
    x['username'] = username
    return render(request, 'cryptocurrency/userprofile.html', x)
    
    
    
