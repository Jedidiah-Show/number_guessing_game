# Reusable command line, time and navigation functions 

import sys
import os
import time
from internal.ui.ui import exit, choice  

def sleep_time(delay = 2):
    time.sleep(delay)

def is_exit(cause="clean"):
    message = exit(cause)
    sys.exit("\n"+ message)
   
def clearscreen():
    return os.system('cls' if os.name == 'nt' else 'clear')

def go_back(page= "Main Menu"):
    try:
        go_back = choice(f"Enter any key to return to the {page}: ")
        if go_back == "exit":
            is_exit()
        elif go_back:
            return
    except KeyboardInterrupt:
        is_exit("interrupt")


