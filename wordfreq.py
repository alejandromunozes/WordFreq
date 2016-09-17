#!/usr/bin/env python3


#© 2016 Alejandro Muñoz Fernández

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

### What's this script for?

# This script stores all the words (and their absolute frequencies, that is, how many times each word is in the given files) of the given xml, html or txt files and store them in a sqlite database (wordfreq.db)

### How to use

# wordfreq file1.xml file2.html file3.txt file(n).(xml|html|txt)

import sys

from bs4 import BeautifulSoup
from lxml.html.clean import Cleaner
import re
import sqlite3


def cleantext(text):
    '''
    Strip out all html and xml labels and numbers (if any) and gives a list with all the words.
    '''

    # First clean
    
    soup = BeautifulSoup(text,"lxml")
    
    for s in soup('script'):
        s.extract()
    
    text = soup.get_text(separator=" ")
    
    # Second clean

    cleaner = Cleaner(allow_tags=[''], remove_unknown_tags=False)
    text = cleaner.clean_html(text)
    
    # Third clean. Yes, I'm very paranoid
    
    text = re.sub('<[^>]*>', ' ', text)
    
    # Delete numbers
    text = ''.join(filter(lambda x: not x.isdigit(), text))
    
    # Delete spaces and puntuation and converts to lowercase
    
    cleanpunct = re.compile('\W+')
    text = cleanpunct.sub(' ', text).strip().lower()
    
    # List of words
    wordlist = text.split()

    return wordlist


def textdict(wordlist):
    '''
    Dictionary of word counts
    '''
    worddict = dict()
    for word in wordlist:
        worddict[word] = worddict.get(word,0) + 1
    return worddict


def intodb(worddict):
    '''
    Store all the words in all the files into a 'wordfreq.db' sqlite3 database
    '''
    # Creates the database (if it doens't exsist already) and connects to it
    conn = sqlite3.connect('wordfreq.db')
    cur = conn.cursor()
    
    # Creates the table if it doesn't exist already
    
    cur.execute('''CREATE TABLE IF NOT EXISTS forms (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    form TEXT UNIQUE NOT NULL,
    frequency INTEGER NOT NULL);''')
    
    # Checks if the word is already in the forms table. If so, it sums up the value in de worddict dictionary to the frecuency in the database.
    
    for key,value in worddict.items():
        cur.execute('SELECT * FROM forms WHERE form = ?', (key,))
        data = cur.fetchall()
        if len(data) == 0:
            cur.execute('INSERT INTO forms (form, frequency) VALUES (?, ?)', (key, value,))
        else:
            new_frequency = data[0][2] + value
            form_id = data[0][0]
            cur.execute('UPDATE forms SET frequency = ? WHERE id = ?', (new_frequency,form_id,))
            #conn.commit() # This transaction may be slower, but safer
        
    
    # Saves all changes

    conn.commit()

    # Closes conexión

    conn.close()

if len(sys.argv) < 2:
    print('Usage:')
    print('python3 wordfreq.py file1 file2...')
    print('The input files must be xml, html or txt.')
    print('You need Python 3 to run this script.')

else:   
    try:
        for arg in sys.argv[1:]:
            filehandler = open(arg, encoding='utf-8')
            text = filehandler.read()
            tlist = cleantext(text)
            tdict = textdict(tlist)
            intodb(tdict)
        print('The word frequency database ("wordfreq.db") is ready.')
    except:
        print('Usage:')
        print('python3 wordfreq.py file1 file2...')
        print('The input files must be xml, html or txt.')
        print('You need Python 3 to run this script.')
