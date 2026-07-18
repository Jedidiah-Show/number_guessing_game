# All UI logic is embedded here...(printing functions)

from colorama import Fore, Back, Style, init

init(autoreset=True)

GOLD = "\033[1;33m"    # Bold Yellow
SILVER = "\033[1;37m"  # Bold White
BRONZE = "\033[1;31m"  # Bold Red/Dark Red
RESET = Fore.RESET

def text(message):
    print(Fore.WHITE + message)

def header(title=""):
    message = "Welcome to the Number Guessing Game!"
    text("=" * len(message))
    print(Fore.CYAN + Style.BRIGHT + message)
    print(Fore.LIGHTCYAN_EX + f"{title}")
    text("=" * len(message))
    text("You can exit the game at any time by typing 'exit'")

def error(message): 
    print(Fore.RED + message)

def correct(message):
    print(Fore.GREEN + message)

def exit(cause):
    if cause.lower() == "interrupt":
        return Fore.RED + "Execution interrupted"
    else:
        return Fore.YELLOW + "Thank you for playing! See ya soon!"

def choice(message):
    selection = input(Fore.BLUE + message)
    return selection

def entry(message="info"):
    user_entry = input(Fore.BLUE + f"Enter your {message}: ")
    return user_entry   
