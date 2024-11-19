from selenium import webdriver
import json

options = webdriver.FirefoxOptions()
options.set_preference("detach", True)
driver = webdriver.Firefox(options=options)

def ParseCookies(cookies):
    out = {}
    for item in cookies:
        key = item['name']
        value = item['value']
        out[key] = value
    return out

def SaveAccount(cookies):
    FileName = 'CSDDaccount'
    with open(f'{FileName}.json', 'w') as f:
        json.dump(cookies, f, indent=4)
        f.close()
    print(f"File [{FileName}.json] has been created successfully")

def GetCSDDuser():
    driver.get("http://e.csdd.lv")
    input("Press enter when you have logged into your CSDD account > ")
    CSDDACCOUNT = ParseCookies(driver.get_cookies())
    SaveAccount(CSDDACCOUNT)



def OpenAccount():
    driver.get("http://e.csdd.lv")
    with open('CSDDaccount.json', 'r') as file:
        cookies = json.load(file)

    for key, value in cookies.items():
        driver.add_cookie({"name": key, "value": value})
    driver.get("http://e.csdd.lv")



if __name__ == '__main__':
    OpenAccount()
