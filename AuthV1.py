#title: Charles Schwab API Authentication
#author: Luke Halla
#date: 8/27/2024

import requests  #http requests
import arrow  #better time management
import base64  #http request
from re import search  #string manipulation
from playsound import playsound # Access token notification

pst_time = arrow.now('US/Pacific')
#Assign keys
pw = {
    'appkey': 'REDACTED',
    'secret': 'REDACTED'
}

config = {'redirect_url': 'https://127.0.0.1', # localhost
          'cs_code': '',
          'accessT': '',
          'refreshT': '',
          'accessT_exp': arrow.now('US/Pacific'),
          }


def cs_login_auth(appkey, redirect_url):
    print('Click and login:')
    print('https://api.schwabapi.com/v1/oauth/authorize?client_id=' + appkey + '&redirect_uri=' + redirect_url)

    print("paste full code URL")
    respURL = input()

    match = search(r"code=([^%]+)%40", respURL)  #Extracting code between code= and %40
    if match:
        cs_code = match.group(1)
        cs_code = cs_code + "@" # instead of URL decoding
        config['cs_code'] = cs_code
    else:
        print("Error. Code not found.")


def generate_tokens(appkey, secret, cs_code, redirect_url):
    combined_credentials = f'{appkey}:{secret}'

    # Base64 encode the combined credentials
    encoded_credentials = base64.b64encode(combined_credentials.encode("utf-8")).decode('utf-8')

    # URL for the POST request
    url = 'https://api.schwabapi.com/v1/oauth/token'
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Data to send in the request
    data = {
        'grant_type': 'authorization_code',
        'code': cs_code,
        'redirect_uri': redirect_url
    }

    # Send the POST request
    try:
        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            # Parse JSON response
            response_json = response.json()

            # Extract values from the response
            config['accessT'] = response_json.get('access_token', 'N/A') # needs refresh every 30 min
            config['refreshT'] = response_json.get('refresh_token', 'N/A') # needs refresh every 7 days

            # Extract timestamp or use current time if timestamp not provided
            current_time = arrow.now('US/Pacific')
            config['accessT_exp'] = current_time.shift(minutes=15)  # 25 minutes from response time

        else:
            print(f"Request failed with status code {response.status_code}.")
            print(f"Response: {response.text}")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


def checkAccessToken(appkey, secret, refreshT, accessT_exp, redirect_url):

    current_time = arrow.now('US/Pacific')

    # Check if the current time is past the threshold for the access token
    if current_time >= accessT_exp:
        getNewAccTkn = True
        print('**Generating New Access Token**')
    else:
        getNewAccTkn = False
        print('**Access Token Valid**')

    #Getting new access token if time is close to expiration
    if getNewAccTkn:

        combined_credentials = f'{appkey}:{secret}'
        # Base64 encode the combined credentials
        encoded_credentials = base64.b64encode(combined_credentials.encode("utf-8")).decode('utf-8')

        url = 'https://api.schwabapi.com/v1/oauth/token'
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Data to send in the request
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refreshT,
            'redirect_uri': redirect_url
        }
        try:
            response = requests.post(url, headers=headers, data=data)

            if response.status_code == 200:
                # Parse JSON response
                response_json = response.json()  # Assign the response JSON to a variable
                print(response_json)  # Print the content of the JSON

                current_time = arrow.now('US/Pacific')

                # Extract values from the response
                config['accessT'] = response_json.get('access_token', 'N/A')

                # Calculate expiration times
                config['accessT_exp'] = current_time.shift(minutes=15)  # 15 minutes from response time

                print("Access Token Successfully Generated")
                playsound("./noti.mp3")

            else:
                print(f"Request failed with status code {response.status_code}.")
                print(f"Response: {response.text}")
                playsound("./error.mp3")

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")

#cs_login_auth(pw['appkey'], config['redirect_url'])
#generate_tokens(pw['appkey'], pw['secret'], config['cs_code'], config['redirect_url'])
#checkAccessToken(pw['appkey'], pw['secret'], config['refreshT'], config['accessT_exp'], config['redirect_url'])
