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

def scrape(pathdriver = "./chromedriver.exe", email = 'youremail@example.com', password = 'yourpassword', link = 'https://www.linkedin.com/jobs/search/', n_pages = 2, csv_file = 'results.csv'):
    """
    collect data from linkedin job list and save it in csv format.

    Parameters
    ----------
    pathdriver : str
        Driver location.
    email : str
        Linkedin email.
    password : str
        Linkedin password.
    link : str
        Link of linkedin job list that you want to search.
    n_pages : int
        The number of pages in job list that you want to collect from linkedin.
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
    driver.implicitly_wait(10)

    # Login to Linkedin
    driver.get('https://www.linkedin.com/login');
    time.sleep(2)

    # User login
    driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(email)
    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(password)
    time.sleep(1)

    # Login button
    driver.find_element(By.XPATH, '//button[@data-litms-control-urn = "login-submit"]').click()

    # Jobs page
    driver.find_element(By.XPATH, '//span[@title = "Jobs"]').click()

    # Enter to the site
    driver.get(link);

    # Get all links for these job
    links = []
    # Navigate the pages
    print('Links are being collected now.')
    n_pages = 2 if n_pages < 2 else n_pages
    for page in range(2,n_pages+1):
        time.sleep(2)
        jobs_block = driver.find_element(By.XPATH, '//ul[@class = "scaffold-layout__list-container"]')
        jobs_list= jobs_block.find_elements(By.CSS_SELECTOR, 'li')
        for job in jobs_list:
            all_links = job.find_elements(By.XPATH,'//a[@class = "disabled ember-view job-card-container__link job-card-list__title"]')
            for a in all_links:
                if a.get_attribute('href') not in links: 
                    links.append(a.get_attribute('href'))
                else:
                    pass
            # scroll down for each job element
            driver.execute_script("arguments[0].scrollIntoView();", job)
        
        print(f'Collecting the links in the page: {page-1}')
        # go to next page:
        driver.find_element(By.XPATH, f"//button[@aria-label='Page {page}']").click()

    print('Found ' + str(len(links)) + ' links for job offers')

    # Create empty lists to store information
    job_titles = []
    company_names = []
    company_locations = []
    post_dates = []
    job_desc = []

    i = 0
    j = 0
    # Visit each link one by one to scrape the information
    print('Visiting the links and collecting information just started.')
    for i in range(len(links)):
        j += 1
        print(f'Scraping the Job Offer - {j}')
        try:
            driver.get(links[i])
            i=i+1
            time.sleep(2)
            article = driver.find_element(By.XPATH, "//article")
            driver.execute_script("arguments[0].scrollIntoView();", article)
            driver.find_element(By.XPATH, '//button[contains(@class, "artdeco-card__action artdeco-button")]').click()
        except:
            pass
        time.sleep(2)
        try:
            job_titles.append(driver.find_element(By.XPATH, '//h1[contains(@class, "jobs-unified-top-card__job-title")]').text)
        except:
            job_titles.append("")
        try:
            company_names.append(driver.find_element(By.XPATH, '//span[contains(@class, "card__company-name")]').text)
        except:
            company_names.append("")
        try:
            company_locations.append(driver.find_element(By.XPATH, '//span[contains(@class, "jobs-unified-top-card__bullet")]').text)
        except:
            company_locations.append("")
        try:
            post_dates.append(driver.find_element(By.XPATH, '//span[contains(@class, "card__posted-date")]').text)
        except:
            post_dates.append("")
        try:
            time.sleep(2)
            job_text = driver.find_element(By.XPATH, '//article').text
            job_desc.append(job_text)
        except:
            job_desc.append("")
                
    # Creating the dataframe 
    df = pd.DataFrame(list(zip(job_titles,company_names,
                        company_locations,post_dates,job_desc)),
                        columns =['Job Title', 'Company Name',
                            'Company Date','Post Date','Job Description'])

    # Saving the data to csv file
    df.to_csv(csv_file, index=False)