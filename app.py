from flask import Flask, render_template, request, flash, redirect, url_for, session, Response
import os
import time
import json
import logging
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from werkzeug.utils import secure_filename
import random
from flask_socketio import SocketIO, emit
import subprocess
import re
import platform

# Set up logging
logging.basicConfig(level=logging.INFO)  # Changed from DEBUG to INFO
logger = logging.getLogger(__name__)

# Disable selenium debug logs
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app)

# Ensure the uploads directory exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt', 'csv', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_leads_file(filepath):
    """Read leads from various file formats, supporting username and name."""
    file_extension = filepath.rsplit('.', 1)[1].lower()
    leads = []
    try:
        if file_extension == 'txt':
            with open(filepath, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    # Support 'username name' or 'username\tname'
                    if '\t' in line:
                        parts = line.split('\t', 1)
                    else:
                        parts = line.split(None, 1)  # split on first whitespace
                    username = parts[0].strip()
                    name = parts[1].strip() if len(parts) > 1 else username
                    leads.append({'username': username, 'name': name})
        elif file_extension == 'csv':
            df = pd.read_csv(filepath)
            username_col = None
            name_col = None
            for col in df.columns:
                if 'user' in col.lower():
                    username_col = col
                if 'name' in col.lower():
                    name_col = col
            if username_col:
                for _, row in df.iterrows():
                    username = str(row[username_col]).strip()
                    name = str(row[name_col]).strip() if name_col and not pd.isna(row[name_col]) else username
                    leads.append({'username': username, 'name': name})
            else:
                # Fallback: use first column as username, second as name if present
                for _, row in df.iterrows():
                    username = str(row.iloc[0]).strip()
                    name = str(row.iloc[1]).strip() if len(row) > 1 else username
                    leads.append({'username': username, 'name': name})
        elif file_extension == 'xlsx':
            df = pd.read_excel(filepath)
            username_col = None
            name_col = None
            for col in df.columns:
                if 'user' in col.lower():
                    username_col = col
                if 'name' in col.lower():
                    name_col = col
            if username_col:
                for _, row in df.iterrows():
                    username = str(row[username_col]).strip()
                    name = str(row[name_col]).strip() if name_col and not pd.isna(row[name_col]) else username
                    leads.append({'username': username, 'name': name})
            else:
                for _, row in df.iterrows():
                    username = str(row.iloc[0]).strip()
                    name = str(row.iloc[1]).strip() if len(row) > 1 else username
                    leads.append({'username': username, 'name': name})
        else:
            logger.warning(f"Unsupported file extension: {file_extension}")
        logger.info(f"Leads loaded: {leads}")
        return leads
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        raise Exception(f"Error reading file: {str(e)}")

def wait_and_click(driver, by, value, timeout=10):
    """Wait for element and click it"""
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )
    element.click()
    return element

def emit_countdown(seconds):
    socketio.emit('countdown', {'seconds': seconds})
    logger.info(f"Waiting {seconds} seconds before next account...")

def get_chrome_version():
    """Get the installed Chrome version."""
    system = platform.system()
    
    if system == "Windows":
        commands = [
            'reg query "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon" /v version',
            'reg query "HKLM\\SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Google Chrome" /v version',
        ]
    elif system == "Darwin":  # macOS
        commands = [
            '/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --version'
        ]
    else:  # Linux
        commands = [
            'google-chrome --version',
            'google-chrome-stable --version',
            'chromium --version',
            'chromium-browser --version'
        ]
    
    for command in commands:
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout:
                # Extract version number
                version_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', result.stdout)
                if version_match:
                    return version_match.group(1)
        except Exception:
            continue
    
    return None

def create_fresh_chrome_options():
    """Create a fresh ChromeOptions object with advanced anti-detection features."""
    options = uc.ChromeOptions()
    
    # Basic stealth arguments
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-gpu')
    options.add_argument('--lang=en-US')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    
    # Advanced anti-detection arguments
    options.add_argument('--disable-automation')
    options.add_argument('--disable-plugins-discovery')
    options.add_argument('--disable-default-apps')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-renderer-backgrounding')
    options.add_argument('--disable-features=TranslateUI')
    options.add_argument('--disable-ipc-flooding-protection')
    options.add_argument('--no-first-run')
    options.add_argument('--no-service-autorun')
    options.add_argument('--password-store=basic')
    options.add_argument('--use-mock-keychain')
    options.add_argument('--disable-component-extensions-with-background-pages')
    options.add_argument('--disable-background-networking')
    options.add_argument('--disable-sync')
    options.add_argument('--metrics-recording-only')
    options.add_argument('--disable-default-apps')
    options.add_argument('--mute-audio')
    options.add_argument('--no-zygote')
    options.add_argument('--disable-background-mode')
    
    # Randomize window size to avoid fingerprinting
    window_sizes = [
        '--window-size=1366,768',
        '--window-size=1920,1080', 
        '--window-size=1440,900',
        '--window-size=1536,864',
        '--window-size=1280,720'
    ]
    options.add_argument(random.choice(window_sizes))
    
    # Add realistic user agent with random selection
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    ]
    options.add_argument(f'user-agent={random.choice(user_agents)}')
    
    # Skip experimental options for better compatibility
    # undetected-chromedriver handles most automation hiding automatically
    
    return options

