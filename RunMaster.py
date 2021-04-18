import time
from PySimpleGUI.PySimpleGUI import B, Checkbox
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
import re


#TODO: INTEGRATE HATCHING EGGS, FILLING EGGS, AND MOVING POKEMON FUNCTIONS INTO CLICK RUN FUNCTION SO WE CAN GET AND HATCH EGGS
#TODO: AUTOMATICALLY IN THE MIDDLE OF CLICK RUNS (EVENTUALLY HAVE FULL AUTO OPTION SO IT WILL JUST RUN AND CLICK AND HATCH EGGS FOR YOU)

class RunMaster:
      
    def __init__(self):
        self._running = True
      
    def terminate(self):
        self._running = False

    def fillEggs(self, driver, username, pokemon_name):
        
        #   [summary]
        #   
        #    Runs routine that fills your party with the specified pokemons eggs
        #
        #    Used as a target method for thread.
        #
        #    To be used in conjunction with threads in this manner:
        #
        #*    threads[username] = Thread(target = RunMasters[username].fillEggs, args =(driver, username, pokemon_name, ))
        #*    threads[username].start()
        #
        #   Args:
        #@   driver (Chrome webdriver): the driver of the Chrome application you are running
        #@   username (string): the username for which account/driver you are running
        #@   pokemon_name (string): the pokemon name for which egg you are looking for to fill up your party
        
        
        
        #@ Navigate to shelter screen
        driver.find_element(By.CSS_SELECTOR, "a[data-page='shelter']").click()
        print(driver.current_url)
        time.sleep(1)
        
        #@ Get number of members in your party
        num_party_members = int(driver.find_element(By.CSS_SELECTOR, "div[data-notification='party']").text)
        print(num_party_members)
        
        #@ load egg data from file
        egg_list = loadEggs("eggs.json")
        image_search = ""

        #@ check if selected pokemon is within our dataset
        if(not(pokemon_name in egg_list)): return print("pokemon not in data")
        image_search = egg_list[pokemon_name]["image"]
        print(num_party_members < 6)
        
        #@ while party isnt full
        while(num_party_members < 6):
            num_party_members = int(driver.find_element(By.CSS_SELECTOR, "div[data-notification='party']").text)
            #print(image_search)
            
            # #@ check if egg is in the current shelter display via img (doesnt work because img url isn't the same like I thought)
            # #@ can maybe implement this search method via checking all images in the shelter against a reference... maybe?
            # if(len(driver.find_elements(By.CSS_SELECTOR, f"img[src={image_search}]")) > 0):
            #     #@ grab egg from shelter
            #     driver.find_element(By.CSS_SELECTOR, f"img[src={image_search}]").click()
            
            #@ check if egg is in the current shelter display via the egg name 
            #@ if you have already discovered/hatched the egg and revealed the egg name in the shelter
            #@ will need to implement the check if you have the egg data in your pokedex before using this
            #@ but for now we assume you already have egg data for the egg selected
            
            egg_found = False
            if(len(driver.find_elements(By.CSS_SELECTOR, f"img[data-tooltip='{pokemon_name} Egg']")) > 0):
                print("Egg found")
                egg_found = True
                
                #@ try to click egg (theres several scenarios where you can't click the egg even if its there like if another egg is on top)
                #@ so we just skip and reload the shelter
                try:
                    driver.find_elements(By.CSS_SELECTOR, f"img[data-tooltip='{pokemon_name} Egg']")[0].click()
                    time.sleep(.5)
                except:
                    egg_found = False
                
                #@ wait for egg claim button to appear 
                #@ (there are cases where the button doesn't appear even when egg IS clicked so we just skip if that happens)
                t_end = time.time() + 1
                timeout = False
                while(len(driver.find_elements(By.XPATH, "//button[text()='Yes, claim it']")) <= 0 and egg_found and self._running and not(timeout)):
                    if(len(driver.find_elements(By.CSS_SELECTOR, f"img[data-tooltip='{pokemon_name} Egg']")) <= 0):
                        egg_found = False
                    if(len(driver.find_elements(By.CSS_SELECTOR, "aside[class='tooltip ']")) > 0):
                        egg_found = False
                    if((time.time() < t_end)):
                        timeout = True
                        egg_found = False
                time.sleep(.5)
                
                #@ click confirmation button
                if(egg_found):
                    driver.find_elements(By.XPATH, "//button[text()='Yes, claim it']")[0].click()
                    time.sleep(.5)
                print("confirmation clicked")
            
            #@ reload shelter
            if(len(driver.find_elements(By.CSS_SELECTOR, "span[class='shelterLoad']")) > 0):
                driver.find_elements(By.CSS_SELECTOR, "span[class='shelterLoad']")[0].click()
            
            #@ quit if end action button is pressed
            if(not(self._running)):
                break
        return
    
    
    
    def hatchEggs(self, driver, username, box_number):
        
        #   [summary]
        #   
        #    Hatch all eggs in your party that are mature
        #
        #   Args:
        #@   driver (Chrome webdriver): the driver of the Chrome application you are running
        #@   username (string): username for account of the driver
        #@   box_number (int): box number to start search for box to put pokemon into to use in movePokemon function after hatching
        
        #TODO: READ MESSAGE AFTER HATCHING EGGS AND SEE IF YOU GOT A SHINY AND MOVE IT TO A DIFFERENT BOX THAT IS LOCKED
        #TODO: ALSO NEED TO CLOSE SAID MESSAGE AFTER HATCHING EGGS (search for "TODO hatchEggs #1")
        
        
        #@ go to main page
        driver.get("https://gpx.plus/main")
        
        #@ check for hatch button (may be disabled if eggs not mature for 1 hour I think)
        if(len(driver.find_elements(By.CSS_SELECTOR, "span[class='pkAllHatch']")) <= 0): return

        #@ click hatch button
        driver.find_elements(By.CSS_SELECTOR, "span[class='pkAllHatch']")[0].click()
        
        #@ wait for hatch all button to appear
        while(len(driver.find_elements(By.CSS_SELECTOR, "span[class='pkAllAll']")) <= 0):
            pass
        
        #@ click hatch all button
        driver.find_elements(By.CSS_SELECTOR, "span[class='pkAllAll']")[0].click()
        
        #@ wait for hatch confirmation button to appear
        while(len(driver.find_elements(By.XPATH, "//button[text()='Yes, hatch them']")) <= 0):
            pass
        
        #@ click the hatch confirmation button
        driver.find_elements(By.XPATH, "//button[text()='Yes, hatch them']")[0].click()
        
        
        #TODO: hatchEggs #1
        
        
        #@ move pokemon into box
        self.movePokemon(driver, box_number)
        
        return
    
    

    def movePokemon(self, driver, box_number):
            
        #   [summary]
        #   
        #    Used to move pokemon from your party into a PC starting at a certain box number so the ones before are not changed
        #
        #   Args:
        #@   driver (Chrome webdriver): the driver of the Chrome application you are running
        #@   box_number (int): box number to start search for box to put pokemon into
        
        #TODO: MAKE IT SO THAT IT CHECKS AGAINST NUMBER IN PARTY NOT JUST MAX PARTY AMOUNT (search for "TODO: movePokemon #1")
        
        #@ wait for move all pokemon button to appear
        while(len(driver.find_elements(By.CSS_SELECTOR, "span[class='pkAllMove']")) <= 0):
            pass
        
        #@ click move all pokemon button
        driver.find_elements(By.CSS_SELECTOR, "span[class='pkAllMove']")[0].click()
        time.sleep(.5)
        
        
        #@ find box to put all pokemon in starting with box_number given
        box_index = box_number
        selected_box = 0
        while(True):
            num_in_box = \
                (
                    driver\
                    .find_element(By.CSS_SELECTOR, "span[class='button toggleButton pkAllAllPC']")\
                    .get_attribute(f"data-{box_index}")\
                    .split(" ")[2]
                )
            num_in_box = int(re.findall(r"\[\s*\+?(-?\d+)\s*\]", num_in_box)[0])
            print(f"Number of pokemon in box {box_index} : {num_in_box}")
            
            
            #TODO: movePokemon #1
            #@ check if box has enough room to put our pokemon in
            if((num_in_box - 6) > 0):
                selected_box = box_index
                break
            
            box_index += 1
            if(box_index > 24):
                break 
        
        print(f"The selected box is {selected_box}")
        
        #@ click move all to box button
        driver.find_elements(By.CSS_SELECTOR, "span[class='button toggleButton pkAllAllPC']")[0].click()  
        
        #@ move selector to the box we selected
        for i in range(selected_box):
            actions = ActionChains(driver)
            actions.send_keys(Keys.DOWN)
            actions.perform()
        time.sleep(.5)
        
        #@ click enter to choose the box we selected to move our pokemon into
        actions = ActionChains(driver)
        actions.send_keys(Keys.ENTER)
        actions.perform()
        time.sleep(.5)
        
        #@ wait for move confirmation button to show up
        while(len(driver.find_elements(By.XPATH, "//button[text()='Yes, move them']")) <= 0):
            pass
        
        #@ click move confirmation button
        driver.find_elements(By.XPATH, "//button[text()='Yes, move them']")[0].click()
        time.sleep(.5)
        
        return
        

    def clickRun(self, driver, username, number, storage, numrunstat, numruns, passorb):
        
        #    [summary]
        #
        #    Runs routine that automates massclicks
        #
        #    Used as a target method for thread.
        #
        #    To be used in conjunction with threads in this manner:
        #
        #*    threads[username] = Thread(target = RunMasters[username].clickRun, args =(driver, username, number, storage, numrunstat, numruns, passorb, ))
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
        return