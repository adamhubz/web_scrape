# Libraries
import time
import pandas as pd    
# ------------- # 
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def scrape(pathdriver = "./chromedriver.exe", link = 'https://www.linkedin.com/jobs/search/', n_scrolls = 2, csv_file = 'results.csv'):
    """
    collect data from linkedin job list and save it in csv format.

    Parameters
    ----------
    pathdriver : str
        Driver location.
    link : str
        Link of linkedin job list that you want to search.
    n_scrolls : int
        The number of scroll that you want to collect from linkedin.
    csv_file : str
        Name of your csv.
    """
    # Driver settings
    path = pathdriver
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    # Maximize Window
    driver.maximize_window() 
    driver.switch_to.window(driver.current_window_handle)

    # Enter to the site
    driver.get(link);

    # Get all links for these offers
    links = []

    print('Links are being collected now.')
    for scroll in range(n_scrolls+1):
        try:
            driver.find_element(By.XPATH, '//button[@data-tracking-control-name = "infinite-scroller_show-more"]').click()
        except:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print(f'Scroll - {scroll}')
            
    time.sleep(3)
    jobs_block = driver.find_element(By.CLASS_NAME, 'jobs-search__results-list')
    jobs_list= jobs_block.find_elements(By.CSS_SELECTOR, '.jobs-search__results-list li')
    for job in jobs_list:
        all_links = job.find_elements(By.TAG_NAME,'a')
        for a in all_links:
            if a.get_attribute('href') not in links: 
                links.append(a.get_attribute('href'))
            else:
                pass
        # scroll down for each job element
        driver.execute_script("arguments[0].scrollIntoView();", job)

    print('Found ' + str(len(links)) + ' links for job offers')

    # Create empty lists to store information
    job_titles = []
    company_names = []
    company_locations = []
    post_dates = []
    job_desc = []

    j = 0
    # Visit each link one by one to scrape the information
    print('Visiting the links and collecting information just started.')
    for link in links:
        j += 1
        try:
            driver.get(link)
            i=i+1
            time.sleep(2)
            article = driver.find_element(By.XPATH, '//div[contains(@class, "description__text")]')
            driver.execute_script("arguments[0].scrollIntoView();", article)
            driver.find_element(By.XPATH, '//button[contains(@class, "show-more-less-html__button")]').click()
            time.sleep(2)
            print(f'Scraping the Job Offer {j}')
            try:
                job_titles.append(driver.find_element(By.XPATH, '//h1[contains(@class, "topcard__title")]').text)
            except:
                job_titles.append(" ")
            try:
                company_names.append(driver.find_element(By.XPATH, '//a[contains(@class, "topcard__org-name")]').text)
            except:
                company_names.append(" ")
            try:
                company_locations.append(driver.find_element(By.XPATH, '//span[contains(@class, "topcard__flavor--bullet")]').text)
            except:
                company_locations.append(" ")
            try:  
                post_dates.append(driver.find_element(By.XPATH, '//span[contains(@class, "posted-time")]').text)
            except:
                post_dates.append(" ")
            try:
                job_text = driver.find_element(By.XPATH, '//div[contains(@class, "show-more-less-html__markup")]').text
                job_desc.append(job_text)
            except:
                job_desc.append(" ") 
        except:
            print('Link need login')   
                
    # Creating the dataframe 
    df = pd.DataFrame(list(zip(job_titles,company_names,
                        company_locations,post_dates,job_desc)),
                        columns =['Job Title', 'Company Name',
                            'Company Location','Post Date','Job Description'])

    # Storing the data to csv file
    df.to_csv(csv_file, index=False)