def inject_stealth_scripts(driver):
    """Inject JavaScript to hide automation traces and make behavior more human-like."""
    scripts_applied = 0
    total_scripts = 6
    
    # Hide webdriver property (only if not already handled by undetected_chromedriver)
    try:
        driver.execute_script("""
            if (navigator.webdriver !== undefined) {
                try {
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                        configurable: true
                    });
                } catch (e) {
                    // Property might already be defined by undetected_chromedriver
                    delete navigator.webdriver;
                }
            }
        """)
        scripts_applied += 1
    except Exception as e:
        logger.debug(f"Webdriver property script failed (likely already handled): {e}")
    
    # Override plugins and languages to look more realistic
    try:
        driver.execute_script("""
            try {
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                    configurable: true
                });
            } catch (e) {
                // Ignore if already defined
            }
        """)
        scripts_applied += 1
    except Exception as e:
        logger.debug(f"Plugins script failed: {e}")
    
    # Override permissions
    try:
        driver.execute_script("""
            try {
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            } catch (e) {
                // Ignore if permissions API not available
            }
        """)
        scripts_applied += 1
    except Exception as e:
        logger.debug(f"Permissions script failed: {e}")
    
    # Hide automation indicators
    try:
        driver.execute_script("""
            try {
                if (!window.chrome) {
                    window.chrome = {
                        runtime: {},
                    };
                }
            } catch (e) {
                // Ignore if already defined
            }
        """)
        scripts_applied += 1
    except Exception as e:
        logger.debug(f"Chrome object script failed: {e}")
    
    # Override the isConnected property
    try:
        driver.execute_script("""
            try {
                Object.defineProperty(HTMLElement.prototype, 'isConnected', {
                    get() {
                        return true;
                    },
                    configurable: true
                });
            } catch (e) {
                // Ignore if already defined
            }
        """)
        scripts_applied += 1
    except Exception as e:
        logger.debug(f"isConnected script failed: {e}")
    
    # Add realistic screen properties
    try:
        driver.execute_script("""
            try {
                Object.defineProperty(screen, 'availTop', {
                    get: () => 0,
                    configurable: true
                });
                Object.defineProperty(screen, 'availLeft', {
                    get: () => 0,
                    configurable: true
                });
            } catch (e) {
                // Ignore if already defined
            }
        """)
        scripts_applied += 1
    except Exception as e:
        logger.debug(f"Screen properties script failed: {e}")
    
    logger.info(f"Successfully injected {scripts_applied}/{total_scripts} stealth scripts")

def simulate_human_behavior(driver, action_type="general"):
    """Simulate human-like behavior with random mouse movements and delays."""
    try:
        if action_type == "before_login":
            # Simulate reading the page
            time.sleep(random.uniform(2, 4))
            
            # Random scroll to simulate looking around
            driver.execute_script("window.scrollTo(0, Math.floor(Math.random() * 200));")
            time.sleep(random.uniform(1, 2))
            
        elif action_type == "before_profile_visit":
            # Simulate human hesitation before visiting profile
            time.sleep(random.uniform(1, 3))
            
            # Random small scroll
            driver.execute_script("window.scrollTo(0, Math.floor(Math.random() * 100));")
            time.sleep(random.uniform(0.5, 1.5))
            
        elif action_type == "before_message":
            # Simulate reading the profile
            time.sleep(random.uniform(3, 6))
            
            # Random scroll on profile
            driver.execute_script("window.scrollTo(0, Math.floor(Math.random() * 300));")
            time.sleep(random.uniform(1, 2))
            
            # Scroll back up
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(random.uniform(1, 2))
            
    except Exception as e:
        logger.warning(f"Error in human behavior simulation: {e}")

def human_like_typing(element, text, driver):
    """Type text in a human-like manner with realistic delays and occasional corrections."""
    try:
        # Clear the field first
        element.clear()
        time.sleep(random.uniform(0.3, 0.8))
        
        # Sometimes make a "mistake" and correct it for more realism
        if random.random() < 0.15:  # 15% chance of making a typo
            # Type a wrong character first
            wrong_chars = ['x', 'z', 'q', 'w']
            element.send_keys(random.choice(wrong_chars))
            time.sleep(random.uniform(0.2, 0.5))
            
            # Backspace to correct
            element.send_keys(Keys.BACKSPACE)
            time.sleep(random.uniform(0.3, 0.7))
        
        # Type the actual message with human-like variations
        for i, char in enumerate(text):
            element.send_keys(char)
            
            # Vary typing speed - slower at beginning, faster in middle, slower at end
            if i < len(text) * 0.2:  # First 20%
                delay = random.uniform(0.15, 0.35)
            elif i < len(text) * 0.8:  # Middle 60%
                delay = random.uniform(0.08, 0.20)
            else:  # Last 20%
                delay = random.uniform(0.12, 0.30)
            
            # Occasionally pause longer (thinking)
            if random.random() < 0.05:  # 5% chance
                delay += random.uniform(0.5, 1.2)
            
            # Pause longer after punctuation
            if char in '.,!?':
                delay += random.uniform(0.2, 0.5)
            
            time.sleep(delay)
        
        # Sometimes pause before sending (reviewing message)
        if random.random() < 0.3:  # 30% chance
            time.sleep(random.uniform(1, 3))
            
    except Exception as e:
        logger.warning(f"Error in human-like typing: {e}")
        # Fallback to simple typing
        element.clear()
        element.send_keys(text)

