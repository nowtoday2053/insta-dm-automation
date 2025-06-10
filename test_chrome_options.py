#!/usr/bin/env python3
"""
Test script to verify ChromeOptions reuse issue is fixed
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_fresh_chrome_options
import undetected_chromedriver as uc
import time

def test_chrome_options_reuse():
    """Test that we can create multiple Chrome instances without reuse issues."""
    print("🧪 Testing Chrome Options Reuse Fix")
    print("=" * 50)
    
    drivers = []
    success_count = 0
    
    try:
        # Test creating multiple Chrome instances
        for i in range(3):
            print(f"\n🔍 Creating Chrome instance {i + 1}...")
            
            try:
                # Create fresh options for each instance
                options = create_fresh_chrome_options()
                options.add_argument('--headless')  # Run headless for testing
                
                # Add a small delay between instances
                time.sleep(2)
                
                # Try to create driver
                driver = uc.Chrome(options=options, version_main=None)
                drivers.append(driver)
                
                print(f"   ✅ Successfully created Chrome instance {i + 1}")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ Failed to create Chrome instance {i + 1}: {e}")
                
                # Try with specific version as fallback
                try:
                    options = create_fresh_chrome_options()
                    options.add_argument('--headless')
                    driver = uc.Chrome(options=options, version_main=136)
                    drivers.append(driver)
                    print(f"   ✅ Successfully created Chrome instance {i + 1} with version 136")
                    success_count += 1
                except Exception as e2:
                    print(f"   ❌ Failed with version 136 too: {e2}")
    
    finally:
        # Clean up all drivers
        print(f"\n🧹 Cleaning up {len(drivers)} Chrome instances...")
        for i, driver in enumerate(drivers):
            try:
                driver.quit()
                print(f"   ✅ Cleaned up Chrome instance {i + 1}")
            except Exception as e:
                print(f"   ⚠️  Error cleaning up instance {i + 1}: {e}")
    
    # Results
    print("\n" + "=" * 50)
    if success_count == 3:
        print("🎉 SUCCESS! All Chrome instances created successfully.")
        print("   ChromeOptions reuse issue appears to be fixed!")
        return True
    elif success_count > 0:
        print(f"⚠️  PARTIAL SUCCESS! {success_count}/3 instances created.")
        print("   Some improvement, but may need more work.")
        return False
    else:
        print("❌ FAILED! No Chrome instances could be created.")
        print("   ChromeOptions reuse issue may still exist.")
        return False

if __name__ == "__main__":
    test_chrome_options_reuse() 