import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import random

# === CONFIG ===
CHROMEDRIVER_PATH = './chromedriver.exe'  # <-- Change this to your chromedriver path
DELAY_BETWEEN_ACTIONS = 4             # Base seconds between unfollows to avoid spam flags
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"

options = uc.ChromeOptions()
options.add_argument(f'--user-agent={USER_AGENT}')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--disable-infobars')
options.add_argument('--disable-extensions')
options.add_argument('--profile-directory=Default')
options.add_argument('--disable-plugins-discovery')
options.add_argument('--start-maximized')

# Use undetected_chromedriver for stealth
# Note: chromedriver.exe must still match your Chrome version

driver = uc.Chrome(driver_executable_path=CHROMEDRIVER_PATH, options=options)

def wait(base=DELAY_BETWEEN_ACTIONS, jitter=1):
    time.sleep(base + random.uniform(0, jitter))

try:
    driver.get('https://www.tiktok.com/login')
    wait(5)

    print("You have 2 minutes to log in to TikTok in the browser using your mobile or any method.")
    for i in range(2, 0, -1):
        print(f"{i} minute(s) remaining...")
        wait(60, 5)
    print("Login time is over. Continuing...")

    # Prompt user for their TikTok username
    username = input("Enter your TikTok username (without @): ").strip()
    print(f"Using username: {username}")

    # Navigate to Profile page with lang param
    profile_url = f'https://www.tiktok.com/@{username}?lang=en-GB'
    driver.get(profile_url)
    wait(5)

    # Click the 'Following' button to open the popup
    following_xpath = '//*[@id="main-content-others_homepage"]/div/div[1]/div[2]/div[3]/h3/div[1]/span'
    try:
        following_btn = driver.find_element(By.XPATH, following_xpath)
        following_btn.click()
        print("Clicked 'Following' to open the following popup.")
        wait(3)
        # Close the cookie banner if it appears
        try:
            cookie_banner = driver.find_element(By.XPATH, '//tiktok-cookie-banner')
            close_btn = cookie_banner.find_element(By.XPATH, './/button')
            close_btn.click()
            print("Closed TikTok cookie banner.")
            wait(2)
        except Exception:
            pass  # No cookie banner found
        # Use the new XPath for the popup section
        try:
            popup_section = driver.find_element(By.XPATH, '//*[@id="tux-portal-container"]/div/div[2]/div/div/div[2]/div/div/section')
            print("Popup section HTML:\n", popup_section.get_attribute('outerHTML'))
        except Exception as e:
            print(f"Could not find popup section: {e}")
    except Exception as e:
        print(f"Could not click 'Following' button: {e}")
        driver.quit()
        exit(1)

    unfollowed = 0
    last_user_count = -1

    while True:
        # Get the popup section
        try:
            popup_section = driver.find_element(By.XPATH, '//*[@id="tux-portal-container"]/div/div[2]/div/div/div[2]/div/div/section')
            user_items = popup_section.find_elements(By.XPATH, './/li')
        except Exception as e:
            print(f"Could not find popup section or user items: {e}")
            break

        if not user_items:
            print("No more users found. Unfollowing complete!")
            break

        # Unfollow users currently loaded
        for user in user_items:
            try:
                # Extract username
                username_elem = user.find_element(By.XPATH, './/a[contains(@href, "/@")]')
                user_url = username_elem.get_attribute('href')
                user_name = user_url.split('/')[-1].split('?')[0].lower()

                # Find the unfollow button
                unfollow_button = user.find_element(By.XPATH, './/button[@data-e2e="follow-button"]')
                btn_text = unfollow_button.text.strip().lower()
                if btn_text == "following":
                    unfollow_button.click()
                    unfollowed += 1
                    print(f"Unfollowed: {user_name} (Total unfollowed: {unfollowed})")
                    wait(DELAY_BETWEEN_ACTIONS)
                else:
                    print(f"Keeping friend: {user_name} (button: {btn_text})")
                    continue

            except Exception as e:
                print(f"Error processing user: {e}")
                continue

        # Scroll the popup to load more users
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", popup_section)
        wait(3)
        
        # Check if new users have loaded
        new_user_items = popup_section.find_elements(By.XPATH, './/li')
        if len(new_user_items) == last_user_count:
            print("Reached the end of the following list.")
            break
        last_user_count = len(new_user_items)

    print(f"Finished unfollowing {unfollowed} accounts.")

finally:
    driver.quit()
    print("Browser closed.")