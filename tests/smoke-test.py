#!/usr/bin/env python3
"""
Comprehensive smoke tests for Selenium standalone-chromium container.
Tests Chromium/ChromeDriver functionality through real browser interactions.
Supports multi-architecture: AMD64 and ARM64.
"""
import sys
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException


def test_container_health(selenium_url):
    """Test 1: Verify Selenium Grid is ready and healthy."""
    print("Test 1: Checking container health...")

    max_retries = 60
    for i in range(max_retries):
        try:
            response = requests.get(f"{selenium_url}/wd/hub/status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                if status.get("value", {}).get("ready"):
                    print(f"  ✓ Selenium Grid ready after {i+1} attempts")
                    return True
        except requests.exceptions.RequestException:
            pass

        if i < max_retries - 1:
            time.sleep(1)

    print("  ✗ Selenium Grid did not become ready within 60 seconds")
    return False


def test_webdriver_connection(selenium_url):
    """Test 2: Verify WebDriver can create a session with Chromium."""
    print("Test 2: Testing WebDriver connection...")

    try:
        options = webdriver.ChromeOptions()
        driver = webdriver.Remote(
            command_executor=selenium_url,
            options=options
        )

        session_id = driver.session_id
        if session_id:
            print(f"  ✓ WebDriver session created: {session_id}")
            driver.quit()
            return True
        else:
            print("  ✗ No session ID returned")
            return False

    except WebDriverException as e:
        print(f"  ✗ WebDriver connection failed: {e}")
        return False


def test_browser_interaction(selenium_url):
    """Test 3: Verify real browser interaction with a test website."""
    print("Test 3: Testing browser interaction...")

    driver = None
    try:
        options = webdriver.ChromeOptions()
        driver = webdriver.Remote(
            command_executor=selenium_url,
            options=options
        )

        wait = WebDriverWait(driver, 10)

        # Navigate to test site
        print("  - Navigating to test site...")
        driver.get("https://the-internet.herokuapp.com/login")

        # Find and fill username
        print("  - Finding and filling username field...")
        username_field = wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_field.send_keys("tomsmith")

        # Find and fill password
        print("  - Finding and filling password field...")
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys("SuperSecretPassword!")

        # Click login button
        print("  - Clicking login button...")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()

        # Verify success message
        print("  - Verifying login success...")
        success_message = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".flash.success"))
        )

        if "You logged into a secure area!" in success_message.text:
            print("  ✓ Login successful, message verified")
        else:
            print(f"  ✗ Unexpected message: {success_message.text}")
            return False

        # Click logout
        print("  - Clicking logout button...")
        logout_button = driver.find_element(By.CSS_SELECTOR, "a[href='/logout']")
        logout_button.click()

        # Verify logout message
        print("  - Verifying logout success...")
        logout_message = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".flash.success"))
        )

        if "You logged out of the secure area!" in logout_message.text:
            print("  ✓ Logout successful, message verified")
        else:
            print(f"  ✗ Unexpected logout message: {logout_message.text}")
            return False

        # Take screenshot for verification
        print("  - Taking screenshot...")
        screenshot_path = "/tmp/selenium-test-screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"  ✓ Screenshot saved to {screenshot_path}")

        print("  ✓ All browser interactions successful")
        return True

    except TimeoutException as e:
        print(f"  ✗ Timeout waiting for element: {e}")
        return False
    except WebDriverException as e:
        print(f"  ✗ Browser interaction failed: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
        return False
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


def main():
    """Run all smoke tests."""
    selenium_url = "http://localhost:4444"

    print("=" * 60)
    print("Selenium Standalone Chromium - Smoke Tests")
    print("=" * 60)
    print()

    # Run all tests
    results = []
    results.append(("Container Health", test_container_health(selenium_url)))
    results.append(("WebDriver Connection", test_webdriver_connection(selenium_url)))
    results.append(("Browser Interaction", test_browser_interaction(selenium_url)))

    # Print summary
    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {test_name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
