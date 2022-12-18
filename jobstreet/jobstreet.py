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

def scrape(pathdriver = "./chromedriver.exe",job = '', location = '', t_wait = 5, period = 'anytime',n_pages = 2, csv_file = 'results.csv'):
    """
    collect data from jobstreet job list and save it in csv format.

    Parameters
    ----------
    pathdriver : str, default './chromedriver.exe'
        Driver location.
    job : str, default ''
        Job to search.
    location : str, default ''
        job location.
    t_wait : int, default 5
        Time limit to find element.
    period : {'anytime', '1d', '3d', '7d', '14d', '30d'}, default 'anytime'
        The number of pages in job list that you want to collect from jobstreet.
    csv_file : str, default 'results.csv'
        Name of your csv.
    """
    # Driver path
    path = pathdriver
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.switch_to.window(driver.current_window_handle)
    driver.implicitly_wait(t_wait)
    driver.get('https://www.jobstreet.co.id/');
    time.sleep(2)

    # Search Job
    driver.find_element(By.XPATH, '//input[@type="search"]').send_keys(job)
    driver.find_element(By.XPATH, '//input[@id="locationAutoSuggest"]').send_keys(location)
    time.sleep(1)

    # Search button
    driver.find_element(By.XPATH, '//button[@data-automation = "searchSubmitButton"]').click()

    # Created Date
    n_days = 1 if period == 'anytime' else 2 if period == '1d' else 3 if period == '3d' else 4 if period == '7d' else 5 if period == '14d' else 6
    driver.find_element(By.XPATH, '//button[@data-automation = "createdAtFilterButton"]').click()
    time.sleep(1)
    driver.find_element(By.XPATH, f'//div[@data-automation = "filterDropdown-CREATED_AT"]//div[@class = "sx2jih0 zcydq872"][{n_days}]').click()
    time.sleep(1)
    driver.find_element(By.XPATH, '//button[@data-automation = "refinementFormApplyButton"]').click()

    # Get all links for these offers
    links = []
    print('Links are being collected now.')
    for page in range(1,n_pages+1):
        print(f'Collecting the links in the page: {page}')
        time.sleep(2)
        jobs_block = driver.find_element(By.XPATH, '//div[@data-automation = "jobListing"]')
        jobs_list= jobs_block.find_elements(By.XPATH, '//h1[@class = "sx2jih0 zcydq84u es8sxo0 es8sxo3 es8sxo21 es8sxoi"]')
        for job in jobs_list:
            all_links = job.find_elements(By.XPATH,'//a[contains(@href, "/job/")]')
            num = 1
            for a in all_links:
                if a.get_attribute('href') not in links: 
                    links.append(a.get_attribute('href'))
                    print(f"{num} links collected in page {page}")
                    num += 1
                else:
                    pass
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # go to next page:
        driver.find_element(By.XPATH, f'//div[@data-automation = "pagination"]/a[contains(@href, "/{page + 1}")]').click()
            
    print('Found ' + str(len(links)) + ' links for job offers')

    # Create empty lists to store information
    job_titles = []
    company_names = []
    details = []
    job_desc = []
    info = []

    i = 0
    j = 0
    # Visit each link one by one to scrape the information
    print('Visiting the links and collecting information just started.')
    n_pages = 2 if n_pages < 2 else n_pages
    for i in range(len(links)):
        j += 1
        print(f'Scraping the Job Offer {j}')
        try:
            driver.get(links[i])
            i=i+1
            time.sleep(2)
            card = driver.find_element(By.XPATH, '//div[@class = "sx2jih0 zcydq8r zcydq8p _16wtmva0 _16wtmva4"]')
            driver.execute_script("arguments[0].scrollIntoView();", card)
            job_titles.append(card.find_element(By.XPATH, '//h1[contains(@class, "sx2jih0 zcydq84u es8sxo0 es8sxol _1d0g9qk4 es8sxos es8sxo21")]').text)
            company_names.append(card.find_element(By.XPATH, '//span[contains(@class, "sx2jih0 zcydq84u es8sxo0 es8sxo2 es8sxo21 _1d0g9qk4 es8sxoa")]').text)
            card_details = card.find_element(By.XPATH, '//div[@class = "sx2jih0 zcydq84u zcydq87i zcydq87r zcydq89m zcydq8p"]').text
            details.append(card_details)
        except:
            pass
        try:
            description = driver.find_element(By.XPATH, "//div[@class = 'sx2jih0 zcydq86q zcydq86v zcydq86w']")
            driver.execute_script("arguments[0].scrollIntoView();", description)
        except:
            pass
        time.sleep(2)
        try:
            job_text = driver.find_element(By.XPATH, '//div[@data-automation="jobDescription"]').text
            job_desc.append(job_text)
        except:
            job_desc.append("")
        try:
            info_block = driver.find_element(By.XPATH, '//div[@class = "sx2jih0 _17fduda0 _17fduda7 _17fdudah"]/div[@class = "sx2jih0 zcydq86q zcydq86v zcydq86w"][2]')
            driver.execute_script("arguments[0].scrollIntoView();", info_block)
            info.append(info_block.text)
        except:
            pass

    # Creating the dataframe 
    df = pd.DataFrame(list(zip(job_titles,company_names,
                        details,job_desc, info)),
                        columns =['Job Title', 'Company Name',
                            'Details', 'Job Description', 'Additional Information'])

    # Storing the data to csv file
    df.to_csv(csv_file, index=False)