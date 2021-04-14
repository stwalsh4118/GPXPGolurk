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







path_to_extension = r'C:\Users\Seanw\OneDrive\Documents\gpx\1.34.0_0'

chrome_options = Options()
chrome_options.add_argument('load-extension=' + path_to_extension)

driver = Chrome(executable_path='./chromedriver', chrome_options=chrome_options)
driver.implicitly_wait(3)

driver.create_options()


#go to website
driver.get("https://gpx.plus/")



def loadAccounts(fileName):
    file = open(fileName)
    accounts = json.load(file)

    accountFix = []
    for acc in accounts["accounts"]:
        accountFix.append(acc)
    accounts = accountFix
    return accounts

accounts = loadAccounts("accounts.json")

#input username and password and login
driver.find_element(By.NAME, "email").send_keys(accounts[0]["user"])
driver.find_element(By.NAME, "password").send_keys(accounts[0]["pw"] + Keys.ENTER)


def endBot(driver):
    driver.quit()
    return


class RunMaster:
      
    def __init__(self):
        self._running = True
      
    def terminate(self):
        self._running = False

        #    [summary]
        #    Used as a target method for thread.
        #
        #    To be used in conjunction with threads in this manner:
        #
        #*    t = Thread(target = c.run, args =(driver, number, storage, numruns, passOrb, ))
        #*    t.start()
        #    
        #    Args:
        #@    driver (Chrome webdriver): the driver of the Chrome application you are running
        #@    number (int: x < 300): number of pokemon to open in the berry feeder
        #@    storage (list): list object used to store data from click run
        #@    numruns (int x > 0): number of click runs to complete in a row
        #@    passOrb (bool): if True selects "Iteract with players that have interacted with you that you haven't" to farm pass orbs

    def run(self, driver, number, storage , numruns, passOrb):
        
        for i in range(numruns):
            
            if(self._running):
                
                #@ selects from range percent of berries that *should* be correct
                percentCorrectBerries = rand.randint(10,20)

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
                if(driver.find_element(By.XPATH, "//*[@id='usersList']/span") != "ordered randomly" and not(passOrb)):
                    driver.find_element(By.XPATH, "//*[@id='usersList']").click()
                    time.sleep(.5)
                    ActionChains(driver).send_keys(Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN).perform()
                    time.sleep(.5)
                    ActionChains(driver).send_keys(Keys.ENTER).perform()
                    time.sleep(2)
                    
                #@ set users to pick from to *users that have interacted with me*
                elif(passOrb):
                    driver.find_element(By.XPATH, "//*[@id='usersList']").click()
                    time.sleep(.5)
                    ActionChains(driver).send_keys(Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.UP + Keys.UP + Keys.UP + Keys.UP + Keys.UP + Keys.UP + Keys.UP + Keys.UP).perform()
                    time.sleep(.5)
                    ActionChains(driver).send_keys(Keys.ENTER).perform()
                    time.sleep(2)
                    
                #@ open berry feeder
                driver.find_element(By.XPATH, "//*[@id='usersOpen']/input[1]").click()



            i = 300
            properBerry = 0
            numBerries = 0
            click = False
            
            #@ while loop that runs the clicking process
            while(i >= 0 and self._running):
                #@ get text to know what berry to click
                try:
                    #@ if feederUI is stale, skip this while step and try again until you can read the text
                    feederUI = driver.find_element(By.ID, "infoInteract")
                    feederInfo = feederUI.find_element(By.CSS_SELECTOR, "div")
                    feederInfoText = feederInfo.text
                    click = True
                except:
                    click = False


                #@ click depending on which berry
                if(click):
                    berryCorrectness = rand.randint(0,100)
                    if(berryCorrectness < percentCorrectBerries):
                        if("sour" in feederInfoText):
                            actions = ActionChains(driver)
                            actions.send_keys("1")
                            actions.perform()
                            properBerry += 1
                        elif("spicy" in feederInfoText):
                            actions = ActionChains(driver)
                            actions.send_keys("2")
                            actions.perform()
                            properBerry += 1
                        elif("dry" in feederInfoText):
                            actions = ActionChains(driver)
                            actions.send_keys("3")
                            actions.perform()
                            properBerry += 1
                        elif("sweet" in feederInfoText):
                            actions = ActionChains(driver)
                            actions.send_keys("4")
                            actions.perform()
                            properBerry += 1
                        elif("spicy" in feederInfoText):
                            actions = ActionChains(driver)
                            actions.send_keys("5")
                            actions.perform()
                            properBerry += 1 
                            
                    #@ if not designated to be "correct" select random berry or if clicking egg/no correct choice pokemon 
                    else:
                        randomInput = rand.randint(1,5)
                        actions = ActionChains(driver)
                        actions.send_keys(str(randomInput))
                        actions.perform()
                        

                ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
                
                #@ get number of pokemon left in the run
                try:
                    numLeft = int((WebDriverWait(driver, 3,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, "//*[@id='infoFeederRemaining']/span"))).text.split())[0])
                    i = numLeft
                    numBerries = number - numLeft
                except:
                    pass

                #@ if on user screen too long end run
                #@ (which probably means either the run broke, or you ran out of pokemon like in the case of pass orb farming)
                if("https://gpx.plus/users" in driver.current_url):
                    break
            
            print("Proper Berry Percent: ", str((properBerry/300)*100), "%")
            print("Proper Berries: ", str(properBerry))
            
            #@ store stats in mutable object that thread can interact with in a global scale
            storage.append([
                "    Total Berries: " + str(numBerries),
                "    Theoretical Percent Correct Berries: " + str(percentCorrectBerries),
                "    Num Proper Berries: " + str(properBerry),
                "    Real Num Correct Berries: " + str((properBerry/numBerries)*100)
            ])


