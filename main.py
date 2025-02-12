import os
import time
import random
import json
import telebot
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service  # Keep this one
from selenium.webdriver.chrome.options import Options
from PIL import Image
from io import BytesIO
from colorama import Fore, Style
import pyfiglet
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Optional: Run without GUI

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Display ASCII Art
ascii_banner = pyfiglet.figlet_format("INSTAGRAM BOT", font="slant")
print(Fore.CYAN + ascii_banner + Style.RESET_ALL)

# Load or ask for Telegram details
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

# Ask number of accounts to create
num_accounts = int(input(Fore.GREEN + "How many accounts to create per session? " + Style.RESET_ALL))

# Function to generate random names & usernames
def random_username():
    return "user" + str(random.randint(100000, 999999))

# Function to solve CAPTCHA manually (ASCII)
def solve_captcha(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    img.show()  # Open image for manual entry

    # Convert to ASCII
    print(Fore.YELLOW + "\nSolve CAPTCHA (check the image):" + Style.RESET_ALL)
    ascii_art = pyfiglet.figlet_format("[CAPTCHA]")
    print(Fore.MAGENTA + ascii_art + Style.RESET_ALL)
    captcha_text = input(Fore.CYAN + "Enter CAPTCHA: " + Style.RESET_ALL)
    return captcha_text

# Start Selenium WebDriver
options = Options()
options.add_argument("--headless")  # Run in headless mode (optional)
options.add_argument("--disable-blink-features=AutomationControlled")  # Hide automation

# Loop to create accounts
for _ in range(num_accounts):
    email = input(Fore.YELLOW + "Enter email for new account: " + Style.RESET_ALL)
    proxy = random.choice(proxies)
    options.add_argument(f"--proxy-server=socks5://{proxy}")

    driver = webdriver.Chrome(service=Service("chromedriver"), options=options)
    driver.get("https://www.instagram.com/accounts/emailsignup/")

    time.sleep(5)

    # Fill details
    username = random_username()
    password = "Void@111"

    driver.find_element(By.NAME, "emailOrPhone").send_keys(email)
    driver.find_element(By.NAME, "fullName").send_keys("Random User")
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.XPATH, "//button[contains(text(),'Sign up')]").click()
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
        pass

    # OTP Handling
    otp = input(Fore.YELLOW + "Enter OTP sent to email: " + Style.RESET_ALL)
    driver.find_element(By.NAME, "confirmationCode").send_keys(otp)
    driver.find_element(By.XPATH, "//button[contains(text(),'Next')]").click()
    time.sleep(5)

    print(Fore.GREEN + f"[SUCCESS] Created account: {username} | {password}" + Style.RESET_ALL)

    # Send account details to Telegram bot
    message = f"✅ *Instagram Account Created*\n📧 Email: `{email}`\n👤 Username: `{username}`\n🔑 Password: `{password}`"
    bot.send_message(owner_id, message, parse_mode="Markdown")

    driver.quit()
    time.sleep(2)  # Short delay between accounts

print(Fore.CYAN + "\nAll accounts created successfully!" + Style.RESET_ALL)