def visit_profile_naturally(driver, username, wait):
    """Visit a profile using different methods to appear more natural."""
    methods = ['direct_url', 'search']
    method = random.choice(methods)
    
    try:
        if method == 'search' and random.random() < 0.4:  # 40% chance to use search
            logger.info(f"Using search method to find {username}")
            
            # Go to Instagram home first
            driver.get('https://www.instagram.com/')
            time.sleep(random.uniform(2, 4))
            
            # Re-inject stealth scripts
            inject_stealth_scripts(driver)
            
            # Find and click search
            search_selectors = [
                "//input[@placeholder='Search']",
                "//input[@aria-label='Search input']",
                "//input[contains(@placeholder, 'Search')]"
            ]
            
            search_input = None
            for selector in search_selectors:
                try:
                    search_input = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    break
                except:
                    continue
            
            if search_input:
                search_input.click()
                time.sleep(random.uniform(0.5, 1))
                
                # Type username with human-like behavior
                human_like_typing(search_input, username, driver)
                time.sleep(random.uniform(1, 2))
                
                # Wait for search results and click on the profile
                try:
                    profile_link = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(@href, '/{username}/')]")))
                    time.sleep(random.uniform(1, 2))
                    profile_link.click()
                    time.sleep(random.uniform(2, 4))
                    return True
                except:
                    logger.info(f"Search method failed for {username}, falling back to direct URL")
                    
        # Fallback to direct URL method
        logger.info(f"Using direct URL method for {username}")
        profile_url = f'https://www.instagram.com/{username.strip()}/'
        driver.get(profile_url)
        time.sleep(random.uniform(3, 5))
        return True
        
    except Exception as e:
        logger.warning(f"Error in visit_profile_naturally: {e}")
        # Final fallback
        profile_url = f'https://www.instagram.com/{username.strip()}/'
        driver.get(profile_url)
        time.sleep(random.uniform(3, 5))
        return True

