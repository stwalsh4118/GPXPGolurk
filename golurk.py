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


    

    #@ filter egg names
    if(parsed_values[focused_tab]["elements"]["searchinput"] != ""):
        search = parsed_values[focused_tab]["elements"]["searchinput"]
        new_values = [x for x in loadEggs("eggs.json")[0] if search in x]
        window.Element(focused_tab + " eggs").Update(new_values)
    else:
        window.Element(focused_tab + " eggs").Update([x for x in loadEggs("eggs.json")[0]])
        
    print(parsed_values)
    
        #@ End program if user closes window or presses the OK button
    if ("End Program" in parsed_event or parsed_event == sg.WIN_CLOSED):
        for user in drivers:
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
                        parsed_values[username_to_run]["elements"]["passorb"],)
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
                        parsed_values[username_to_run]["elements"]["passorb"],)
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
                           parsed_values[username_to_run]["elements"]["passorb"],)
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
                           parsed_values[username_to_run]["elements"]["passorb"],)
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
            
        elif(parsed_event["event"] == "fillparty"):
            username_to_run = parsed_event["user"]
            pokemon_name = "Wooloo"
            if(not(username_to_run in is_thread_active)):
                is_thread_active[username_to_run] = True
                RunMasters[username_to_run] = RunMaster()
                
                threads[username_to_run] = Thread(
                    target = RunMasters[username_to_run].fillEggs,
                    args =(drivers[username_to_run],
                           username_to_run,
                           pokemon_name)
                    )
                
                threads[username_to_run].start()
                
            elif(not(is_thread_active[username_to_run])):
                is_thread_active[username_to_run] = True
                RunMasters[username_to_run] = RunMaster()
                
                threads[username_to_run] = Thread(
                    target = RunMasters[username_to_run].fillEggs,
                    args =(drivers[username_to_run],
                           username_to_run,
                           pokemon_name)
                    )
                threads[username_to_run].start()
            

    #@ if a thread is not alive (which means it died for some reason without my intervention) play sound and reset
    for user in threads:
        if(not(threads[user].is_alive()) and is_thread_active[user]):
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
