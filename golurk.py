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

#@ end chromedriver
def endBot(driver):
    driver.quit()
    return


def parseEvent(events, accounts):
    
    #@ reads and interprets events from pysimplegui elements
    #@ events from elements are in the form: "user (space) event"
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
               )
       ],
       tab_building += [
            sg.Button(button_text="End Program"),
            sg.Text("Number of Runs"),
            sg.Spin(values=list(range(1, 100000)), initial_value=1, size=(5, 1), key=account["user"] + " spin"),
            sg.Checkbox(text="Pass Orb?", key=account["user"] + " passorb"),
            sg.Button(button_text="Click", key=account["user"] + " click"),
            sg.Button(button_text="End Click", key=account["user"] + " endclick")
       ],
       tabs += [
           sg.Tab(title = account["user"] + "'s tab", layout = tab_building)
       ],
    return tabs

class RunMaster:
      
    def __init__(self):
        self._running = True
      
    def terminate(self):
        self._running = False

    

    def run(self, driver, number, storage , numruns, passorb):
        
        #    [summary]
        #    Used as a target method for thread.
        #
        #    To be used in conjunction with threads in this manner:
        #
        #*    t = Thread(target = c.run, args =(driver, number, storage, numruns, passorb, ))
        #*    t.start()
        #    
        #    Args:
        #@    driver (Chrome webdriver): the driver of the Chrome application you are running
        #@    number (int: x < 300): number of pokemon to open in the berry feeder
        #@    storage (list): list object used to store data from click run
        #@    numruns (int x > 0): number of click runs to complete in a row
        #@    passorb (bool): if True selects "Iteract with players that have interacted with you that you haven't" to farm pass orbs
        
        for i in range(numruns):
            
            if(self._running):
                
                #@ selects from range percent of berries that *should* be correct
                percent_correct_berries = rand.randint(10,20)

                #@ navigates to users screen
                driver.find_element(By.LINK_TEXT, "Users").click()
                print(driver.current_url)
                time.sleep(1)

                #@ set number of pokemon/eggs to *300*
                if(driver.find_element(By.NAME, "number").get_attribute("value") != 300):
                    driver.find_element(By.NAME, "number").send_keys(Keys.DELETE + Keys.DELETE + Keys.DELETE + Keys.BACKSPACE + Keys.BACKSPACE + Keys.BACKSPACE + str(number))

                #@ set number of users to *1000*
                if(driver.find_element(By.XPATH,"//*[@id='usersCount']/span").text != "View 1000 users (who)"):
                    driver.find_element(By.ID, "usersCount").click()
                    time.sleep(.5)
                    actions = ActionChains(driver)
                    actions.send_keys(Keys.DOWN + Keys.DOWN + Keys.DOWN)
                    actions.perform()
                    time.sleep(.5)
                    actions.send_keys(Keys.ENTER)
                    actions.perform()

                #@ set users to pick from to *random(because all is being a bitch)*
                if(driver.find_element(By.XPATH, "//*[@id='usersList']/span") != "ordered randomly" and not(passorb)):
                    driver.find_element(By.XPATH, "//*[@id='usersList']").click()
                    time.sleep(.5)
                    ActionChains(driver).send_keys(Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN).perform()
                    time.sleep(.5)
                    ActionChains(driver).send_keys(Keys.ENTER).perform()
                    time.sleep(2)
                    
                #@ set users to pick from to *users that have interacted with me*
                elif(passorb):
                    driver.find_element(By.XPATH, "//*[@id='usersList']").click()
                    time.sleep(.5)
                    ActionChains(driver).send_keys(Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.UP + Keys.UP + Keys.UP + Keys.UP + Keys.UP + Keys.UP + Keys.UP + Keys.UP).perform()
                    time.sleep(.5)
                    ActionChains(driver).send_keys(Keys.ENTER).perform()
                    time.sleep(2)
                    
                #@ open berry feeder
                driver.find_element(By.XPATH, "//*[@id='usersOpen']/input[1]").click()



            i = 300
            proper_berry_amount = 0
            total_berry_amount = 0
            click = False
            
            #@ while loop that runs the clicking process
            while(i >= 0 and self._running):
                #@ get text to know what berry to click
                try:
                    #@ if feeder_UI is stale, skip this while step and try again until you can read the text
                    feeder_UI = driver.find_element(By.ID, "infoInteract")
                    feeder_info = feeder_UI.find_element(By.CSS_SELECTOR, "div")
                    feeder_info_text = feeder_info.text
                    click = True
                except:
                    click = False


                #@ click depending on which berry
                if(click):
                    berry_correctness = rand.randint(0,100)
                    if(berry_correctness < percent_correct_berries):
                        if("sour" in feeder_info_text):
                            actions = ActionChains(driver)
                            actions.send_keys("1")
                            actions.perform()
                            proper_berry_amount += 1
                        elif("spicy" in feeder_info_text):
                            actions = ActionChains(driver)
                            actions.send_keys("2")
                            actions.perform()
                            proper_berry_amount += 1
                        elif("dry" in feeder_info_text):
                            actions = ActionChains(driver)
                            actions.send_keys("3")
                            actions.perform()
                            proper_berry_amount += 1
                        elif("sweet" in feeder_info_text):
                            actions = ActionChains(driver)
                            actions.send_keys("4")
                            actions.perform()
                            proper_berry_amount += 1
                        elif("spicy" in feeder_info_text):
                            actions = ActionChains(driver)
                            actions.send_keys("5")
                            actions.perform()
                            proper_berry_amount += 1 
                            
                    #@ if not designated to be "correct" select random berry or if clicking egg/no correct choice pokemon 
                    else:
                        random_input = rand.randint(1,5)
                        actions = ActionChains(driver)
                        actions.send_keys(str(random_input))
                        actions.perform()
                        

                ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
                
                #@ get number of pokemon left in the run
                try:
                    num_pokemon_left = int((WebDriverWait(driver, 3,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, "//*[@id='infoFeederRemaining']/span"))).text.split())[0])
                    i = num_pokemon_left
                    total_berry_amount = number - num_pokemon_left
                except:
                    pass

                #@ if on user screen too long end run
                #@ (which probably means either the run broke, or you ran out of pokemon like in the case of pass orb farming)
                if("https://gpx.plus/users" in driver.current_url):
                    break
            
            print("Proper Berry Percent: ", str((proper_berry_amount/300)*100), "%")
            print("Proper Berries: ", str(proper_berry_amount))
            
            #@ store stats in mutable object that thread can interact with in a global scale
            storage.append([
                "    Total Berries: " + str(total_berry_amount),
                "    Theoretical Percent Correct Berries: " + str(percent_correct_berries),
                "    Num Proper Berries: " + str(proper_berry_amount),
                "    Real Num Correct Berries: " + str((proper_berry_amount/total_berry_amount)*100)
            ])


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
run_data_storages = []
for acc in accounts:
    run_data_storages.append({
        acc["user"] : []
    })

