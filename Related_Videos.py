import requests 
import sys
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

        return self
        
    # enter & exit similar to try, finally
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()

    def subtitles(self):
        """Visits video's page, enables 'CC' to scrape the subtitles and generates filename, link and the subtitles content."""
        for x in range(100):
            try:                
                self.driver.get(self.start_url)
                WebDriverWait(self.driver,3).until(EC.presence_of_element_located((By.XPATH,"/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[3]/div[2]/div/div[2]/ytd-watch-next-secondary-results-renderer/div[2]/ytd-compact-autoplay-renderer/div[2]/ytd-compact-video-renderer/div[1]/a")))
                next_video = self.driver.find_element_by_xpath("/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[3]/div[2]/div/div[2]/ytd-watch-next-secondary-results-renderer/div[2]/ytd-compact-autoplay-renderer/div[2]/ytd-compact-video-renderer/div[1]/a")
                self.enable_subtitles()            
                link = self.get_subtitles_link()
                video_title = self.driver.find_element_by_xpath('//*[@id="video-title"]').text
                channel_name = self.driver.find_element_by_xpath('/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[3]/div[1]/div/div[7]/div[3]/ytd-video-secondary-info-renderer/div/div[2]/ytd-video-owner-renderer/div[1]/div/yt-formatted-string/a').text
            except:
                print("video incompatible ")
                link = ""
                video_title = "Missing Video"
                channel_name=""
            print(self.start_url)
            next_url = next_video.get_attribute("href")
            self.start_url = next_url #go to next video in Up Next
            yield video_title,link, channel_name if link else "No Closed Caption"

    def enable_subtitles(self):
        """Clicks on CC(Closed Caption) button in YouTube video."""
        show_subtitles_button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ytp-subtitles-button")))
        show_subtitles_button.click()

    #PROBLEM HERE
    def get_subtitles_link(self):
        #cool how doe this work? checks different stages of browser loading, returns all entries, then finds 'srv3' value? 
        """Finds string in performance timings that contains the substring 'srv3' which is the subtitles link."""
        time.sleep(1)
        timings = self.driver.execute_script("return window.performance.getEntries();")
        for timing in timings:
            for value in timing.values():
                if "srv3" in str(value):
                    return value
        return ""

if __name__ == "__main__":
    start_url = "https://www.youtube.com/watch?v=LsqKL3pBVMA"
    ytScraper = YoutubeSubtitlesScraper(start_url)
    subtitles_file = open("subtitleUrl.txt",'w')
    with ytScraper as scraper:
        for title, link, channel in scraper.subtitles():
            try:
                if link != '':
                    subtitles_file.write(title + '\t' + link + '\t' + channel + '\n')
            except:
                print("can't create file for: " + title + " : " + link + " : " + channel)
    subtitles_file.close()

