import requests
import os
import json
import CookiesLoader
import re
import time

IpasniekaNumurs = 'kc366'
Serija = 'OB'

LoggedUserPattern = "<h4 class=\"capitalize\">"
timeout = 1.6


def check_and_wait(last_request_time):
    elapsed_time = time.time() - last_request_time
    if elapsed_time < timeout:
        sleep_time = timeout - elapsed_time
        print(f"{timeout}s since previous form sent")
        time.sleep(sleep_time)
    else:
        print(f"{elapsed_time:.2f}s since previous form sent")
    return time.time()  


def GetCaptcha(htmlbody):
    if '<img src="/captcha' not in htmlbody:
        print("CAPTCHA NOT FOUND!!!!!")
        return False
    else:
        pattern = r'<img src="([^"]+/captcha\.php[^"]*)"'
        CaptchaUrlFull = "https://e.csdd.lv" + re.findall(pattern, htmlbody)[0]
        return CaptchaUrlFull


def CSDD():
    headers = {
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        'Accept-Encoding': 'gzip, deflate, br'
    }

    if not os.path.isfile("./CSDDaccount.json"):
        print("No CSDDaccount.json file found! Exiting script...")
        return

    __Session = requests.Session()
    with open("./CSDDaccount.json", "r") as f:
        csdd_cookies = json.load(f)
    requests.utils.add_dict_to_cookiejar(__Session.cookies, csdd_cookies)
    last_request_time = time.time()
    resp = __Session.get("https://e.csdd.lv")

    if LoggedUserPattern in str(resp.content):
        LoggedUser = re.findall(r"<h4 class=\"capitalize\">(.*?)</h4>", str(resp.content.decode('utf-8')))[0]
        print(f"Successfully logged in CSDD! Logged in as {LoggedUser}")

        forms = [
            {'rn_find': IpasniekaNumurs, 'RnFind': 'Meklēt'},
            {'confirmTl': 'Atlasīt izvēles numurus'},
            {'nrSeries': Serija, 'chooseNrSeries': 'Izvēlēties'}
        ]

        
        for i in range(3):
            last_request_time = check_and_wait(last_request_time)
            response = __Session.post("https://e.csdd.lv/izvnum/", data=forms[i], headers=headers)
            body = response.content.decode('utf-8')

            with open(f"form{i+1}.html", 'w', encoding="utf-8") as f:
                f.write(body)
            print(f'{"--" * (i+1)}Sent form nr. > {i+1}')

        for numurs in [777, 666, 7777, 6666, 192]:
            last_request_time = check_and_wait(last_request_time)
            response = __Session.post("https://e.csdd.lv/izvnum/", data={
                'chosenNR': f'{Serija}{numurs}',
                'nrSeries': Serija,
                'seriesType': None,
                'chooseNr': 'Izvēlēties'
            }, headers=headers)
            body = response.content.decode('utf-8')

            if f'Izvēles numurs: <b>{Serija}{numurs}</b>' in body:
                print(f'--------{Serija}{numurs} available!!!')

                cURL = GetCaptcha(body)
                if cURL:
                    response = __Session.get(cURL, headers=headers)
                    with open('captcha.png', 'wb') as f:
                        f.write(response.content)

                    CaptchaAnswer = input("Enter captcha > ")
                    ConfirmForm = {
                        'kac_select': 'K',
                        'capcha': CaptchaAnswer,
                        'chosenNR': f'{Serija}{numurs}',
                        'nrSeries': Serija,
                        'seriesType': None,
                        'confirmKac': 'Turpināt'
                    }
                    last_request_time = check_and_wait(last_request_time)
                    response = __Session.post("https://e.csdd.lv/izvnum/", data=ConfirmForm, headers=headers)
                    with open("prefinalconfirm.html", 'w', encoding='utf-8') as f:
                        f.write(response.content.decode('utf-8'))

                    last_request_time = check_and_wait(last_request_time)
                    response = __Session.post("https://e.csdd.lv/izvnum/", data={
                        'kac_code': 'K',
                        'chosenNR': f'{Serija}{numurs}',
                        'nrSeries': Serija,
                        'payIzvNum': 'Apstiprināt'
                    }, headers=headers)
                    body = response.content.decode('utf-8')
                    with open("finalconfirm.html", 'w', encoding='utf-8') as f:
                        f.write(body)

                break
            else:
                print(f'--------{Serija}{numurs} taken :(')
                with open(f"failure{numurs}.html", 'w', encoding='utf-8') as f:
                    f.write(body)

    else:
        print("Login to CSDD failed. Try updating CSDDaccount.json file, exiting...")

while True:
    os.system("cls")
    option = input("\nSelect option:\n1 [Get CSDD user]\n2 [Launch script]\n>>> ")
    if option == '1':
        CookiesLoader.GetCSDDuser()
    elif option == '2':
        CSDD()
        break
    elif option == "3":
