#!/usr/bin/env python3
"""
Standalone Anti-Detection Test Script for InstaDM Pro
Tests stealth features without importing Flask dependencies.
"""

import undetected_chromedriver as uc
import time
import random

def create_stealth_chrome_options():
    """Create Chrome options with advanced anti-detection features."""
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
    options.add_argument('--mute-audio')
    options.add_argument('--no-zygote')
    options.add_argument('--disable-background-mode')
    
    # Randomize window size
    window_sizes = [
        '--window-size=1366,768',
        '--window-size=1920,1080', 
        '--window-size=1440,900',
        '--window-size=1536,864',
        '--window-size=1280,720'
    ]
    options.add_argument(random.choice(window_sizes))
    
    # Add realistic user agent
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    ]
    options.add_argument(f'user-agent={random.choice(user_agents)}')
    
    # Skip experimental options for compatibility
    # These will be handled by undetected-chromedriver automatically
    
    return options

def inject_stealth_scripts(driver):
    """Inject JavaScript to hide automation traces."""
    scripts_applied = 0
    total_scripts = 4
    
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
        print(f"   ⚠️  Webdriver property script failed (likely already handled): {e}")
    
    # Override plugins
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
        print(f"   ⚠️  Plugins script failed: {e}")
    
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
        print(f"   ⚠️  Permissions script failed: {e}")
    
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
        print(f"   ⚠️  Chrome object script failed: {e}")
    
    if scripts_applied == total_scripts:
        print("   ✅ All stealth scripts injected successfully")
        return True
    else:
        print(f"   ✅ {scripts_applied}/{total_scripts} stealth scripts injected successfully")
        return scripts_applied > 0

