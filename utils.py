import requests
from distutils.dir_util import copy_tree

from config import TELEGRAM, ENV, TESTING_PRODUCTION
import json
import os
import telegram_send

def print_trade_analysis(analyzer):
    # Get the results we are interested in
    if not analyzer.get("total"):
        return

    total_open = analyzer.total.open
    total_closed = analyzer.total.closed
    total_won = analyzer.won.total
    total_lost = analyzer.lost.total
    win_streak = analyzer.streak.won.longest
    lose_streak = analyzer.streak.lost.longest
    pnl_net = round(analyzer.pnl.net.total, 2)
    strike_rate = round((total_won / total_closed) * 2)

    # Designate the rows
    h1 = ['Total Open', 'Total Closed', 'Total Won', 'Total Lost']
    h2 = ['Strike Rate', 'Win Streak', 'Losing Streak', 'PnL Net']
    r1 = [total_open, total_closed, total_won, total_lost]
    r2 = [strike_rate, win_streak, lose_streak, pnl_net]

    # Check which set of headers is the longest.
    if len(h1) > len(h2):
        header_length = len(h1)
    else:
        header_length = len(h2)

    # Print the rows
    print_list = [h1, r1, h2, r2]
    row_format = "{:<15}" * (header_length + 1)
    print("Trade Analysis Results:")
    for row in print_list:
        print(row_format.format('', *row))

def createJsonFile(data):
    '''
    data = {}
    data['people'] = []
    data['people'].append({
        'name': 'Scott',
        'website': 'stackabuse.com',
        'from': 'Nebraska'
    })
    data['people'].append({
        'name': 'Larry',
        'website': 'google.com',
        'from': 'Michigan'
    })
    data['people'].append({
        'name': 'Tim',
        'website': 'apple.com',
        'from': 'Alabama'
    })
    '''

    #with open('data.json', 'w') as outfile:
    #    json.dump(data, outfile)
    start = "var text = \'"
    end = "\';"
    f = open("./UI/1.0/data.js", "w")
    #TODO cambiar cuando este finalizada 1.0 de javascript!
    #f = open("./sessions/template/data.js", "w")
    f.write(start + json.dumps(data) + end)
    f.close()

def print_sqn(analyzer):
    sqn = round(analyzer.sqn, 2)
    print('SQN: {}'.format(sqn))


def send_telegram_message(message="", force=False):
    if ENV != "production":
        return
    elif TESTING_PRODUCTION == False or force == True:
        telegram_send.send(messages=[message])
    return True
    #base_url = "https://api.telegram.org/bot%s" % TELEGRAM.get("bot")
    #print(base_url)
    #return requests.get("%s/sendMessage" % base_url, params={
    #    'chat_id': TELEGRAM.get("channel"),
    #    'text': message
    #}).content

def copy_UI_template():
    '''
        copia el template de UI para mostrar graficos 
    '''
    # copy subdirectory example
    fromDirectory = "./UI/1.0"
    toDirectory = "./sessions/template"

    path = "./sessions/template"
    try:
        os.makedirs(path)
    except OSError:
        print ("Creation of the directory %s failed" % path)
    else:
        print ("Successfully created the directory %s" % path)

    copy_tree(fromDirectory, toDirectory)
    print("Copy Ready")