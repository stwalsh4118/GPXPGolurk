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
from helper import *

class RunMaster:
      
    def __init__(self):
        self._running = True
      
    def terminate(self):
        self._running = False

    def fillEggs(self, driver, username, pokemon_name):
        #@ Navigate to shelter screen
        driver.find_element(By.CSS_SELECTOR, "a[data-page='shelter']").click()
        print(driver.current_url)
        time.sleep(1)
        
        #@ Get number of members in your party
        num_party_members = int(driver.find_element(By.CSS_SELECTOR, "div[data-notification='party']").text)
        print(num_party_members)
        loadEggs("eggs.json")
        #while(num_party_members < 6):
        
        return

    def clickRun(self, driver, username, number, storage, numrunstat, numruns, passorb):
        
        #    [summary]
        #    Used as a target method for thread.
        #
        #    To be used in conjunction with threads in this manner:
        #
        #*    threads[username] = Thread(target = c.run, args =(driver, username, number, storage, numrunstat, numruns, passorb, ))
        #*    threads[username].start()
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
            storage[username].append([
                "    Total Berries: " + str(total_berry_amount),
                "    Theoretical Percent Correct Berries: " + str(percent_correct_berries),
                "    Num Proper Berries: " + str(proper_berry_amount),
                "    Real Num Correct Berries: " + str((proper_berry_amount/total_berry_amount)*100)
            ])
            
            numrunstat[username] += 1