def test_instagram_stealth():
    """Test stealth features specifically for Instagram."""
    print("🛡️  Testing Instagram Anti-Detection")
    print("=" * 50)
    
    driver = None
    test_results = {
        'chrome_creation': False,
        'stealth_injection': False,
        'webdriver_hidden': False,
        'instagram_access': False,
        'automation_hidden': False
    }
    
    try:
        print("\n🔧 Creating stealth Chrome instance...")
        options = create_stealth_chrome_options()
        
        # Add headless for testing (remove this for actual use)
        # options.add_argument('--headless')
        
        try:
            driver = uc.Chrome(options=options, version_main=None)
            test_results['chrome_creation'] = True
            print("   ✅ Chrome instance created successfully with auto-detection")
        except Exception as e:
            print(f"   ⚠️  Auto-detection failed, trying with detected Chrome version: {e}")
            try:
                # Get Chrome version
                import subprocess
                import re
                import platform
                
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
                
                chrome_version = get_chrome_version()
                if chrome_version:
                    major_version = int(chrome_version.split('.')[0])
                    print(f"   🔍 Detected Chrome version: {chrome_version}, using major version: {major_version}")
                else:
                    major_version = None
                    print("   ⚠️  Could not detect Chrome version, trying with no version specified")
                
                # Create fresh options to avoid reuse issue
                options = create_stealth_chrome_options()
                driver = uc.Chrome(options=options, version_main=major_version)
                test_results['chrome_creation'] = True
                print(f"   ✅ Chrome instance created successfully with detected version {major_version}")
            except Exception as e2:
                print(f"   ❌ Failed to create Chrome instance: {e2}")
                return False
        
        print("\n🕵️  Injecting stealth scripts...")
        test_results['stealth_injection'] = inject_stealth_scripts(driver)
        
        print("\n🤖 Testing webdriver detection...")
        webdriver_result = driver.execute_script("return navigator.webdriver")
        if webdriver_result is None or webdriver_result == False:
            test_results['webdriver_hidden'] = True
            print("   ✅ navigator.webdriver is hidden")
        else:
            print(f"   ❌ navigator.webdriver detected: {webdriver_result}")
        
        print("\n🔍 Testing automation detection...")
        automation_result = driver.execute_script("""
            return window.chrome && window.chrome.runtime;
        """)
        if automation_result:
            test_results['automation_hidden'] = True
            print("   ✅ Chrome runtime properly simulated")
        else:
            print("   ⚠️  Chrome runtime simulation needs improvement")
        
        print("\n🌐 Testing Instagram access...")
        driver.get('https://www.instagram.com/')
        time.sleep(5)
        
        # Re-inject stealth scripts after navigation
        inject_stealth_scripts(driver)
        
        page_title = driver.title
        page_source_snippet = driver.page_source[:500]
        
        if "Instagram" in page_title and "blocked" not in page_title.lower() and "suspended" not in page_source_snippet.lower():
            test_results['instagram_access'] = True
            print("   ✅ Instagram page loaded successfully")
            print(f"   📄 Page title: {page_title}")
        else:
            print("   ⚠️  Instagram page may have detection issues")
            print(f"   📄 Page title: {page_title}")
            if "blocked" in page_source_snippet.lower() or "suspended" in page_source_snippet.lower():
                print("   🚨 DETECTION WARNING: Page contains blocking/suspension indicators")
        
        # Test additional properties
        user_agent = driver.execute_script("return navigator.userAgent")
        plugins_count = driver.execute_script("return navigator.plugins.length")
        languages = driver.execute_script("return navigator.languages")
        
        print(f"\n🔧 Browser fingerprint:")
        print(f"   User Agent: {user_agent[:80]}...")
        print(f"   Plugins: {plugins_count}")
        print(f"   Languages: {languages}")
        
        # Test for common detection methods
        print(f"\n🔍 Detection tests:")
        
        # Test for webdriver property
        webdriver_test = driver.execute_script("return navigator.webdriver")
        print(f"   navigator.webdriver: {webdriver_test}")
        
        # Test for automation flags
        automation_test = driver.execute_script("return window.navigator.webdriver")
        print(f"   window.navigator.webdriver: {automation_test}")
        
        # Test for chrome runtime
        chrome_test = driver.execute_script("return !!window.chrome")
        print(f"   window.chrome exists: {chrome_test}")
        
    except Exception as e:
        print(f"   ❌ Error during testing: {e}")
    
    finally:
        if driver:
            driver.quit()
            print("\n🧹 Chrome instance cleaned up")
    
    # Results summary
    print("\n" + "=" * 50)
    print("📊 STEALTH TEST RESULTS")
    print("=" * 50)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall Score: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 EXCELLENT! All stealth measures are working!")
        print("   Your tool should be much harder for Instagram to detect.")
        print("   ✅ Ready for safe Instagram automation!")
    elif passed_tests >= total_tests * 0.8:
        print("\n✅ GOOD! Most stealth measures are working.")
        print("   Your tool has good protection against detection.")
        print("   💡 Consider increasing delays for extra safety.")
    else:
        print("\n⚠️  WARNING! Some stealth measures failed.")
        print("   🔧 Recommendations:")
        print("   - Update Chrome browser to latest version")
        print("   - Update undetected-chromedriver: pip install --upgrade undetected-chromedriver")
        print("   - Use longer delays (60+ seconds)")
        print("   - Test with a small number of messages first")
    
    return passed_tests >= total_tests * 0.8

if __name__ == "__main__":
    print("🚀 Starting Instagram Anti-Detection Test...\n")
    
    success = test_instagram_stealth()
    
    print("\n" + "=" * 50)
    if success:
        print("🎯 READY! Your Instagram DM tool has good stealth protection.")
        print("💡 Tips for maximum safety:")
        print("   - Use delays of 30+ seconds between messages")
        print("   - Limit to 50-100 messages per account per day")
        print("   - Take breaks every 10-20 messages")
        print("   - Use aged, high-quality Instagram accounts")
    else:
        print("🔧 NEEDS IMPROVEMENT! Address the failed tests above.")
        print("⚠️  Use with caution and conservative settings.")
    print("=" * 50) 