import requests 
import sys
import re
import time
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class YoutubeSubtitlesScraper:
    def __init__(self,url):
        self.start_url = url
        
    def __enter__(self):
        self.driver = webdriver.Chrome(executable_path='/Users/edwardcox/chromedriver/chromedriver')
        
        self.wait = WebDriverWait(self.driver, 10)

        self.driver.get(start_url)
        self.display_all_videos()
        
    # enter & exit similar to try, finally
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()

    def display_all_videos(self):
        """Clicks on "Load More" button to display all users videos."""
        while True:
            try:
                element = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "yt-uix-load-more")))
                element.click()
            except TimeoutException:
                break

    def subtitles(self):
        """Visits video's page, enables 'CC' to scrape the subtitles and generates filename, link and the subtitles content."""
        videos = [(video.text, video.get_attribute("href"))
                  for video in self.driver.find_elements_by_class_name("yt-uix-tile-link")]

        for filename, link in videos:
            self.driver.get(link)
            self.enable_subtitles()

            link = self.get_subtitles_link()
            if link!="":
                matchObj = re.match( r'(.*)expire=(.*)key(.*)', link)
                link = matchObj.group(1) + "key" + matchObj.group(3) #excludes expiry data
            #empty strings are falsy
            yield filename, link, self.scrape_subtitles(link) if link else "No Closed Caption"

    def enable_subtitles(self):
        """Clicks on CC(Closed Caption) button in YouTube video."""
        show_subtitles_button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ytp-subtitles-button")))
        show_subtitles_button.click()

    def get_subtitles_link(self):
        #cool how doe this work? checks different stages of browser loading, returns all entries, then finds 'srv3' valufe? 
        """Finds string in performance timings that contains the substring 'srv3' which is the subtitles link."""
        time.sleep(1)
        timings = self.driver.execute_script("return window.performance.getEntries();")

        for timing in timings:
            for value in timing.values():
                if "srv3" in str(value):
                    return value
        return ""

    def scrape_subtitles(self, subtitle_link):
        """HTML parses subtitles."""
        response = urllib.request.urlopen(subtitle_link)
        soup = BeautifulSoup(response, "lxml")
        return soup.get_text(strip=True)

def create_file(filename, link, subtitles):
    """Creates file for the subtitle."""
    title = "".join([c for c in filename if c.isalpha() or c.isdigit() or c == ' ']).rstrip()

    with open(title + '.txt', 'w') as subtitles_file:
        subtitles_file.write('LINK: ' + link + '\n')
        subtitles_file.write(subtitles)


if __name__ == "__main__":
    start_url = "https://www.youtube.com/watch?v=uUWaIDEE3gM"

    with YoutubeSubtitlesScraper(start_url) as scraper:
        for filename, link, content in scraper.subtitles():
            try:
                create_file(filename, link, content)
            except:
                print("Can't create file for: " + filename + " : " + link)
