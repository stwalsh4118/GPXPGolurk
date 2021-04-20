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



#TODO: EVENTUALLY HAVE FULL AUTO OPTION SO IT WILL JUST RUN AND CLICK AND HATCH EGGS FOR YOU

#IDEA: COULD TRACK TIME IT TAKES FOR SERVER TO RESPOND OVERTIME AND ADD THAT TIME TO SPECIFIC 
#IDEA: SLEEPS SO WE NEVER DO STUFF BEFORE THE PAGE IS READY ON THOSE SPECIFIC SLEEPS

#IDEA: SAFARI ZONE MODE
#IDEA: LAB MODE

class RunMaster:
      
    def __init__(self):
        self._running = True
      
    def terminate(self):
        self._running = False

    def fillEggs(self, driver, username, pokemon_name):
        """
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
        """
                
        #TODO: PROBABLY SHOULD HAVE A TIMEOUT IF LOOKING FOR EGGS FOR TOO LONG
        #TODO: IF TIMED OUT, CHECK IF YOU HAVE EGGS READY TO DONATE TO SHELTER IN YOUR DAYCARE (search "TODO: fillEggs #1")
        
        #IDEA: RANDOM EGG MODE
        
        if(pokemon_name == None or pokemon_name == ""): return 
        
        #@ Navigate to shelter screen
        driver.get("https://gpx.plus/shelter")
        time.sleep(1)
        
        #@ Get number of members in your party
        num_party_members = int(driver.find_element(By.CSS_SELECTOR, "div[data-notification='party']").text)
        print(num_party_members)
        
        #@ load egg data from file
        egg_list = loadEggs("eggs.json")
        image_search = ""

        # #@ check if selected pokemon is within our dataset
        # if(not(pokemon_name in egg_list)): return print("pokemon not in data")
        # image_search = egg_list[pokemon_name]["image"]
        
        
        #TODO: fillEggs #1  
        #@ while party isnt full
        while(num_party_members < 6):
            num_party_members = int(driver.find_element(By.CSS_SELECTOR, "div[data-notification='party']").text)
            #print(image_search)
            
            # #@ check if egg is in the current shelter display via img (doesnt work because img url isn't the same like I thought)
            # #@ can maybe implement this search method via checking all images in the shelter against a reference... maybe?
            # if(len(driver.find_elements(By.CSS_SELECTOR, f"img[src={image_search}]")) > 0):
            #     #@ grab egg from shelter
            #     driver.find_element(By.CSS_SELECTOR, f"img[src={image_search}]").click()
            
            #TODO: RANDOM EGG MODE AS WELL NOT JUST MYSTERY
            #@ if mystery egg mode is enabled, only grab eggs that we haven't gotten before (gonna use this so I can harvest egg images)
            mystery_egg_mode = False
            if(mystery_egg_mode):
                self.gatherEgg(driver, "Mystery")
            else:
                self.gatherEgg(driver, pokemon_name)
            
            #@ reload shelter
            try:
                clickElementWait(driver, "CSS", "span[class='shelterLoad']", 3)
                time.sleep(.5)
            except Exception as e:
                print(e)
                return
            
            #@ quit if end action button is pressed
            if(not(self._running)):
                break
        return
    
    def gatherEgg(self, driver, pokemon_name):
        
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
                clickElementWait(driver, "CSS", f"img[data-tooltip='{pokemon_name} Egg']", 1)
                time.sleep(.5)
            except Exception as e:
                print(e)
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
                clickElementWait(driver, "XPATH", "//button[text()='Yes, claim it']", 3)
                time.sleep(.5)
                print("confirmation clicked")
            
        return
    
    
    
    def hatchEggs(self, driver, username, box_number):
        
        """
        #   [summary]
        #   
        #    Hatch all eggs in your party that are mature
        #
        #   Args:
        #@   driver (Chrome webdriver): the driver of the Chrome application you are running
        #@   username (string): username for account of the driver
        #@   box_number (int): box number to start search for box to put pokemon into to use in movePokemon function after hatching
        """
        
        #TODO: NEED TO HAVE A SYSTEM THAT KNOWS WHICH BOX TO PUT YOUR SHINY INTO (search "TODO: hatchEggs #2")
        #TODO: OPTIONS ARE:
        #TODO:           DO A CHECK IN THE PC TO SEE WHICH BOXES ARE PROTECTED 
        #TODO:                  (WE CAN ALSO CHECK IF PROTECTED IS FULL AND THEN MAKE ANOTHER PROTECTED BOX TO FILL UP, AD INFINITUM)
        #TODO:           MANUALLY PICK (NOT GOOD FOR AUTOMATIC MODE)
        #TODO:           SELECT THE FIRST BOX WITH ROOM(NOT GOOD BECAUSE REQUIRES MANUAL CHECKING FOR SHINIES WHICH THIS IS SUPPOSED TO REMEDY)
        #TODO:           SAVE FIRST X AMOUNT OF BOXES TO BE RESERVED FOR SPECIAL POKEMON IMPLICITLY (THIS ONES OK, BUT PROBLEM IF FILLED)

        #IDEA: PRINT SAVE DATA WHEN EGGS ARE HATCHED
        
        #@ go to main page
        driver.get("https://gpx.plus/main")       
        
        #@ check for hatch button (may be disabled if eggs not mature for 1 hour I think)
        #@ move any pokemon that need to be then stop hatching
        if(len(driver.find_elements(By.CSS_SELECTOR, "span[class='pkAllHatch']")) <= 0): 
            self.movePokemon(driver, box_number) 
            return

        #@ click hatch button
        clickElementWait(driver, "CSS", "span[class='pkAllHatch']", 3)
        
        #@ click hatch all button
        clickElementWait(driver, "CSS", "span[class='pkAllAll']", 3)
        
        #@ wait for hatch confirmation button to appear
        while(len(driver.find_elements(By.XPATH, "//button[text()='Yes, hatch them']")) <= 0):
            pass
        time.sleep(.5)
        
        #@ click the hatch confirmation button
        try:
            clickElementWait(driver, "XPATH", "//button[text()='Yes, hatch them']", 3)
        except Exception as e:
            print(e)
            return
        
        #@ wait for post-hatch alert that tells you what you hatched
        while(len(driver.find_elements(By.XPATH, "//div[contains(text(), 'Your egg hatched into')]")) <= 0):
            pass
        
        print(driver.find_elements(By.XPATH, "//div[contains(text(), 'Your egg hatched into')]")[0].text)
        
        #@ get list of events that happened during hatching (includes items being found on pokemon)
        hatched_info = driver.find_elements(By.XPATH, "//div[contains(text(), 'Your egg hatched into')]")[0].text.split("\n")
        print(hatched_info)
        
        #@ check if there is a shiny among the pokemon hatched and get its position in your party
        index = 1
        shiny_index = -1
        for hatched in hatched_info:
            print(hatched)
            if("Your egg hatched into Sh." in hatched):
                print("Shiny hatched!")
                shiny_index = index
            index += 1
            
        #@ close post-hatch alert
        t_end = time.time() + 2
        timeout = False
        clickElementWait(driver, "CSS", "span[class='ui-icon ui-icon-closethick']", 3)
            
        
        #TODO: hatchEggs #2
        #@ if there is a shiny that was hatched move it into box specified
        shiny_box = 1
        if(shiny_index != -1):
            clickElementWait(driver, "XPATH", f"//*[@id='UserParty']/li[{shiny_index}]/div[4]/span[1]", 3)
            
            for box_index in range(15 + shiny_box):
                actions = ActionChains(driver)
                actions.send_keys(Keys.DOWN)
                actions.perform()
            time.sleep(.5)
            
            actions = ActionChains(driver)
            actions.send_keys(Keys.ENTER)
            actions.perform()
            time.sleep(.5)
            
            actions = ActionChains(driver)
            actions.send_keys(Keys.ENTER)
            actions.perform()
            time.sleep(.5)
        
        
        time.sleep(.5)
        #@ move pokemon into box
        self.movePokemon(driver, box_number)

        return
    
    

    def movePokemon(self, driver, box_number):
        
        """    
        #   [summary]
        #   
        #    Used to move pokemon from your party into a PC starting at a certain box number so the ones before are not changed
        #
        #   Args:
        #@   driver (Chrome webdriver): the driver of the Chrome application you are running
        #@   box_number (int): box number to start search for box to put pokemon into
        """
        
        #TODO: MAKE IT SO THAT IT CHECKS AGAINST NUMBER IN PARTY NOT JUST MAX PARTY AMOUNT (search for "TODO: movePokemon #1")
        
        #IDEA: PRINT SAVE DATA WHEN POKEMON ARE MOVED
        
            
        #@ click move all pokemon button
        try:
            clickElementWait(driver, "CSS", "span[class='pkAllMove']", 3)
        except Exception as e:
            print(e)
            return
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
            if((num_in_box - 6) >= 0):
                selected_box = box_index
                break
            
            box_index += 1
            if(box_index > 24):
                break 
        
        print(f"The selected box is {selected_box}")
        
        #@ click move all to box button
        clickElementWait(driver, "CSS", "span[class='button toggleButton pkAllAllPC']", 3)
        
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
        
        #@ click move confirmation button
        clickElementWait(driver, "XPATH", "//button[text()='Yes, move them']", 3)
        time.sleep(.5)
        
        return
        

    def clickRun(self, driver, username, number, storage, numrunstat, numruns, passorb, fullrandom, pokemon_name):
        
        """
        #    [summary]
        #
        #    Runs routine that automates massclicks
        #
        #    Used as a target method for thread.
        #
        #    To be used in conjunction with threads in this manner:
        #
        #*    threads[username] = Thread(target = RunMasters[username].clickRun, args =(driver, username, number, storage, numrunstat, numruns, passorb, fullrandom, pokemon_name))
        #*    threads[username].start()
        #    
        #    Args:
        #@    driver (Chrome webdriver): the driver of the Chrome application you are running
        #@    number (int: x < 300): number of pokemon to open in the berry feeder
        #@    storage (list): list object used to store data from click run
        #@    numruns (int x > 0): number of click runs to complete in a row
        #@    passorb (bool): if True selects "Iteract with players that have interacted with you that you haven't" to farm pass orbs
        """
        
        #IDEA: implement time based clicking, so that the different accounts don't look so similar
        #TODO: MAKE IT SO PROPER BERRIES ARE STILL COUNTED FOR RANDOM MODE (search TODO: clickRun #1)
        for i in range(numruns):
            
            if(self._running):
                
                #@ selects from range percent of berries that *should* be correct
                percent_correct_berries = rand.randint(10,20)

                #@ navigates to users screen
                driver.get("https://gpx.plus/users/")
                print(driver.current_url)
                time.sleep(1)

                #@ set number of pokemon/eggs to *300*
                if(driver.find_element(By.NAME, "number").get_attribute("value") != 300):
                    driver.find_element(By.NAME, "number").send_keys(Keys.DELETE + Keys.DELETE + Keys.DELETE + Keys.BACKSPACE + Keys.BACKSPACE + Keys.BACKSPACE + str(number))

                #@ set number of users to *1000*
                if(driver.find_element(By.XPATH,"//*[@id='usersCount']/span").text != "View 1000 users (who)"):
                    clickElementWait(driver, "ID", "usersCount", 3)
                    time.sleep(.5)
                    actions = ActionChains(driver)
                    actions.send_keys(Keys.DOWN + Keys.DOWN + Keys.DOWN)
                    actions.perform()
                    time.sleep(.5)
                    actions.send_keys(Keys.ENTER)
                    actions.perform()

                #@ set users to pick from to *random(because all is being a bitch)*
                if(driver.find_element(By.XPATH, "//*[@id='usersList']/span") != "ordered randomly" and not(passorb)):
                    clickElementWait(driver, "XPATH", "//*[@id='usersList']", 3)
                    time.sleep(.5)
                    ActionChains(driver).send_keys(Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN).perform()
                    time.sleep(.5)
                    ActionChains(driver).send_keys(Keys.ENTER).perform()
                    time.sleep(2)
                    
                #@ set users to pick from to *users that have interacted with me*
                elif(passorb):
                    clickElementWait(driver, "XPATH", "//*[@id='usersList']", 3)
                    time.sleep(.5)
                    ActionChains(driver).send_keys(Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.DOWN + Keys.UP + Keys.UP + Keys.UP + Keys.UP + Keys.UP + Keys.UP + Keys.UP + Keys.UP).perform()
                    time.sleep(.5)
                    ActionChains(driver).send_keys(Keys.ENTER).perform()
                    time.sleep(2)
                    
                #@ open berry feeder
                clickElementWait(driver, "XPATH", "//*[@id='usersOpen']/input[1]", 3)



            i = 300
            proper_berry_amount = 0
            total_berry_amount = 0
            click = False
            
            base_minute = 60
            base_pokemon_per_minute = 300
            
            #TODO: HAVE INPUT FOR THIS
            pokemon_per_minute = 300
            
            #@ time for mass click run to run
            run_end = time.time() + base_minute * base_pokemon_per_minute / pokemon_per_minute
            
            
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


                if(not(fullrandom)):
                    
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
                                
                        #@ if not designated to be "correct" select berry that is purposefully wrong or if clicking egg/no correct choice pokemon 
                        else:
                            if("sour" in feeder_info_text):
                                actions = ActionChains(driver)
                                actions.send_keys("2")
                                actions.perform()
                                proper_berry_amount += 1
                            elif("spicy" in feeder_info_text):
                                actions = ActionChains(driver)
                                actions.send_keys("3")
                                actions.perform()
                                proper_berry_amount += 1
                            elif("dry" in feeder_info_text):
                                actions = ActionChains(driver)
                                actions.send_keys("4")
                                actions.perform()
                                proper_berry_amount += 1
                            elif("sweet" in feeder_info_text):
                                actions = ActionChains(driver)
                                actions.send_keys("5")
                                actions.perform()
                                proper_berry_amount += 1
                            elif("spicy" in feeder_info_text):
                                actions = ActionChains(driver)
                                actions.send_keys("1")
                                actions.perform()
                                proper_berry_amount += 1 
                                
                #TODO: clickRun #1
                #@ pick berry completely randomly (should have a 1:5 proper berry input to interaction ratio)
                else:
                    if(click):
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
                #TODO: THIS IS DEFINITLY NOT THE BEST WAY TO DO THIS, BREAKS IF SERVERS RUNNING SLOW
                if("https://gpx.plus/users" in driver.current_url):
                    break
            
            print("Proper Berry Percent: ", str((proper_berry_amount/300)*100), "%")
            print("Proper Berries: ", str(proper_berry_amount))
            
            #@ store stats in mutable object that thread can interact with in a global scale
            if(total_berry_amount == 0):
                total_berry_amount = 1
            storage[username].append([
                "    Total Berries: " + str(total_berry_amount),
                "    Theoretical Percent Correct Berries: " + str(percent_correct_berries),
                "    Num Proper Berries: " + str(proper_berry_amount),
                "    Real Num Correct Berries: " + str((proper_berry_amount/total_berry_amount)*100)
            ])
            
            numrunstat[username] += 1
            
            #@ hatch any eggs you can then fill your party back with eggs after every mass click run
            self.hatchEggs(driver, username, 3)
            self.fillEggs(driver, username, pokemon_name)
            
            #@ if mass click run is faster than X pokemon per second then wait, if it is slower, then do nothing (we can't go faster than a certain amount)
            print(f"Time left in run: {run_end - time.time()}")
            while(time.time() < run_end):
                pass
            
        return