def send_messages_old_unused(username, password, leads_file, message_template, delay_seconds=30):
    options = create_fresh_chrome_options()
    
    driver = None # Initialize driver to None for robust finally block
    results_list = [] 
    
    try:
        # Initialize Chrome driver with automatic version detection to avoid version mismatch
        try:
            driver = uc.Chrome(options=options, version_main=None)
            logger.info("Successfully initialized Chrome driver with auto-detection")
        except Exception as e:
            logger.warning(f"Failed to initialize with auto-detection, trying with detected Chrome version: {e}")
            # Get the Chrome version and extract major version
            chrome_version = get_chrome_version()
            if chrome_version:
                major_version = int(chrome_version.split('.')[0])
                logger.info(f"Detected Chrome version: {chrome_version}, using major version: {major_version}")
            else:
                major_version = None
                logger.warning("Could not detect Chrome version, trying with no version specified")
            
            # Create fresh options again in case the previous attempt corrupted them
            options = create_fresh_chrome_options()
            driver = uc.Chrome(options=options, version_main=major_version)
            logger.info(f"Successfully initialized Chrome driver with version {major_version}")
        
        wait = WebDriverWait(driver, 20) # Standard wait
        short_wait = WebDriverWait(driver, 5) # Shorter wait for optional elements

        driver.get('https://www.instagram.com/')
        time.sleep(random.uniform(3,5))
        
        try:
            logger.info("Attempting login...")
            username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
            username_input.clear(); password_input.clear()
            username_input.send_keys(username); time.sleep(random.uniform(0.5, 1))
            password_input.send_keys(password); time.sleep(random.uniform(0.5, 1))
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()
            time.sleep(random.uniform(4,6)) # Wait for login process
            
            # Handle "Not Now" for Save Login Info and Turn On Notifications
            not_now_xpaths = [
                "//button[text()='Not Now']", 
                "//div[@role='button' and text()='Not Now']",
                "//button[contains(., 'Not Now')]"
            ]
            for _ in range(2): # Try to click "Not Now" twice for potential multiple popups
                for xpath in not_now_xpaths:
                    try:
                        not_now_btn = short_wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                        not_now_btn.click()
                        logger.info(f"Clicked 'Not Now' button using XPath: {xpath}")
                        time.sleep(random.uniform(1,2))
                    except: # TimeoutException or other, just means button not found or not clickable
                        pass # Continue to next xpath or next attempt

            # Verify login by checking for common post-login elements
            home_elements_xpath = "//svg[@aria-label='Home'] | //svg[@aria-label='Direct'] | //img[contains(@alt, 'profile') or contains(@alt, 'Profile')] | //span[@data-testid='user-avatar']"
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, home_elements_xpath)))
                logger.info("Login appears successful.")
            except TimeoutException:
                if "instagram.com/accounts/login" in driver.current_url:
                    raise Exception("Login failed. Still on login page after attempts.")
                else:
                    logger.warning("Could not definitively verify login with home elements, but not on login page. Proceeding cautiously.")

        except Exception as e:
            logger.error(f"Login process failed: {e}")
            raise Exception(f"Failed to login or handle initial popups: {e}")

        leads = read_leads_file(leads_file)
        total_leads = len(leads)
        session['total_leads'] = total_leads # For results page to know total in advance

        socketio.emit('initial_stats', {
            'total_leads': total_leads, 'sent': 0, 'failed': 0, 'remaining': total_leads
        })

        for index, lead in enumerate(leads, 1):
            lead_username = lead['username']
            lead_name = lead['name']
            personalized_message = message_template.replace('{name}', lead_name)
            current_lead_info = {'username': lead_username, 'current_count': index, 'total_count': total_leads}
            socketio.emit('current_lead', current_lead_info)
            
            lead_processed_data = {
                'username': lead_username, 'success': False, 'message': 'Lead processing started',
                'total_leads': total_leads, 'processed_count': index
            }
            found_btn_and_messaged = False

            try:
                # Simulate human behavior before visiting profile
                simulate_human_behavior(driver, "before_profile_visit")
                
                # Use natural profile visiting method
                visit_profile_naturally(driver, lead_username, wait)
                
                # Re-inject stealth scripts on new page
                inject_stealth_scripts(driver)
                
                # Simulate human behavior on profile (reading, scrolling)
                simulate_human_behavior(driver, "before_message")
                
                time.sleep(random.uniform(3, 5))  # Allow page to load properly

                # Try to find and click the Message button with multiple strategies
                found_msg_button = False
                
                # Strategy 1: Look for button/div with exact "Message" text
                message_selectors = [
                    "//div[text()='Message']",
                    "//button[text()='Message']", 
                    "//a[text()='Message']"
                ]
                
                for selector in message_selectors:
                    try:
                        msg_btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", msg_btn)
                        time.sleep(1)
                        msg_btn.click()
                        found_msg_button = True
                        logger.info(f"Lead {lead_username}: Found Message button with selector: {selector}")
                        break
                    except:
                        continue
                
                # Strategy 2: If exact match fails, try contains
                if not found_msg_button:
                    contains_selectors = [
                        "//div[contains(text(), 'Message')]",
                        "//button[contains(text(), 'Message')]",
                        "//a[contains(text(), 'Message')]"
                    ]
                    
                    for selector in contains_selectors:
                        try:
                            msg_btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", msg_btn)
                            time.sleep(1)
                            msg_btn.click()
                            found_msg_button = True
                            logger.info(f"Lead {lead_username}: Found Message button with contains selector: {selector}")
                            break
                        except:
                            continue
                
                # Strategy 3: Last resort - find all elements with "Message" and try clicking them
                if not found_msg_button:
                    try:
                        logger.info(f"Lead {lead_username}: Trying fallback search for Message button...")
                        all_message_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Message')]")
                        for element in all_message_elements:
                            try:
                                if element.is_displayed() and element.is_enabled():
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                                    time.sleep(0.5)
                                    element.click()
                                    found_msg_button = True
                                    logger.info(f"Lead {lead_username}: Found Message button using fallback method")
                                    break
                            except:
                                continue
                    except Exception as e:
                        logger.debug(f"Lead {lead_username}: Fallback failed: {str(e)}")
                
                if not found_msg_button:
                    lead_message = "Message button not found on profile"
                    raise Exception(lead_message)

                # Wait for message composer to load
                time.sleep(random.uniform(3, 5))
                
                # Find the message input field with multiple strategies
                msg_input = None
                input_selectors = [
                    "//textarea[@placeholder='Message...']",
                    "//div[@contenteditable='true'][@role='textbox']",
                    "//div[@contenteditable='true'][contains(@aria-label, 'Message')]",
                    "//textarea[contains(@placeholder, 'Message')]",
                    "//div[@contenteditable='true']",
                    "//textarea[@aria-label='Message']"
                ]
                
                for selector in input_selectors:
                    try:
                        msg_input = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        if msg_input.is_displayed():
                            logger.info(f"Lead {lead_username}: Found message input with selector: {selector}")
                            break
                    except:
                        continue
                
                if not msg_input:
                    lead_message = "Message input field not found"
                    raise Exception(lead_message)

                # Click and focus on the input field
                try:
                    driver.execute_script("arguments[0].focus();", msg_input)
                    msg_input.click()
                    time.sleep(1)
                    msg_input.clear()
                    time.sleep(0.5)
                    
                    # Type the message character by character
                    logger.info(f"Lead {lead_username}: Typing message...")
                    human_like_typing(msg_input, personalized_message, driver)
                    
                    time.sleep(1)
                    logger.info(f"Lead {lead_username}: Message typed successfully")
                    
                except Exception as e:
                    logger.error(f"Lead {lead_username}: Error typing message: {str(e)}")
                    lead_message = f"Error typing message: {str(e)}"
                    raise Exception(lead_message)

                # Try to send the message
                send_success = False
                send_selectors = [
                    "//div[@role='button'][text()='Send']",
                    "//button[text()='Send']",
                    "//div[text()='Send'][@role='button']",
                    "//button[contains(text(), 'Send')]"
                ]
                
                for selector in send_selectors:
                    try:
                        send_btn = short_wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        send_btn.click()
                        send_success = True
                        logger.info(f"Lead {lead_username}: Message sent using selector: {selector}")
                        break
                    except:
                        continue
                
                # If send button not found, try Enter key
                if not send_success:
                    try:
                        msg_input.send_keys(Keys.RETURN)
                        send_success = True
                        logger.info(f"Lead {lead_username}: Message sent using Enter key")
                    except Exception as e:
                        logger.error(f"Lead {lead_username}: Failed to send with Enter key: {str(e)}")
                
                if send_success:
                    time.sleep(random.uniform(2, 4))  # Wait for message to send
                    lead_success = True
                    lead_message = "Message sent successfully"
                    results_list.append((lead_username, True, lead_message))
                    lead_processed_data.update({'success': True, 'message': lead_message})
                    found_btn_and_messaged = True
                else:
                    lead_message = "Failed to find send button or send message"
                    raise Exception(lead_message)

            except Exception as e_lead:
                error_msg_for_lead = f"Error processing {lead_username}: {str(e_lead)}"
                logger.error(error_msg_for_lead)
                # Ensure we record a failure if it wasn't a skip case handled above
                if not any(r[0] == lead_username for r in results_list): # if not already added (e.g. by skip logic)
                    results_list.append((lead_username, False, error_msg_for_lead))
                lead_processed_data.update({'success': False, 'message': error_msg_for_lead})
            
            finally:
                # This block executes for every lead, regardless of success or failure within the try block for this lead.
                # We use lead_processed_data which holds the latest status for this lead.
                socketio.emit('lead_processed', lead_processed_data)
                
                # Delay unless it was the very last lead
                if index < total_leads:
                    logger.info(f"Initiating delay of {delay_seconds}s before next lead.")
                    for sec in range(delay_seconds, 0, -1):
                        emit_countdown(sec)
                        time.sleep(1)
    
    except Exception as e_main:
        main_error_msg = f"A critical error occurred: {str(e_main)}"
        logger.error(main_error_msg, exc_info=True)
        socketio.emit('script_error', {'error_message': main_error_msg})
        # results_list might be partially populated, so it's good to return it for any partial results
    
    finally:
        if driver:
            try:
                # Comprehensive cleanup to prevent ChromeOptions reuse issues
                driver.delete_all_cookies()
                driver.execute_script("window.localStorage.clear();")
                driver.execute_script("window.sessionStorage.clear();")
            except Exception as cleanup_error:
                logger.warning(f"Error during driver cleanup for {username}: {cleanup_error}")
            finally:
                driver.quit()
                logger.info(f"WebDriver quit for account: {username}")
                
                # Force garbage collection to ensure clean state for next account
                import gc
                gc.collect()
                
                # Small delay to ensure driver is fully cleaned up
                time.sleep(random.uniform(1, 2))
    
    final_summary_message = f"Campaign finished! Processed: {len(results_list)}/{total_leads}, Sent: {sum(1 for _, s, _ in results_list if s)}, Failed: {sum(1 for _, s, _ in results_list if not s)}"
    logger.info(final_summary_message)
    socketio.emit('all_leads_processed', {'message': final_summary_message, 'results_summary': results_list})
    return results_list

