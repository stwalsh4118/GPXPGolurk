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
from RunMaster import RunMaster
from helper import *




#@ Initialize chromedrivers

accounts = loadAccounts("accounts.json")

path_to_extension = r'C:\Users\Seanw\OneDrive\Documents\gpx\1.34.0_0'

chrome_options = Options()
chrome_options.add_argument('load-extension=' + path_to_extension)

drivers = {}
for acc in accounts:
    drivers[acc["user"]] = Chrome(executable_path='./chromedriver', chrome_options=chrome_options)

for user in drivers:
    drivers[user].create_options()


account_index = 0
for user in drivers:
    #go to website
    drivers[user].get("https://gpx.plus/")

    #input username and password and login
    drivers[user].find_element(By.NAME, "email").send_keys(accounts[account_index]["user"])
    drivers[user].find_element(By.NAME, "password").send_keys(accounts[account_index]["pw"] + Keys.ENTER)
    account_index += 1




#@ initialize gui window

layout = [
    [
        sg.TabGroup(createWindow(accounts))
    ]
]

#@ initialize data storage
run_data_storages = {}
previous_run_storage_state = {}
runs_completed = {}
for acc in accounts:
    run_data_storages[acc["user"]] = []
    previous_run_storage_state[acc["user"]] = []
    runs_completed[acc["user"]] = 0

window = sg.Window("Golurk", layout, return_keyboard_events=True, use_default_focus=False, finalize=True)


p = vlc.MediaPlayer("https://play.pokemonshowdown.com/audio/cries/wooloo.mp3")
p.audio_set_volume(50)
p.play()



QT_ENTER_KEY1 =  'special 16777220'
QT_ENTER_KEY2 =  'special 16777221'
passorb = False

RunMasters = {}
threads = {}
is_thread_active = {}
currently_selected_egg = {}


window.bind('<Motion>', "???")
names = ['Roberta', 'Kylie', 'Jenny', 'Helen','Andrea', 'Meredith','Deborah','Pauline','Belinda', 'Wendy']

