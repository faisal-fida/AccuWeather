from selenium import webdriver
import os
import time


profile_directory = os.path.join(os.getcwd(), "chrome_profile")

options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={profile_directory}")

# adguard_extension_path = os.path.join(os.getcwd(), "adguard.crx")

# if not os.path.exists(profile_directory):
#     options.add_extension(adguard_extension_path)

driver = webdriver.Chrome(options=options)

driver.get("http://www.google.com")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    driver.quit()