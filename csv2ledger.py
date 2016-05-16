#!/usr/bin/python3

import argparse
import ast
import csv
import datetime
import os
import sys

# argparse stuff
parser = argparse.ArgumentParser(description="A simple script to convert UCU CSVs to Ledger .dat files")
parser.add_argument('input', nargs=1, metavar='input.csv',
        help='the CSV input file')
parser.add_argument('-a', '--account', nargs=1, metavar='Account:Name',
        help='ledger account name (e.g. Assets:Checking)', required=True)
parser.add_argument('-r', '--replace', nargs=1, metavar='replacements.txt',
        help='file containing replacements for CSV descriptions (see documentation)')
args = parser.parse_args()

if not os.path.exists(args.input[0]):
    sys.exit('ERROR: CSV file {} not found!'.format(args.input))

DEBIT = args.account[0]

# define list of replacements for auto-sort
replacements = []

if args.replace:
    if not os.path.exists(args.replace[0]):
        sys.exit('ERROR: replacements file {} not found!'.format(args.replace[0]))
    with open(args.replace[0], 'r') as repfile:
        for line in repfile:
            replacements.append(ast.literal_eval(line))

# printdic contains output lines with a ISO date key for sorting
printdic = {}

with open(args.input[0], newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    
    # skip header
    next(reader)

    # sometimes we have >1 transaction in a day, so we give
    # each transaction a number to keep them in order
    itemcounter = 99999999

    for row in reader:
        # 0 = purchase, 1 = deposit, 2 = transfer
        entry_type = 0

        ucu_date = row[0].split('/')
        ucu_date = [int(item) for item in ucu_date]
        date = datetime.date(ucu_date[2], ucu_date[0], ucu_date[1])
        isodate = date.isoformat()

        ucu_desc = row[2].lower()
        desc = ""
        account = ""
        for rep in replacements:
            if rep[0] in ucu_desc:
                desc = rep[1]
                if len(rep) == 2:
                    continue
                account = rep[2]

        # ucu_desc usually doesn't get filled from the check desc form
        # blame the tellers for not filling it in
        if ucu_desc == "":
            if "check" in row[1].lower():
                desc = "Check payment"
            elif "withdrawal" in row[1].lower():
                desc = "Cash withdrawal"
            elif "deposit" in row[1].lower():
                desc = "Check deposit"
        # for now, we're printing everything, so use any desc we have
        if desc == "":
            desc = ucu_desc
        if account == "":
            account = "ACCOUNT"

        amount = float(row[5])
        credit = True
        if amount < 0:
            credit = False
            amount = -1 * amount
        # handle comments, holds etc
        if amount < 0.01:
            continue

        output = isodate.replace('-','/') + " " + desc + "\n"

        # format amount to 2 decimals and add $ sign
        amount = "${:.2f}".format(amount)

        if credit:
            # use .format to allot 41 spaces to date and account, 10 to amount
            output += "{:<41} {:>10}\n".format("    " + DEBIT, amount)
            output += "    " + account + "\n"
        else:
            output += "{:<41} {:>10}\n".format("    " + account, amount)
            output += "    " + DEBIT + "\n"

        itemcounter -= 1
        printdic[isodate + str(itemcounter)] = output

for transaction in sorted(printdic.values()):
    print(transaction)
