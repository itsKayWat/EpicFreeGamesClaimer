import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)

# Function to send notifications (placeholder)
def send_notification(message):
    logging.info(f'Notification: {message}')

def setup_chrome_with_profile():
    chrome_options = webdriver.ChromeOptions()
    
    # Get the correct path for Windows
    user_data_dir = os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data')
    
    # Add necessary options to prevent crashes
    chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
    chrome_options.add_argument('--profile-directory=Default')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Close any existing Chrome instances
    os.system("taskkill /f /im chrome.exe")
    time.sleep(2)
    
    try:
        return webdriver.Chrome(options=chrome_options)
    except Exception as e:
        print(f"Error creating Chrome instance: {str(e)}")
        print("Trying alternative method...")
        
        # Alternative method without user profile
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome(options=chrome_options)

# Function to claim free games
def claim_free_games():
    driver = None
    try:
        driver = setup_chrome_with_profile()
        driver.get('https://www.epicgames.com/store/free-games')
        logging.info('Navigated to Epic Games Store')

        # Wait for the page to load
        time.sleep(5)

        # Find and click claim buttons
        game_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/p/"]')
        for link in game_links:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", link)
                time.sleep(1)
                link.click()
                logging.info('Navigated to game page')
                time.sleep(5)  # Increase wait time for page to load

                # Click the "Get" button
                get_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="purchase-cta-button"]'))
                )
                get_button.click()
                logging.info('Clicked Get button')
                time.sleep(5)  # Increase wait time for checkout page

                # Check if the order is $0
                total_price = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, '.order-summary-total__price'))
                ).text
                if total_price == '$0.00':
                    # Agree to terms if necessary
                    try:
                        agree_checkbox = driver.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
                        if agree_checkbox.is_displayed() and agree_checkbox.is_enabled():
                            agree_checkbox.click()
                            logging.info('Agreed to terms')
                    except Exception as e:
                        logging.info('No terms to agree to')

                    # Confirm purchase
                    confirm_button = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="confirm-purchase-button"]'))
                    )
                    confirm_button.click()
                    logging.info('Confirmed purchase')
                    time.sleep(5)

                    # Click "Place Order" button
                    click_place_order(driver)
                    logging.info('Placed order')
                    time.sleep(5)
                else:
                    logging.info('Skipped non-free game')

                # Navigate back to free games page
                driver.get('https://www.epicgames.com/store/free-games')
                time.sleep(5)

            except Exception as e:
                logging.error(f'Failed to claim a game: {str(e)}')
                continue

    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')
    finally:
        if driver:
            driver.quit()

def click_place_order(driver):
    try:
        # Try multiple approaches to click the button
        try:
            # Approach 1: Direct click with explicit wait
            place_order_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'PLACE ORDER')]"))
            )
            place_order_button.click()
            logging.info("Clicked Place Order button directly")
            return
        except:
            logging.info("Direct click failed, trying alternative methods")

        try:
            # Approach 2: Use JavaScript click
            place_order_button = driver.find_element(By.CSS_SELECTOR, ".payment-order-confirm__btn")
            driver.execute_script("arguments[0].click();", place_order_button)
            logging.info("Clicked Place Order button using JavaScript")
            return
        except:
            logging.info("JavaScript click failed, trying keyboard navigation")

        # Approach 3: Use TAB key to focus and ENTER to click
        active_element = driver.switch_to.active_element
        for _ in range(10):  # Try tabbing up to 10 times to find the button
            active_element.send_keys(Keys.TAB)
            time.sleep(0.5)
            # Check if we've focused the Place Order button
            focused_element = driver.switch_to.active_element
            if "PLACE ORDER" in focused_element.text:
                focused_element.send_keys(Keys.RETURN)
                logging.info("Clicked Place Order button using keyboard navigation")
                return

        logging.error("Failed to click Place Order button with all methods")
    except Exception as e:
        logging.error(f"Error in click_place_order: {str(e)}")

def claim_game(driver):
    try:
        # Try multiple methods to trigger CTRL+F
        
        # Method 1: Send directly to document
        driver.execute_script("document.execCommand('find')")
        time.sleep(1)
        
        # Method 2: If Method 1 fails, try direct key simulation
        if not driver.execute_script("return document.querySelector('.find-box')"):
            # Focus on body first
            driver.find_element(By.TAG_NAME, 'body').click()
            
            # Send Ctrl+F using different approach
            ActionChains(driver)\
                .key_down(Keys.CONTROL)\
                .send_keys('f')\
                .key_up(Keys.CONTROL)\
                .pause(1)\
                .perform()
        
        time.sleep(2)  # Wait for search dialog
        
        # Continue with search once dialog is open
        ActionChains(driver)\
            .send_keys("Purchase Order")\
            .pause(1)\
            .send_keys(Keys.RETURN)\
            .pause(1)\
            .send_keys(Keys.ESCAPE)\
            .pause(1)\
            .send_keys(Keys.TAB)\
            .pause(1)\
            .send_keys(Keys.RETURN)\
            .perform()
        
        logging.info("Completed keyboard navigation sequence")
        
        # Return to free games page
        time.sleep(3)  # Wait for any animations/loading
        driver.get('https://www.epicgames.com/store/free-games')
        time.sleep(5)  # Wait for page to load
        
        return True
        
    except Exception as e:
        logging.error(f"Failed to claim game: {e}")
        # Still return to free games page even if there's an error
        driver.get('https://www.epicgames.com/store/free-games')
        time.sleep(5)
        return False

# Main function
def main():
    claim_free_games()
    send_notification('Successfully claimed free games!')

if __name__ == '__main__':
    main()