@app.route('/', methods=['GET', 'POST'])
def index():
    logger.info("Index route accessed")
    if request.method == 'POST':
        logger.info("POST request received for multi-account setup")
        session.clear() # Clear any previous session data for a fresh start

        try:
            num_accounts = int(request.form.get('num_accounts_to_submit', 0))
            master_message_template = request.form.get('message_template')
            delay_seconds = int(request.form.get('delay_seconds', 30))

            if not master_message_template or delay_seconds < 1:
                flash('Master message template and a valid delay are required.', 'danger')
                return redirect(request.url)
            
            if num_accounts == 0:
                flash('No accounts submitted. Please add at least one account.', 'warning')
                return redirect(request.url)

            accounts_data = []
            total_leads_for_campaign = 0

            for i in range(num_accounts):
                username = request.form.get(f'username_{i}')
                password = request.form.get(f'password_{i}')
                leads_file_obj = request.files.get(f'leads_file_{i}')

                if not all([username, password, leads_file_obj]):
                    flash(f'Missing username, password, or leads file for Account #{i+1}.', 'danger')
                    return redirect(request.url)

                if leads_file_obj.filename == '':
                    flash(f'No leads file selected for Account #{i+1}.', 'danger')
                    return redirect(request.url)

                if allowed_file(leads_file_obj.filename):
                    filename = secure_filename(f"account_{i}_{leads_file_obj.filename}")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    leads_file_obj.save(filepath)
                    
                    current_account_leads = read_leads_file(filepath)
                    if not current_account_leads:
                        flash(f'Leads file for Account #{i+1} ({username}) is empty or unreadable.', 'warning')
                        # Optionally, decide if this is a hard stop or just skip this account
                        # For now, let's make it a hard stop to ensure data integrity for demo
                        return redirect(request.url)
                    
                    total_leads_for_campaign += len(current_account_leads)

                    accounts_data.append({
                        'username': username,
                        'password': password, # WARNING: Storing passwords in session is not secure for production
                        'leads_filepath': filepath,
                        'original_leads_filename': leads_file_obj.filename,
                        'parsed_leads': current_account_leads # Store parsed leads for easy access
                    })
                else:
                    flash(f'Invalid file type for leads in Account #{i+1}. Please use .txt, .csv, or .xlsx.', 'danger')
                    return redirect(request.url)
            
            if not accounts_data:
                flash('No valid accounts were processed. Please check your inputs.', 'danger')
                return redirect(request.url)

            # Store campaign data in session
            session['campaign_accounts'] = accounts_data
            session['master_message_template'] = master_message_template
            session['delay_seconds'] = delay_seconds
            session['total_campaign_leads'] = total_leads_for_campaign
            session.pop('campaign_results', None) # Clear any old campaign results

            logger.info(f"Campaign configured with {len(accounts_data)} accounts and {total_leads_for_campaign} total leads.")
            return redirect(url_for('results')) # Redirect to results page to start the campaign

        except Exception as e:
            logger.error(f"Error processing multi-account form: {e}", exc_info=True)
            flash(f'An unexpected error occurred: {str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template('index.html')

@socketio.on('start_messaging_task')
def handle_start_messaging_task():
    logger.info("Socket event 'start_messaging_task' received for multi-account campaign.")
    
    campaign_accounts = session.get('campaign_accounts')
    master_message_template = session.get('master_message_template')
    delay_seconds = session.get('delay_seconds', 30)  # Default 30 seconds delay
    total_campaign_leads = session.get('total_campaign_leads', 0)
    messages_per_account = 50  # Set limit to 50 messages per account

    if not all([campaign_accounts, master_message_template, isinstance(delay_seconds, int)]):
        logger.error("Missing critical campaign data in session to start messaging task.")
        socketio.emit('script_error', {'error_message': 'Session data missing. Please restart campaign setup.'})
        return

    # Emit initial stats for the whole campaign
    socketio.emit('initial_campaign_stats', {
        'total_accounts': len(campaign_accounts),
        'total_leads': total_campaign_leads,
        'overall_sent': 0,
        'overall_failed': 0
    })
    
    campaign_overall_results = []
    overall_sent_count = 0
    overall_failed_count = 0
    overall_processed_leads_count = 0

    for acc_idx, account in enumerate(campaign_accounts):
        socketio.emit('account_processing_start', {
            'account_username': account['username'], 
            'account_index': acc_idx + 1,
            'total_accounts': len(campaign_accounts),
            'leads_for_this_account': min(messages_per_account, len(account['parsed_leads']))
        })
        
        driver = None
        current_account_results = []
        account_sent_count = 0

        try:
            logger.info(f"Starting processing for account: {account['username']}")
            
            # Configure Chrome options for optimal performance and stealth
            options = create_fresh_chrome_options()
            
            # Initialize Chrome driver with automatic version detection to avoid version mismatch
            try:
                # Force garbage collection to ensure clean state
                import gc
                gc.collect()
                
                # Add a small random delay to prevent collision between drivers
                time.sleep(random.uniform(1, 3))
                
                driver = uc.Chrome(options=options, version_main=None)
                logger.info(f"Successfully initialized Chrome driver with auto-detection for account: {account['username']}")
            except Exception as e:
                logger.warning(f"Failed to initialize with auto-detection for {account['username']}, trying with detected Chrome version: {e}")
                try:
                    # Get the Chrome version and extract major version
                    chrome_version = get_chrome_version()
                    if chrome_version:
                        major_version = int(chrome_version.split('.')[0])
                        logger.info(f"Detected Chrome version: {chrome_version}, using major version: {major_version}")
                    else:
                        major_version = None
                        logger.warning("Could not detect Chrome version, trying with no version specified")
                    
                    # Create fresh options again in case the previous attempt corrupted them
                    options = create_fresh_chrome_options()
                    driver = uc.Chrome(options=options, version_main=major_version)
                    logger.info(f"Successfully initialized Chrome driver with version {major_version} for account: {account['username']}")
                except Exception as e2:
                    logger.error(f"Failed to initialize Chrome driver for account {account['username']}: {e2}")
                    socketio.emit('script_error', {
                        'error_message': f"Chrome driver initialization failed for {account['username']}. Skipping this account. Error: {str(e2)}"
                    })
                    continue  # Skip this account and move to next one
            
            wait = WebDriverWait(driver, 20) # Standard wait
            short_wait = WebDriverWait(driver, 7)

            # Clear cookies and cache before login
            driver.delete_all_cookies()
            
            # Perform login with human-like behavior
            driver.get('https://www.instagram.com/')
            
            # Inject stealth scripts immediately after page load
            inject_stealth_scripts(driver)
            
            # Simulate human behavior before login
            simulate_human_behavior(driver, "before_login")
            
            time.sleep(random.uniform(3,5))  # Wait longer for initial page load
            
            # Simulate human-like typing and interaction
            username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
            
            # Clear fields with human-like behavior
            username_input.click()
            time.sleep(random.uniform(0.5, 1))
            username_input.clear()
            time.sleep(random.uniform(0.5, 1))
            
            # Type username with random delays
            for char in account['username']:
                username_input.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            time.sleep(random.uniform(0.8, 1.5))
            
            # Type password with random delays
            password_input.click()
            time.sleep(random.uniform(0.5, 1))
            password_input.clear()
            time.sleep(random.uniform(0.5, 1))
            
            for char in account['password']:
                password_input.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            time.sleep(random.uniform(0.8, 1.5))
            
            # Click login button
            login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", login_button)
            time.sleep(random.uniform(0.5, 1))
            login_button.click()
            
            # Wait longer after login attempt
            time.sleep(random.uniform(5,7))
            
            # Re-inject stealth scripts after login (in case page refreshed)
            inject_stealth_scripts(driver)

            # Handle "Not Now" popups
            not_now_xpaths = ["//button[text()='Not Now']", "//div[@role='button' and text()='Not Now']"]
            for _ in range(2):
                for xpath in not_now_xpaths:
                    try: 
                        short_wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
                        time.sleep(1)
                    except: 
                        pass

            # Process leads for this account (limited to 50)
            leads_to_process = account['parsed_leads'][:messages_per_account]
            for lead_idx, lead in enumerate(leads_to_process):
                lead_username = lead['username']
                lead_name = lead['name']
                personalized_message = master_message_template.replace('{name}', lead_name)
                if account_sent_count >= messages_per_account:
                    logger.info(f"Reached 50 message limit for account {account['username']}")
                    break

                overall_processed_leads_count += 1
                socketio.emit('current_lead_update', {
                    'account_username': account['username'], 
                    'lead_username': lead_username, 
                    'lead_in_account_count': lead_idx + 1, 
                    'total_leads_in_account': len(leads_to_process),
                    'overall_progress_percent': int((overall_processed_leads_count / total_campaign_leads) * 100) if total_campaign_leads > 0 else 0
                })
                
                lead_success = False
                lead_message = "Processing..."

                try:
                    # Simulate human behavior before visiting profile
                    simulate_human_behavior(driver, "before_profile_visit")
                    
                    # Use natural profile visiting method
                    visit_profile_naturally(driver, lead_username, wait)
                    
                    # Re-inject stealth scripts on new page
                    inject_stealth_scripts(driver)
                    
                    # Simulate human behavior on profile (reading, scrolling)
                    simulate_human_behavior(driver, "before_message")
                    
                    time.sleep(random.uniform(3, 5))  # Allow page to load properly

                    # Try to find and click the Message button with multiple strategies
                    found_msg_button = False
                    
                    # Strategy 1: Look for button/div with exact "Message" text
                    message_selectors = [
                        "//div[text()='Message']",
                        "//button[text()='Message']", 
                        "//a[text()='Message']"
                    ]
                    
                    for selector in message_selectors:
                        try:
                            msg_btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", msg_btn)
                            time.sleep(1)
                            msg_btn.click()
                            found_msg_button = True
                            logger.info(f"Lead {lead_username}: Found Message button with selector: {selector}")
                            break
                        except:
                            continue
                    
                    # Strategy 2: If exact match fails, try contains
                    if not found_msg_button:
                        contains_selectors = [
                            "//div[contains(text(), 'Message')]",
                            "//button[contains(text(), 'Message')]",
                            "//a[contains(text(), 'Message')]"
                        ]
                        
                        for selector in contains_selectors:
                            try:
                                msg_btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", msg_btn)
                                time.sleep(1)
                                msg_btn.click()
                                found_msg_button = True
                                logger.info(f"Lead {lead_username}: Found Message button with contains selector: {selector}")
                                break
                            except:
                                continue
                    
                    # Strategy 3: Last resort - find all elements with "Message" and try clicking them
                    if not found_msg_button:
                        try:
                            logger.info(f"Lead {lead_username}: Trying fallback search for Message button...")
                            all_message_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Message')]")
                            for element in all_message_elements:
                                try:
                                    if element.is_displayed() and element.is_enabled():
                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                                        time.sleep(0.5)
                                        element.click()
                                        found_msg_button = True
                                        logger.info(f"Lead {lead_username}: Found Message button using fallback method")
                                        break
                                except:
                                    continue
                        except Exception as e:
                            logger.debug(f"Lead {lead_username}: Fallback failed: {str(e)}")
                    
                    if not found_msg_button:
                        lead_message = "Message button not found on profile"
                        raise Exception(lead_message)

                    # Wait for message composer to load
                    time.sleep(random.uniform(3, 5))
                    
                    # Find the message input field with multiple strategies
                    msg_input = None
                    input_selectors = [
                        "//textarea[@placeholder='Message...']",
                        "//div[@contenteditable='true'][@role='textbox']",
                        "//div[@contenteditable='true'][contains(@aria-label, 'Message')]",
                        "//textarea[contains(@placeholder, 'Message')]",
                        "//div[@contenteditable='true']",
                        "//textarea[@aria-label='Message']"
                    ]
                    
                    for selector in input_selectors:
                        try:
                            msg_input = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                            if msg_input.is_displayed():
                                logger.info(f"Lead {lead_username}: Found message input with selector: {selector}")
                                break
                        except:
                            continue
                    
                    if not msg_input:
                        lead_message = "Message input field not found"
                        raise Exception(lead_message)

                    # Click and focus on the input field
                    try:
                        driver.execute_script("arguments[0].focus();", msg_input)
                        msg_input.click()
                        time.sleep(1)
                        msg_input.clear()
                        time.sleep(0.5)
                        
                        # Type the message character by character
                        logger.info(f"Lead {lead_username}: Typing message...")
                        human_like_typing(msg_input, personalized_message, driver)
                        
                        time.sleep(1)
                        logger.info(f"Lead {lead_username}: Message typed successfully")
                        
                    except Exception as e:
                        logger.error(f"Lead {lead_username}: Error typing message: {str(e)}")
                        lead_message = f"Error typing message: {str(e)}"
                        raise Exception(lead_message)

                    # Try to send the message
                    send_success = False
                    send_selectors = [
                        "//div[@role='button'][text()='Send']",
                        "//button[text()='Send']",
                        "//div[text()='Send'][@role='button']",
                        "//button[contains(text(), 'Send')]"
                    ]
                    
                    for selector in send_selectors:
                        try:
                            send_btn = short_wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                            send_btn.click()
                            send_success = True
                            logger.info(f"Lead {lead_username}: Message sent using selector: {selector}")
                            break
                        except:
                            continue
                    
                    # If send button not found, try Enter key
                    if not send_success:
                        try:
                            msg_input.send_keys(Keys.RETURN)
                            send_success = True
                            logger.info(f"Lead {lead_username}: Message sent using Enter key")
                        except Exception as e:
                            logger.error(f"Lead {lead_username}: Failed to send with Enter key: {str(e)}")
                    
                    if send_success:
                        time.sleep(random.uniform(2, 4))  # Wait for message to send
                        lead_success = True
                        lead_message = "Message sent successfully"
                        overall_sent_count += 1
                        account_sent_count += 1

                        # Add human-like delay between messages with variation
                        actual_delay = delay_seconds
                        
                        # Add random variation (±20%)
                        variation = random.uniform(-0.2, 0.2)
                        actual_delay = int(actual_delay * (1 + variation))
                        
                        # Occasionally take longer breaks (every 5-10 messages)
                        if account_sent_count % random.randint(5, 10) == 0:
                            extra_break = random.randint(30, 90)
                            actual_delay += extra_break
                            logger.info(f"Taking extended break: {extra_break}s (total: {actual_delay}s)")
                        
                        # Ensure minimum delay
                        actual_delay = max(actual_delay, 15)
                        
                        logger.info(f"Delaying {actual_delay}s before next message")
                        for sec in range(actual_delay, 0, -1):
                            socketio.emit('countdown', {'seconds': sec})
                            time.sleep(1)
                    else:
                        lead_message = "Failed to find send button or send message"
                        raise Exception(lead_message)

                except Exception as e_lead:
                    logger.error(f"Error processing lead {lead_username} for account {account['username']}: {e_lead}")
                    lead_message = str(e_lead)[:100]
                    overall_failed_count += 1
                
                current_account_results.append((lead_username, lead_success, lead_message))
                result_entry = (account['username'], lead_username, lead_success, lead_message)
                campaign_overall_results.append(result_entry)
                
                socketio.emit('lead_processed', {
                    'account_username': account['username'],
                    'username': lead_username,
                    'success': lead_success,
                    'message': lead_message,
                    'overall_processed_leads': overall_processed_leads_count,
                    'overall_sent': overall_sent_count,
                    'overall_failed': overall_failed_count,
                    'total_campaign_leads': total_campaign_leads
                })

        except Exception as e:
            logger.error(f"Error processing account {account['username']}: {e}")
            socketio.emit('script_error', {'error_message': f"Error with account {account['username']}: {str(e)}"})
        
        finally:
            if driver:
                try:
                    # Comprehensive cleanup to prevent ChromeOptions reuse issues
                    driver.delete_all_cookies()
                    driver.execute_script("window.localStorage.clear();")
                    driver.execute_script("window.sessionStorage.clear();")
                except Exception as cleanup_error:
                    logger.warning(f"Error during driver cleanup for {account['username']}: {cleanup_error}")
                finally:
                    driver.quit()
                    logger.info(f"WebDriver quit for account: {account['username']}")
                    
                    # Force garbage collection to ensure clean state for next account
                    import gc
                    gc.collect()
                    
                    # Small delay to ensure driver is fully cleaned up
                    time.sleep(random.uniform(1, 2))
            
            socketio.emit('account_processing_complete', {
                'account_username': account['username'],
                'account_index': acc_idx + 1,
                'sent_count': account_sent_count,
                'failed_count': len(current_account_results) - account_sent_count,
                'results_for_account': current_account_results
            })
            
            # Delay between accounts if it's not the last account
            if acc_idx < len(campaign_accounts) - 1:
                inter_account_delay = delay_seconds * 2
                logger.info(f"Delaying {inter_account_delay}s before starting next account.")
                for sec in range(inter_account_delay, 0, -1):
                    socketio.emit('countdown', {'seconds': sec})
                    time.sleep(1)

    session['campaign_results'] = campaign_overall_results
    final_summary = f"Multi-account campaign finished! Total Leads: {total_campaign_leads}, Sent: {overall_sent_count}, Failed: {overall_failed_count}"
    logger.info(final_summary)
    socketio.emit('campaign_complete', {
        'message': final_summary,
        'overall_sent': overall_sent_count,
        'overall_failed': overall_failed_count,
        'overall_results': campaign_overall_results
    })
    logger.info("handle_start_messaging_task completed.")

@app.route('/results')
def results():
    logger.info("Results route accessed for multi-account campaign.")
    campaign_data_in_session = session.get('campaign_accounts')
    total_campaign_leads_from_session = session.get('total_campaign_leads', 0)
    raw_previous_results = session.get('campaign_results', []) 

    # Transform previous results for the template
    formatted_previous_results = []
    if raw_previous_results:
        for acc_user, lead_user, l_success, l_message in raw_previous_results:
            formatted_previous_results.append({
                'timestamp': 'Prev. Run',
                'account': acc_user,
                'lead': lead_user,
                'message': l_message,
                'type': 'success' if l_success else 'error'
            })

    initial_message = "Preparing your multi-account campaign..."
    if not campaign_data_in_session and not formatted_previous_results:
         initial_message = "Please set up a new campaign from the home page."
    elif formatted_previous_results and not campaign_data_in_session: # Only previous results exist, campaign not active
        sent_count = sum(1 for r in formatted_previous_results if r['type'] == 'success')
        failed_count = len(formatted_previous_results) - sent_count
        initial_message = f"Previous Campaign Finished! Total Leads: {len(formatted_previous_results)}, Sent: {sent_count}, Failed: {failed_count}"
    # If campaign_data_in_session exists, a new campaign is configured and SocketIO will take over.
    
    return render_template('results.html', 
                           message=initial_message, 
                           total_leads_overall=total_campaign_leads_from_session, 
                           results_log_initial = formatted_previous_results
                           )

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    try:
        logger.info("Attempting to start SocketIO server on port 5000...")
        # Start with localhost and port 5000 for better compatibility
        socketio.run(app, host='127.0.0.1', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        print(f"Error starting application: {e}")
        input("Press Enter to exit...") 