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
from selenium.webdriver.chrome.options import Options
options = Options()
options.add_extension('/Users/edwardcox/chrome_extension/extension_1_5_21_0.crx')

#chrome_options.add_extension('/Users/edwardcox/Desktop/extension_1_5_21_0.crx')

class YoutubeSubtitlesScraper:
    def __init__(self,url):
        self.subtitles_file = open("subtitleUrl.txt",'w')
        self.start_url = url
        
    def __enter__(self):
        self.driver = webdriver.Chrome(executable_path='/Users/edwardcox/chromedriver/chromedriver',chrome_options=options)
        self.wait = WebDriverWait(self.driver, 10)
        return self
        
    # enter & exit similar to try, finally
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()

    def playlist_all(self):
        for i in range(1):
            self.driver.get(self.start_url)
            playlist_title_btns = self.wait.until(EC.presence_of_all_elements_located((By.PARTIAL_LINK_TEXT,'VIEW FULL PLAYLIST')))
            playlist_title_btn = playlist_title_btns[i]
            single_playlist_url = playlist_title_btn.get_attribute('href')
            playlist_title_btn.click()
            self.playlist_single(single_playlist_url)
        
    def playlist_single(self,playlist_url):
        playlist_single_btns = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'.yt-simple-endpoint.style-scope.ytd-playlist-video-renderer')))
        len_btns = len(playlist_single_btns)
        for i in range(len_btns): #stale element exception, must reassign reference every time
            playlist_single_btns = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'.yt-simple-endpoint.style-scope.ytd-playlist-video-renderer')))
            url = playlist_single_btns[i].get_attribute('href')
            for title, link, channel in self.subtitles(url):
                try: 
                    self.subtitles_file.write(title + '\t' + link + '\t' + channel + '\n')
                except Exception as e:
                    print(e)
                self.driver.get(playlist_url) #return to the previous page
            
    def subtitles(self,url):
        """Visits video's page, enables 'CC' to scrape the subtitles and generates filename, link and the subtitles content."""
        try:
            self.driver.get(url)
            self.enable_subtitles()            
            link = self.get_subtitles_link()
            print(link)
            self.enable_subtitles()
            video_title = self.driver.find_element_by_xpath('/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[3]/div[1]/div/div[5]/div[2]/ytd-video-primary-info-renderer/div/h1/yt-formatted-string').text
            channel_name = self.driver.find_element_by_xpath('/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[3]/div[1]/div/div[7]/div[3]/ytd-video-secondary-info-renderer/div/div[2]/ytd-video-owner-renderer/div[1]/div/yt-formatted-string/a').text
        except Exception as e:
            link = ""
            video_title = "Missing Video"
            channel_name=""
        yield video_title,link, channel_name if link else "No Closed Caption"

    def enable_subtitles(self):
        """Clicks on CC(Closed Caption) button in YouTube video."""
        try:
            show_subtitles_button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ytp-subtitles-button")))
            show_subtitles_button.click()
        except Exception as e:
            print(e)

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
    playlist_page = "https://www.youtube.com/results?search_query=chemistry&sp=EgIQAw%253D%253D"
    ytScraper = YoutubeSubtitlesScraper(playlist_page)
    with ytScraper as scraper:
        scraper.playlist_all()
        scraper.subtitles_file.close()