def createWindow(accounts):
    tabs = []
    for account in accounts:
       tabBuilding = []
       tabBuilding +=[
           sg.Text("Tab for " + account["user"] + "'s account")
       ],
       tabBuilding += [
            sg.Text("Mass Click Runs")
       ],
       tabBuilding += [
            sg.Multiline(
                   autoscroll=False, disabled=True, size=(40, 30), key=(account["user"] + " multiline")
               )
       ],
       tabBuilding += [
            sg.Button(button_text="End Program", key=account["user"] + " endbutton"),
            sg.Text("Number of Runs"),
            sg.Spin(values=list(range(1, 100000)), initial_value=1, size=(5, 1), key=account["user"] + " spin"),
            sg.Checkbox(text="Pass Orb?", key = account["user"] + " passorb"),
            sg.Button(button_text="Click", key=account["user"] + " click"),
            sg.Button(button_text="End Click", key=account["user"] + " endclick")
       ],
       tabs += [
           sg.Tab(title = account["user"] + "'s tab", layout = tabBuilding)
       ],
    return tabs


#app = [
#
#    [
#       sg.Text("Mass Click Runs")
#   ],
#    [
#       sg.Multiline(
#            autoscroll=False, disabled=True, size=(40, 30), key="-RUN LIST-"
#       )
#    ],
#    [
#        sg.Button("End Program"),
#        sg.Text("Number of Runs"),
#        sg.Spin(values=list(range(1, 100000)), initial_value=1, size=(5, 1)),
#       sg.Checkbox(text="Pass Orb?"),
#        sg.Button("Click"),
#        sg.Button("End Click")
#    ]
#
#]

#layout = [
#    [sg.TabGroup(
#        [
#            [
#                sg.Tab('Tab 1', tab1_layout),
#                sg.Tab('Tab 2', tab2_layout)
#            ]
#       ], tooltip='TIP2')
#     ],
#    [
#        sg.Button('Read')
#    ]
#]


layout = [
    [sg.TabGroup(createWindow(accounts))
     ]
]


clickRuns = []
window = sg.Window("Demo", layout, return_keyboard_events=True, use_default_focus=False)
c = RunMaster()
t = Thread(target = c.run, args =(driver, 300, clickRuns, 1,))

clicking = False
prevRunList = []
p = vlc.MediaPlayer("https://play.pokemonshowdown.com/audio/cries/wooloo.mp3")
p.audio_set_volume(50)
p.play()


        


QT_ENTER_KEY1 =  'special 16777220'
QT_ENTER_KEY2 =  'special 16777221'
passOrb = False

RunMasters = []
threads = []
isClicking = []


#@ Create an event loop
while True:
    event, values = window.read(timeout=1000, close=False)
    passOrb = False
    numRuns = 0
    #if(values[0] == ''):
    #    numRuns = 1
    #else:
    #   numRuns = int(values[0])
    #    
    ##@ End program if user closes window or presses the OK button
    if event == "End Program" or event == sg.WIN_CLOSED:
        endBot(driver)
        break
    print("event ", event, " values ", values ) 
    # 
    ##@ on clicking "Click" button do run
    #elif event == "Click":
    #    if(not(clicking)):
    #        if(values[1]):
    #            passOrb = True
    #        RunMasters.append(RunMaster())
    #        threads.append(Thread(target = RunMasters[len(RunMasters) - 1].run, args =(driver, 300, clickRuns, numRuns, passOrb, )))
    #        threads[len(threads) - 1].start()
    #        isClicking.append(True)
    #
    ##@ on "ENTER" key input do run
    #elif(event in ('\r', QT_ENTER_KEY1, QT_ENTER_KEY2)):
    #    if(not(clicking)):
    #        if(values[1]):
    #            passOrb = True
    #        RunMasters.append(RunMaster())
    #        threads.append(Thread(target=RunMasters[len(RunMasters) - 1].run, args=(driver, 300, clickRuns, numRuns, passOrb, )))
    #        threads[len(threads) - 1].start()
    #        isClicking.append(True)
    #
    ##@ on clicking "End Click" button end run on thread        
    #elif event == "End Click":
    #    for i in range(0, len(RunMasters)):
    #        RunMasters[i].terminate()
    #    RunMasters.clear()
    #    threads.clear()
    #    isClicking.clear()
    #   driver.get("https://gpx.plus/users/random/1")
    #   p = vlc.MediaPlayer("https://play.pokemonshowdown.com/audio/cries/wooloo.mp3")
    #    p.audio_set_volume(50)
    #    p.play()
    #   
    ##@ if a thread is not alive (which means it died for some reason without my intervention) play sound and reset
    #i = 0
    #for thread in threads:
    #   if(not(thread.is_alive()) and isClicking[i]):
    #        p = vlc.MediaPlayer("https://play.pokemonshowdown.com/audio/cries/wooloo.mp3")
    #        p.audio_set_volume(50)
    #        p.play()
    #        threads.pop(i)
    #        isClicking.pop(i)
    #        RunMasters.pop(i)
    #    i += 1
    #    
    #    
    #runList = []
    #runNum = 1
    #
    ##@ form stats list in "storage" in string that can be used by multiline element
    #for run in clickRuns:
    #    runList.insert(0,"Num Run: " + str(runNum))
    #    runNum += 1
    #    index = 1
    #    for stat in run:
    #        runList.insert(index,stat)
    #        index += 1
    #
    #if(prevRunList != runList):
    #    window["-RUN LIST-"].update(value = '\n'.join(runList))
    #prevRunList = runList

window.close()
