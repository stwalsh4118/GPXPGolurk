import time
from PySimpleGUI.PySimpleGUI import Checkbox
import vlc
from threading import Thread
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import PySimpleGUI as sg
import random as rand
import json

#@ load accounts from accounts.json file
def loadAccounts(fileName):
    file = open(fileName)
    accounts = json.load(file)

    accountFix = []
    for acc in accounts["accounts"]:
        accountFix.append(acc)
    accounts = accountFix
    return accounts

#@ load egg data
def loadEggs(fileName):
    file = open(fileName)
    eggs = json.load(file)
    
    eggFix = {}
    for egg in eggs["eggs"]:
        eggFix = {**eggFix, **egg}
    eggs = eggFix
    
    return eggs

#@ end chromedriver
def endBot(driver):
    driver.quit()
    return

def getMouseCoordinates(event_string):
    
    if(event_string != "None"):
        x = event_string.split(" ")[2].split("=")[1]
        y = (event_string.split(" ")[3].split("=")[1])[:-1]
        coordinate_pair = (int(x),int(y))
    else:
        return "No coordinates available."
    
    return coordinate_pair


def parseEvent(events, accounts):
    
    #@ reads and interprets events from pysimplegui elements
    #@ events from elements are in the form:   "user (space) event"
    #@ other events triggered are keyboard events in the form: keycode (like Alt_L:18 for example)
    
    event = {}
    for acc in accounts:
        if(acc["user"] in events):
            event["user"] = acc["user"]
            event["event"] = events.split(" ")[1]
    if(not(event)):
        event = events
    return event

def parseValues(values, accounts):
    
    #@ reads and interprets values from pysimplegui elements
    #@ values from elements are in the form: "username elementType : value"
    #@ returns the parsed values in the form :
    #@
    #* username: {
    #*    elements: {
    #*        elementType : value
    #*    }
    #* }
    #@ 
    #@ with an additional entry that gives the currently focused tab in the form of:
    #* tab : username
    
    parsed_values = {}
    
    #@ loop through all accounts
    for acc in accounts:
        parsed_values[acc["user"]] = {
            "elements" : {}
        }
        #@ loop through every value output
        for key in values:
            
            #@ check if value is of the form "username elementType : value"
            if(not(isinstance(key, int))):
                if(acc["user"] in key):
                    parsed_values[acc["user"]]["elements"][key.split(" ")[1]] = values[key]
                    
            #@ assign which tab is currently focused
            elif(acc["user"] in values[key]):
                parsed_values["tab"] = acc["user"]
    
    return parsed_values

def createWindow(accounts):
    
    # [summary]
    #     #@ create window tab for each account 
    # Args:
    #    #@ accounts (list of accounts): accounts in form of:
    #    #*  {
    #    #*   "user": username,
    #    #*   "pw": password
    #    #*  }
    #    #*

    # Returns:
    #     #@ list (pysimplegui layout): returns tabs for each account
    
    names = ['Roberta', 'Kylie', 'Jenny', 'Helen',
        'Andrea', 'Meredith','Deborah','Pauline',
        'Belinda', 'Wendy']
    
    tabs = []
    for account in accounts:
       tab_building = []
       tab_building +=[
           sg.Text("Tab for " + account["user"] + "'s account")
       ],
       tab_building += [
            sg.Text("Mass Click Runs")
       ],
       tab_building += [
            sg.Multiline(
                   autoscroll=False, disabled=True, size=(40, 30), key=(account["user"] + " multiline")
               ),
            sg.Column([
                [sg.Text('Select Egg to Fill Party With')],
                [sg.Input(do_not_clear=True, size=(30,1),enable_events=True, key=(account["user"] + " searchinput"))],
                [sg.Listbox(loadEggs("eggs.json"), size=(30,20), select_mode = "LISTBOX_SELECT_MODE_SINGLE", enable_events=True, key=(account["user"] + " eggs"))],
                [sg.Text("Currently Selected Egg", font = ("Helvetica", 11, "underline"))],
                [sg.Text("", size=(30,1), key = (account["user"] + " selectedegg"))]
            ], vertical_alignment = 't')
       ],
       tab_building += [
            sg.Button(button_text="End Program"),
            sg.Text("Number of Runs"),
            sg.Spin(values=list(range(1, 100000)), initial_value=1, size=(5, 1), key=account["user"] + " spin"),
            sg.Checkbox(text="Pass Orb?", key=account["user"] + " passorb"),
            sg.Button(button_text="Click", key=account["user"] + " click"),
            sg.Button(button_text="End Action", key=account["user"] + " endaction"),
            sg.Button(button_text = "Fill Party", key=account["user"] + " fillparty")
       ],
       tabs += [
           sg.Tab(title = account["user"] + "'s tab", layout = tab_building)
       ],
    return tabs