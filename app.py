
from dotenv import load_dotenv
import os
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
import re

load_dotenv()

LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")


def create_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")  # Uncomment to run headless
    driver = webdriver.Chrome(options=options)
    return driver

def scrape_emails_from_profile(driver, profile_url):
    driver.get(profile_url)
    time.sleep(5)
    
    try:
        contact_button = driver.find_element(By.ID, "top-card-text-details-contact-info")
        contact_button.click()
        time.sleep(3)
    except NoSuchElementException:
        return "Contact info button not found."
    
    try:
        popup = driver.find_element(By.CSS_SELECTOR, "section.pv-contact-info, div[role='dialog'], div.artdeco-modal__content")
        popup_text = popup.text
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        emails = re.findall(email_pattern, popup_text)
        if emails:
            return list(set(emails))
        else:
            return "No emails found."
    except NoSuchElementException:
        return "Contact info popup not found."

def main():
    st.title("LinkedIn Email Scraper with Selenium")
    st.write("Enter one or more LinkedIn profile URLs (one per line):")
    
    urls_input = st.text_area("Profile URLs")
    start_button = st.button("Start Scraping")
    
    if start_button and urls_input.strip():
        urls = [url.strip() for url in urls_input.split("\n") if url.strip()]
        st.info(f"Logging into LinkedIn as {LINKEDIN_USERNAME} ...")
        
        driver = create_driver()
        try:
            # Login
            driver.get("https://www.linkedin.com/login")
            time.sleep(2)
            driver.find_element(By.ID, "username").send_keys(LINKEDIN_USERNAME)
            driver.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD)
            driver.find_element(By.XPATH, '//button[@type="submit"]').click()
            time.sleep(5)
            
            results = []
            for url in urls:
                st.info(f"Scraping {url}")
                result = scrape_emails_from_profile(driver, url)
                results.append((url, result))
            
            st.success("Scraping complete!")
            for url, emails in results:
                st.write(f"**{url}**")
                if isinstance(emails, list):
                    st.write("Emails found:")
                    for e in emails:
                        st.write(f"- {e}")
                else:
                    st.write(emails)
                    
        except Exception as e:
            st.error(f"Error during scraping: {e}")
        finally:
            driver.quit()

if __name__ == "__main__":
    main()
