# License

    UCU-LEDGER: a simple set of scripts to make using Ledger with UCU easier
    Copyright (C) 2016 Adam Fontenot

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
    
# What does it do?
    
One script connects to the [University Credit Union](https://ucu.org)
servers and downloads a CSV of transactions in a 
specified date range. The other script processes the CSV file to 
create a .dat file compatible with [Ledger](http://ledger-cli.org). 
The script is capable of replacing unhelpful descriptions in the CSV 
with more verbose ones. See replacements.txt for the format.
    
The scripts are written in a way that it should be easy to modify 
them to be compatible with other well-designed bank websites. This 
might make the scripts useful to a wider audience.

# Requirements

UCU-LEDGER requires Python 3 and Python-requests. You'll also 
need Ledger (ledger-cli on Github) for these scripts to be useful. 
    
# Usage
    
## ucu2csv.py usage:
        ucu2csv.py [-h] [--start date] [--end date] output.csv
        
        positional arguments:
          output.csv    the csv output file

        other arguments:
          -h, --help    show this help message and exit
          --start date  csv start date in ISO 8601 (YYYY-MM-DD)
          --end date    csv end date in ISO 8601 (YYYY-MM-DD) 
          
None of the arguments (except the output file) are required. 
If the start or end date are not provided, you will be prompted when 
running the script. 
        
Currently, the script will request your username and 
password. I will accept pull requests allowing them to be specified 
on the command line. The code currently doesn't handle security 
questions, but (I believe) these only appear when the server sees an 
IP address for the first time. I will add code for this next item I 
am prompted to enter security questions.
    
## csv2ledger.py usage:
        csv2ledger.py [-h] -a Account:Name [-r replacements.txt] input.csv

        positional arguments:
          input.csv             the CSV input file

        other arguments:
          -h, --help            show this help message and exit
          -a Account:Name, --account Account:Name
                                ledger account name (e.g. Assets:Checking)
          -r replacements.txt, --replace replacements.txt
                                file containing replacements for CSV descriptions
                                
The --account argument is required. This option will tell the 
script what account the CSV file is for. So if you're running the 
script on the CSV from your checking account, you'll want something 
like "Assets:Checking" here. The script will put this on the credit 
line when the transaction is a credit, and the debit line when the 
transaction is a debit. 
        
The --replace argument is not required. If provided, the 
script will try to open a text file at that location and use it to 
provide more useful transaction descriptions in the .dat file. The 
syntax of the replacements file is shown below.
        
The script will print the results to the terminal, much like 
Ledger itself. You can simply redirect the output to a file with 
./csv2ledger.py > output.dat.
        
If you wish to use the script independently of ucu2csv.py, 
you will need your CSV file in the following format:

    MM/DD/YYYY,"Transaction Type","Transaction Description",IGNORED,IGNORED,Amount

Negative amounts are considered debits from the account, positive 
amounts are debits to the account.
        
## replacements.txt usage:
The replacements file contains Python 2-tuples or 3-tuples, 
one per line. The first item in the tuple contains a simple text 
match (lower case). Any transaction with a description matching this 
line will have its description replaced by the second item in the 
tuple. 
        
 If a third item in the tuple is provided, it will provide a 
source account for the transaction to Ledger. So if the transaction 
is a credit, the source account will be the account the amount is 
debited from. And if the transaction is a debit, the source account 
is the account the amount if debited from. See the sample below.
        
        ("ralphs", "Ralphs", "Expenses:Groceries")
        ("wholefds", "Whole Foods", "Expenses:Groceries")
        ("amazon.com", "Amazon")
        ("ladwp", "LADWP - power bill", "Expenses:Utilities")
        ("apye", "Monthly Dividend Deposit", "Income:Dividends")
