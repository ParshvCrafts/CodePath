"""
Screenshot script for PawPal+ Streamlit app
"""

import subprocess
import time
import os
import sys
from pathlib import Path

# Ensure we're in the right directory
os.chdir(Path(__file__).parent)

# Start Streamlit app in background
print("Starting Streamlit app...")
proc = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", "app.py", "--logger.level=error"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for app to start
time.sleep(5)

try:
    # Try using Playwright to take screenshot
    from playwright.sync_api import sync_playwright

    print("Taking screenshot with Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        try:
            page.goto("http://localhost:8501", timeout=10000)
            time.sleep(3)  # Wait for app to fully load

            # Take screenshot
            screenshot_path = Path(__file__).parent / "pawpal_demo.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"✅ Screenshot saved to {screenshot_path}")

        finally:
            browser.close()

except Exception as e:
    print(f"Playwright method failed: {e}")
    print("Trying alternative screenshot method...")

    # Fallback: Try PIL/Pillow if available
    try:
        from PIL import ImageGrab
        screenshot_path = Path(__file__).parent / "pawpal_demo.png"
        img = ImageGrab.grab()
        img.save(str(screenshot_path))
        print(f"✅ Screenshot saved to {screenshot_path} using PIL")
    except Exception as e2:
        print(f"PIL method also failed: {e2}")
        print("Note: Manual screenshot required. Take a screenshot of http://localhost:8501")

finally:
    # Stop Streamlit
    proc.terminate()
    proc.wait(timeout=5)
    print("Streamlit app stopped")