window = sg.Window("Demo", layout, return_keyboard_events=True, use_default_focus=False)

previous_run_storage_state = []
p = vlc.MediaPlayer("https://play.pokemonshowdown.com/audio/cries/wooloo.mp3")
p.audio_set_volume(50)
p.play()



QT_ENTER_KEY1 =  'special 16777220'
QT_ENTER_KEY2 =  'special 16777221'
passorb = False

RunMasters = []
threads = []
is_clicking = []


#@ Create an event loop
while True:
    event, values = window.read(timeout=1000, close=False)
    passorb = False
    print("event ", event, " values ", values ) 
    
    parsed_event = parseEvent(event, accounts)
    parsed_values = parseValues(values, accounts)
    print(parsed_values)
    
    
    ##@ End program if user closes window or presses the OK button
    if ("End Program" in parsed_event or parsed_event == sg.WIN_CLOSED):
        for user in drivers:
            endBot(drivers[user])
        break
    

    # #@ on clicking "Click" button do run
    # elif event == "Click":
    #    if(not(clicking)):
    #        if(values[1]):
    #            passorb = True
    #        RunMasters.append(RunMaster())
    #        threads.append(Thread(target = RunMasters[len(RunMasters) - 1].run, args =(driver, 300, run_data_storages, numRuns, passorb, )))
    #        threads[len(threads) - 1].start()
    #        is_clicking.append(True)
    
    ##@ on "ENTER" key input do run
    #elif(event in ('\r', QT_ENTER_KEY1, QT_ENTER_KEY2)):
    #    if(not(clicking)):
    #        if(values[1]):
    #            passorb = True
    #        RunMasters.append(RunMaster())
    #        threads.append(Thread(target=RunMasters[len(RunMasters) - 1].run, args=(driver, 300, run_data_storages, numRuns, passorb, )))
    #        threads[len(threads) - 1].start()
    #        is_clicking.append(True)
    #
    ##@ on clicking "End Click" button end run on thread        
    #elif event == "End Click":
    #    for i in range(0, len(RunMasters)):
    #        RunMasters[i].terminate()
    #    RunMasters.clear()
    #    threads.clear()
    #    is_clicking.clear()
    #   driver.get("https://gpx.plus/users/random/1")
    #   p = vlc.MediaPlayer("https://play.pokemonshowdown.com/audio/cries/wooloo.mp3")
    #    p.audio_set_volume(50)
    #    p.play()
    #   
    ##@ if a thread is not alive (which means it died for some reason without my intervention) play sound and reset
    #i = 0
    #for thread in threads:
    #   if(not(thread.is_alive()) and is_clicking[i]):
    #        p = vlc.MediaPlayer("https://play.pokemonshowdown.com/audio/cries/wooloo.mp3")
    #        p.audio_set_volume(50)
    #        p.play()
    #        threads.pop(i)
    #        is_clicking.pop(i)
    #        RunMasters.pop(i)
    #    i += 1
    #    
    #    
    #run_data_storages = []
    #runNum = 1
    #
    ##@ form stats list in "storage" in string that can be used by multiline element
    # for run in run_data_storages:
    #    run_data_storages.insert(0,"Num Run: " + str(runNum))
    #    runNum += 1
    #    index = 1
    #    for stat in run:
    #        run_data_storages.insert(index,stat)
    #        index += 1
    
    # if(previous_run_storage_state != run_data_storages):
    #    window["-RUN LIST-"].update(value = '\n'.join(run_data_storages))
    # previous_run_storage_state = run_data_storages

window.close()