#@ pysimplegui event loop
while True:
    event, values = window.read(timeout=1000, close=False)
    passorb = False
    #print("event ", event, " values ", values ) 
    #print(event)
    parsed_event = parseEvent(event, accounts)
    #print(parsed_event)
    parsed_values = parseValues(values, accounts)
    focused_tab = parsed_values["tab"]
    #print(parsed_values)
    #print(is_thread_active)


    #TODO: ADD CHECKBOX FOR FULLRANDOM CLICKING MODE, ALSO NEED TO ADD PERCENT RANGE INPUT FOR THE NON-RANDOM MODE
    #TODO: PROBABLY NEED TO REWORK INPUT CONFIGURATIONS FOR ROUTINE METHODS INTO A CONFIGURATION OBJECT SO THERES NOT INFINITE PARAMS
    #TODO: ^GONNA DRAG MY FEET ON THIS THOUGH UNTIL ITS TOO LATE AND IM MAD AT MYSELF LMAO
    #IDEA: ALSO PER USER CONFIGURATION SAVING WOULD BE NICE, AND SAVED TO FILE/DB WOULD BE COOL SO LAST USED CONFIG WILL LOAD ON PROGRAM START
    #TODO: NEED TO CHECK FOR PLUS POWERS AND CHANGE ROUTINE TO FIT IF A PLUS POWER IS ACTIVE, FOR EXAMPLE AUTO RELEASING IF RELEASE POWER IS ON, ETC...
    #TODO: PLUS POWERS TO IMPLEMENT:
    #TODO:          HATCH (HATCH RIGHT AFTER FULL MATURITY)(ADD CHECK FOR IF HATCH BUTTON IS DISABLED)
    #TODO:          RELEASE (ABLE TO RELEASE RIGHT AFTER HATCHING)(AUTO RELEASE INSTEAD OF PUTTING INTO PC)
    #TODO:                  (PROBABLY SHOULD WAIT UNTIL I SEE THAT SHINY DETECTION AND MOVING SHINY TO PROTECTED PC WORKS)
    #TODO:          HONEY (ABLE FILL SHELTER SCREEN WITH EGGS YOURE LOOKING FOR) (PROBABLY NOT NECESSARY SINCE EGGS ARE FOUND AUTOMATICALLY ANYWAY)
    
    
    #@ filter egg names
    if(parsed_values[focused_tab]["elements"]["searchinput"] != ""):
        search = parsed_values[focused_tab]["elements"]["searchinput"]
        new_values = [x for x in loadEggs("eggs.json")[0] if search in x]
        window.Element(focused_tab + " eggs").Update(new_values)
    else:
        window.Element(focused_tab + " eggs").Update([x for x in loadEggs("eggs.json")])
        
    #print(parsed_values)
    
    #@ display currently selected egg to fill party with
    
    if(parsed_values[focused_tab]["elements"]["eggs"] != []):
        currently_selected_egg[focused_tab] = parsed_values[focused_tab]["elements"]["eggs"][0]
        window.Element(focused_tab + " selectedegg").Update(currently_selected_egg[focused_tab])
    
    #@ End program if user closes window or presses the OK button
    if ("End Program" in parsed_event or parsed_event == sg.WIN_CLOSED):
        for user in drivers:
            if(user in RunMasters): 
                RunMasters[user].terminate()
            endBot(drivers[user])
        break
    
    #@ on "ENTER" key input do run
    elif(event in ('\r', QT_ENTER_KEY1, QT_ENTER_KEY2)):
        username_to_run = parsed_values["tab"]
        if(not(username_to_run in is_thread_active)):
            is_thread_active[username_to_run] = True
            RunMasters[username_to_run] = RunMaster()
            
            threads[username_to_run] = Thread(
                target = RunMasters[username_to_run].clickRun,
                args =(drivers[username_to_run],
                        username_to_run,
                        300,
                        run_data_storages,
                        runs_completed,
                        parsed_values[username_to_run]["elements"]["spin"],
                        parsed_values[username_to_run]["elements"]["passorb"],
                        True,
                        currently_selected_egg[username_to_run],    
                    )
                )
            
            threads[username_to_run].start()
                
        elif(not(is_thread_active[username_to_run])):
            is_thread_active[username_to_run] = True
            RunMasters[username_to_run] = RunMaster()
            
            threads[username_to_run] = Thread(
                target = RunMasters[username_to_run].clickRun,
                args =(drivers[username_to_run],
                        username_to_run,
                        300,
                        run_data_storages,
                        runs_completed,
                        parsed_values[username_to_run]["elements"]["spin"],
                        parsed_values[username_to_run]["elements"]["passorb"],
                        True,
                        currently_selected_egg[username_to_run],)
                )
            threads[username_to_run].start()
    
    
    
    if(isinstance(parsed_event, dict)):
        
    #@ on clicking "Click" button do run
        if (parsed_event["event"] == "click"):
            
            username_to_run = parsed_event["user"]
            if(not(username_to_run in is_thread_active)):
                is_thread_active[username_to_run] = True
                RunMasters[username_to_run] = RunMaster()
                
                threads[username_to_run] = Thread(
                    target = RunMasters[username_to_run].clickRun,
                    args =(drivers[username_to_run],
                           username_to_run,
                           300,
                           run_data_storages,
                           runs_completed,
                           parsed_values[username_to_run]["elements"]["spin"],
                           parsed_values[username_to_run]["elements"]["passorb"],
                           True,
                           currently_selected_egg[username_to_run],)
                    )
                
                threads[username_to_run].start()
                
            elif(not(is_thread_active[username_to_run])):
                is_thread_active[username_to_run] = True
                RunMasters[username_to_run] = RunMaster()
                
                threads[username_to_run] = Thread(
                    target = RunMasters[username_to_run].clickRun,
                    args =(drivers[username_to_run],
                           username_to_run,
                           300,
                           run_data_storages,
                           runs_completed,
                           parsed_values[username_to_run]["elements"]["spin"],
                           parsed_values[username_to_run]["elements"]["passorb"],
                           True,
                           currently_selected_egg[username_to_run],)
                    )
                threads[username_to_run].start()
                
        #@ end action when endaction button is clicked
        elif(parsed_event["event"] == "endaction"):
            
            username_to_end = parsed_event["user"]
            RunMasters[username_to_end].terminate()
            is_thread_active[username_to_end] = False
            drivers[username_to_end].get("https://gpx.plus/main")
            p = vlc.MediaPlayer("https://play.pokemonshowdown.com/audio/cries/wooloo.mp3")
            p.audio_set_volume(50)
            p.play()
        
        #@ run fillparty routine if button is clicked and egg is selected    
        elif(parsed_event["event"] == "fillparty" and (focused_tab in currently_selected_egg)):
            username_to_run = parsed_event["user"]
            if(not(username_to_run in is_thread_active)):
                is_thread_active[username_to_run] = True
                RunMasters[username_to_run] = RunMaster()
                
                threads[username_to_run] = Thread(
                    target = RunMasters[username_to_run].fillEggs,
                    args =(drivers[username_to_run],
                           username_to_run,
                           currently_selected_egg[focused_tab])
                    )
                
                threads[username_to_run].start()
                
            elif(not(is_thread_active[username_to_run]) and (focused_tab in currently_selected_egg)):
                is_thread_active[username_to_run] = True
                RunMasters[username_to_run] = RunMaster()
                
                threads[username_to_run] = Thread(
                    target = RunMasters[username_to_run].fillEggs,
                    args =(drivers[username_to_run],
                           username_to_run,
                           currently_selected_egg[focused_tab])
                    )
                threads[username_to_run].start()
            

    #@ if a thread is not alive (which means it died for some reason without my intervention) go to main page, play sound, and reset
    for user in threads:
        if(not(threads[user].is_alive()) and is_thread_active[user]):
            drivers[user].get("https://gpx.plus/main")
            is_thread_active[user] = False
            p = vlc.MediaPlayer("https://play.pokemonshowdown.com/audio/cries/wooloo.mp3")
            p.audio_set_volume(50)
            p.play()
    
    #@ form stats list in "run_data_storage" in string that can be used by each users multiline element
    for user in run_data_storages:
        
        run_output = []
        run_amount = 1
        for run in run_data_storages[user]:
            
            run_output.insert(0,"Num Run: " + str(run_amount))
            index = 1
            run_amount += 1
            for stat in run:
                run_output.insert(index,stat)
                index += 1
        if(previous_run_storage_state[user] != run_data_storages[user]):
            print("printing to multiline")
            window[user + " multiline"].update(value = '\n'.join(run_output))
            previous_run_storage_state[user] = run_data_storages[user].copy()



window.close()
