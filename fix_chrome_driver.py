#!/usr/bin/env python3
"""
Chrome Driver Fix Script for InstaDM Pro
This script helps resolve Chrome driver version mismatch issues.
"""

import subprocess
import sys
import os
import re
import platform

def run_command(command):
    """Run a command and return the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

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
        success, output, _ = run_command(command)
        if success and output:
            # Extract version number
            version_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', output)
            if version_match:
                return version_match.group(1)
    
    return None

def fix_chrome_driver():
    """Main function to fix Chrome driver issues."""
    print("🔧 InstaDM Pro - Chrome Driver Fix Tool")
    print("=" * 50)
    
    # Step 1: Check Chrome version
    print("1️⃣  Checking Chrome browser version...")
    chrome_version = get_chrome_version()
    
    if chrome_version:
        major_version = chrome_version.split('.')[0]
        print(f"   ✅ Chrome version found: {chrome_version} (Major: {major_version})")
    else:
        print("   ❌ Could not detect Chrome version. Please install Google Chrome.")
        return False
    
    # Step 2: Update undetected-chromedriver
    print("\n2️⃣  Updating undetected-chromedriver...")
    success, output, error = run_command(f"{sys.executable} -m pip install --upgrade undetected-chromedriver")
    
    if success:
        print("   ✅ Successfully updated undetected-chromedriver")
    else:
        print(f"   ❌ Failed to update: {error}")
        return False
    
    # Step 3: Clear cache
    print("\n3️⃣  Clearing Chrome driver cache...")
    
    # Common cache locations
    cache_dirs = []
    
    if platform.system() == "Windows":
        cache_dirs = [
            os.path.expanduser("~\\AppData\\Local\\Temp\\undetected_chromedriver"),
            os.path.expanduser("~\\.undetected_chromedriver")
        ]
    else:
        cache_dirs = [
            os.path.expanduser("~/.cache/undetected_chromedriver"),
            os.path.expanduser("~/.undetected_chromedriver"),
            "/tmp/undetected_chromedriver"
        ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                import shutil
                shutil.rmtree(cache_dir)
                print(f"   ✅ Cleared cache: {cache_dir}")
            except Exception as e:
                print(f"   ⚠️  Could not clear {cache_dir}: {e}")
    
    # Step 4: Test the fix
    print("\n4️⃣  Testing Chrome driver initialization...")
    
    try:
        import undetected_chromedriver as uc
        
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Try automatic version detection first
        try:
            driver = uc.Chrome(options=options, version_main=None)
            driver.quit()
            print("   ✅ Chrome driver initialized successfully with auto-detection")
            success = True
        except Exception as e:
            print(f"   ⚠️  Auto-detection failed: {e}")
            # Try with specific version
            try:
                driver = uc.Chrome(options=options, version_main=int(major_version))
                driver.quit()
                print(f"   ✅ Chrome driver initialized successfully with version {major_version}")
                success = True
            except Exception as e2:
                print(f"   ❌ Failed with specific version: {e2}")
                success = False
        
    except ImportError:
        print("   ❌ undetected-chromedriver not found. Please run: pip install undetected-chromedriver")
        success = False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        success = False
    
    # Summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS! Chrome driver is now working correctly.")
        print("   You can now run your InstaDM Pro campaign!")
    else:
        print("❌ FAILED! There are still issues with the Chrome driver.")
        print("\n💡 TROUBLESHOOTING TIPS:")
        print("   1. Update Google Chrome to the latest version")
        print("   2. Restart your computer")
        print("   3. Run: pip install --force-reinstall undetected-chromedriver")
        print("   4. Check if you have multiple Chrome installations")
        print("   5. Try running as administrator/sudo")
    
    return success

if __name__ == "__main__":
    fix_chrome_driver() 