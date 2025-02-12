import os
import time
import random
import json
import telebot
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from PIL import Image
from io import BytesIO
from colorama import Fore, Style
import pyfiglet
from webdriver_manager.chrome import ChromeDriverManager

# Set up WebDriver options
options = Options()
options.add_argument("--headless")  
options.add_argument("--no-sandbox")  
options.add_argument("--disable-dev-shm-usage")  
options.add_argument("--disable-blink-features=AutomationControlled")  

# Display ASCII Art
ascii_banner = pyfiglet.figlet_format("INSTAGRAM BOT", font="slant")
print(Fore.CYAN + ascii_banner + Style.RESET_ALL)

# Load Telegram bot details
config_file = "config.json"
if os.path.exists(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)
        owner_id = config["owner_id"]
        bot_token = config["bot_token"]
else:
    owner_id = input(Fore.YELLOW + "Enter your Telegram Owner ID: " + Style.RESET_ALL)
    bot_token = input(Fore.YELLOW + "Enter your Telegram Bot Token: " + Style.RESET_ALL)
    with open(config_file, "w") as f:
        json.dump({"owner_id": owner_id, "bot_token": bot_token}, f)

bot = telebot.TeleBot(bot_token)

# Read proxies
proxy_file = "proxy.txt"
if not os.path.exists(proxy_file):
    print(Fore.RED + "[ERROR] proxy.txt not found!" + Style.RESET_ALL)
    exit()

with open(proxy_file, "r") as f:
    proxies = f.read().splitlines()

if not proxies:
    print(Fore.RED + "[ERROR] No proxies found in proxy.txt!" + Style.RESET_ALL)
    exit()

# Ask the number of accounts to create
try:
    num_accounts = int(input(Fore.GREEN + "How many accounts to create per session? " + Style.RESET_ALL))
except ValueError:
    print(Fore.RED + "[ERROR] Invalid number entered!" + Style.RESET_ALL)
    exit()

# Function to generate random usernames
def random_username():
    return "user" + str(random.randint(100000, 999999))

# Function to solve CAPTCHA manually
def solve_captcha(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    img.show()

    print(Fore.YELLOW + "\nSolve CAPTCHA (check the image):" + Style.RESET_ALL)
    ascii_art = pyfiglet.figlet_format("[CAPTCHA]")
    print(Fore.MAGENTA + ascii_art + Style.RESET_ALL)

    captcha_text = input(Fore.CYAN + "Enter CAPTCHA: " + Style.RESET_ALL)
    return captcha_text

# Loop to create accounts
for _ in range(num_accounts):
    email = input(Fore.YELLOW + "Enter email for new account: " + Style.RESET_ALL)
    proxy = random.choice(proxies)

    # Add proxy to options
    options.add_argument(f"--proxy-server={proxy}")

    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.instagram.com/accounts/emailsignup/")
    
    time.sleep(5)

    # Fill account details
    username = random_username()
    password = "Void@111"

    try:
        driver.find_element(By.NAME, "emailOrPhone").send_keys(email)
        driver.find_element(By.NAME, "fullName").send_keys("Random User")
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[contains(text(),'Sign up')]").click()
    except Exception as e:
        print(Fore.RED + f"[ERROR] Could not fill form: {e}" + Style.RESET_ALL)
        driver.quit()
        continue

    time.sleep(5)

    # CAPTCHA Handling
    try:
        captcha_element = driver.find_element(By.XPATH, "//img[contains(@src, 'captcha')]")
        captcha_url = captcha_element.get_attribute("src")
        captcha_text = solve_captcha(captcha_url)
        driver.find_element(By.NAME, "captcha").send_keys(captcha_text)
        driver.find_element(By.NAME, "captcha").send_keys(Keys.ENTER)
        time.sleep(3)
    except:
        print(Fore.GREEN + "[INFO] No CAPTCHA detected!" + Style.RESET_ALL)

    # OTP Handling
    otp = input(Fore.YELLOW + "Enter OTP sent to email: " + Style.RESET_ALL)
    try:
        driver.find_element(By.NAME, "confirmationCode").send_keys(otp)
        driver.find_element(By.XPATH, "//button[contains(text(),'Next')]").click()
        time.sleep(5)
    except Exception as e:
        print(Fore.RED + f"[ERROR] OTP entry failed: {e}" + Style.RESET_ALL)
        driver.quit()
        continue

    print(Fore.GREEN + f"[SUCCESS] Created account: {username} | {password}" + Style.RESET_ALL)

    # Send account details to Telegram bot
    message = f"✅ *Instagram Account Created*\n📧 Email: `{email}`\n👤 Username: `{username}`\n🔑 Password: `{password}`"
    bot.send_message(owner_id, message, parse_mode="Markdown")

    driver.quit()
    time.sleep(2)

print(Fore.CYAN + "\nAll accounts created successfully!" + Style.RESET_ALL)
