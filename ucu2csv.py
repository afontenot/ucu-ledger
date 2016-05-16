#!/usr/bin/env python

import argparse
import getpass
import re
import requests

from datetime import date, datetime

# login POST url
auth_url = "https://secure.ucu.org/hb/login"

# login POST request data
user_post = "account"
pw_post = "pin"

# script uses auth cookies to pull this url and grep for account
# suffix and names to show user
suffix_url = "https://secure.ucu.org/hb/suffixes"
suffix_pattern = "suffixes/(\d+)/transactions\">(\w+)"

# the url we send a GET request to; payload is urlencoded and sent with it
# we run .format on the string to add the suffix to it
csv_url = "https://secure.ucu.org/hb/suffixes/{}/transactions"

# a dict of params that are urlencoded and sent to request csv file
csv_payload = {"utf8": "✓", "start_draft": "", "end_draft": "", 
        "transaction_type": "0", "order": "0", "format": "csv"}

# these three params are added to csv_payload with the correct values
csv_payload_suffix = "suffix"
csv_payload_sdate = "start_date"
csv_payload_edate = "end_date"

# strftime date format used for csv_payload_sdate and csv_payload_edate
date_format = "%m/%d/%Y"

# utils to validate user input
def get_date(name, date_format):
    while True:
        try:
            d = input("Input {} date in YYYY-MM-DD format: ".format(name))
            d = datetime.strptime(d, "%Y-%m-%d")
            d = d.strftime(date_format)
            return d
        except KeyboardInterrupt:
            raise SystemExit()
        except:
            print("Date format not valid! Ctrl-c to exit.")
            pass

def get_int(request, maxnum):
    while True:
        try:
            num = int(input(request))
            assert(0 <= num and num < maxnum)
            return num
        except KeyboardInterrupt:
            raise SystemExit()
        except:
            print("Date format not valid! Ctrl-c to exit.")
            pass

# argparse stuff
parser = argparse.ArgumentParser(description="A CSV fetcher for simple auth'd bank accounts")
parser.add_argument('csvfile', help='the csv output file', metavar='output.csv')
parser.add_argument('--start', nargs=1, metavar='date', 
        help='csv start date in ISO 8601 (YYYY-MM-DD)', 
        type=lambda s: datetime.strptime(s, '%Y-%m-%d'))
parser.add_argument('--end', nargs=1, metavar='date', 
        help='csv end date in ISO 8601 (YYYY-MM-DD)', 
        type=lambda s: datetime.strptime(s, '%Y-%m-%d'))
args = parser.parse_args()

# get user's data, make a dict to send with auth request
user = getpass.getpass("Username: ")
pw = getpass.getpass()
auth_data = {user_post: user, pw_post: pw}

# send auth request, use cookies to get the suffix url and find matches
# block redirects so we can get the cookies from the response
auth = requests.post(auth_url, data = auth_data, allow_redirects = False)
if auth.status_code == 200: # user / password not correct
    raise SystemExit("Login unsuccessful!")
suffixes_raw = requests.get(suffix_url, cookies = auth.cookies).text
suffixes_matches = re.findall(suffix_pattern, suffixes_raw)

# print a list of accounts to the user
print("\nAccounts:")
for match in suffixes_matches:
    print(str(suffixes_matches.index(match)) + ":", match[1], 
            "(" + str(match[0]) + ")")

# request an index and a date range
index = get_int("Choose account by index: ", len(suffixes_matches))
suffix = suffixes_matches[index][0]
if args.start:
    start_date = args.start[0].strftime(date_format)
else:
    start_date = get_date("start", date_format)
if args.end:
    end_date = args.end[0].strftime(date_format)
else:
    end_date = get_date("end", date_format)

# add params to the payload
csv_payload[csv_payload_suffix] = suffix
csv_payload[csv_payload_sdate] = start_date
csv_payload[csv_payload_edate] = end_date

# get the csv, write it to a file
csv_url = csv_url.format(suffix)
csv = requests.get(csv_url, params = csv_payload, cookies = auth.cookies)

with open(args.csvfile, 'w') as f:
    f.write(csv.text)
