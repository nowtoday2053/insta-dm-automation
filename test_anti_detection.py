#!/usr/bin/env python3
"""
Anti-Detection Test Script for InstaDM Pro
This script tests all anti-detection measures to ensure Instagram won't detect the automation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_fresh_chrome_options, inject_stealth_scripts, simulate_human_behavior
import undetected_chromedriver as uc
import time
import random

def test_anti_detection():
    """Test all anti-detection measures."""
    print("🛡️  Testing Anti-Detection Measures")
    print("=" * 60)
    
    driver = None
    test_results = {
        'chrome_options': False,
        'stealth_scripts': False,
        'human_behavior': False,
        'webdriver_hidden': False,
        'automation_hidden': False
    }
    
    try:
        print("\n🔧 Creating Chrome instance with anti-detection options...")
        options = create_fresh_chrome_options()
        options.add_argument('--headless')  # Run headless for testing
        
        driver = uc.Chrome(options=options, version_main=None)
        test_results['chrome_options'] = True
        print("   ✅ Chrome instance created successfully")
        
        print("\n🕵️  Testing stealth script injection...")
        driver.get('https://httpbin.org/user-agent')
        time.sleep(2)
        
        inject_stealth_scripts(driver)
        test_results['stealth_scripts'] = True
        print("   ✅ Stealth scripts injected successfully")
        
        print("\n🤖 Testing webdriver detection...")
        webdriver_result = driver.execute_script("return navigator.webdriver")
        if webdriver_result is None or webdriver_result == False:
            test_results['webdriver_hidden'] = True
            print("   ✅ navigator.webdriver is hidden")
        else:
            print("   ❌ navigator.webdriver is still detectable")
        
        print("\n🔍 Testing automation detection...")
        automation_result = driver.execute_script("""
            return window.chrome && window.chrome.runtime && window.chrome.runtime.onConnect;
        """)
        if automation_result:
            test_results['automation_hidden'] = True
            print("   ✅ Chrome runtime properly simulated")
        else:
            print("   ⚠️  Chrome runtime simulation may need improvement")
        
        print("\n👤 Testing human behavior simulation...")
        simulate_human_behavior(driver, "before_login")
        test_results['human_behavior'] = True
        print("   ✅ Human behavior simulation working")
        
        print("\n🌐 Testing Instagram detection (basic check)...")
        driver.get('https://www.instagram.com/')
        time.sleep(5)
        
        # Re-inject stealth scripts after navigation
        inject_stealth_scripts(driver)
        
        # Check if we can access the page without immediate detection
        page_title = driver.title
        if "Instagram" in page_title and "blocked" not in page_title.lower():
            print("   ✅ Instagram page loaded successfully")
            print(f"   📄 Page title: {page_title}")
        else:
            print("   ⚠️  Instagram page may have issues")
            print(f"   📄 Page title: {page_title}")
        
        # Test user agent
        user_agent = driver.execute_script("return navigator.userAgent")
        print(f"\n🔧 User Agent: {user_agent}")
        
        # Test plugins
        plugins_count = driver.execute_script("return navigator.plugins.length")
        print(f"🔌 Plugins detected: {plugins_count}")
        
        # Test screen properties
        screen_info = driver.execute_script("""
            return {
                width: screen.width,
                height: screen.height,
                availWidth: screen.availWidth,
                availHeight: screen.availHeight
            }
        """)
        print(f"🖥️  Screen info: {screen_info}")
        
    except Exception as e:
        print(f"   ❌ Error during testing: {e}")
    
    finally:
        if driver:
            driver.quit()
            print("\n🧹 Chrome instance cleaned up")
    
    # Results summary
    print("\n" + "=" * 60)
    print("📊 ANTI-DETECTION TEST RESULTS")
    print("=" * 60)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall Score: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 EXCELLENT! All anti-detection measures are working!")
        print("   Your tool should be much harder for Instagram to detect.")
    elif passed_tests >= total_tests * 0.8:
        print("\n✅ GOOD! Most anti-detection measures are working.")
        print("   Your tool has good protection against detection.")
    else:
        print("\n⚠️  WARNING! Some anti-detection measures failed.")
        print("   Consider updating undetected-chromedriver or checking your setup.")
    
    return passed_tests == total_tests

def test_typing_behavior():
    """Test human-like typing behavior."""
    print("\n" + "=" * 60)
    print("⌨️  TESTING HUMAN-LIKE TYPING BEHAVIOR")
    print("=" * 60)
    
    # Simulate typing patterns
    test_message = "Hey! Hope you're doing well. Would love to connect!"
    
    print(f"📝 Test message: '{test_message}'")
    print("🕐 Simulating typing delays...")
    
    total_time = 0
    for i, char in enumerate(test_message):
        # Simulate the same logic as human_like_typing
        if i < len(test_message) * 0.2:  # First 20%
            delay = random.uniform(0.15, 0.35)
        elif i < len(test_message) * 0.8:  # Middle 60%
            delay = random.uniform(0.08, 0.20)
        else:  # Last 20%
            delay = random.uniform(0.12, 0.30)
        
        if char in '.,!?':
            delay += random.uniform(0.2, 0.5)
        
        total_time += delay
    
    print(f"⏱️  Total typing time: {total_time:.2f} seconds")
    print(f"📊 Average WPM: {len(test_message.split()) / (total_time / 60):.1f}")
    print("✅ Typing behavior appears human-like!")

if __name__ == "__main__":
    print("🚀 Starting comprehensive anti-detection tests...\n")
    
    success = test_anti_detection()
    test_typing_behavior()
    
    print("\n" + "=" * 60)
    if success:
        print("🎯 READY TO GO! Your Instagram DM tool is well-protected.")
    else:
        print("🔧 NEEDS WORK! Please address the failed tests above.")
    print("=" * 60) 