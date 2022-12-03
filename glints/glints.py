# Libraries
import time
import pandas as pd
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def scrape(pathdriver = "./chromedriver.exe",job = '', location = '', t_wait = 5, n_pages = 2, csv_file = 'results.csv'):
    """
    collect data from glints job list and save it in csv format.

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
    driver.get('https://glints.com/');
    time.sleep(2)

    # Search Job
    driver.find_element(By.XPATH, '//div[@class = "SearchContainersc__FieldWrapper-sc-1pfj0s7-1 gyztjg"][1]//input').send_keys(job)
    driver.find_element(By.XPATH, '//div[@class = "SearchContainersc__FieldWrapper-sc-1pfj0s7-1 gyztjg"][2]//input').send_keys(location)
    time.sleep(1)

    # Search button
    driver.find_element(By.XPATH, '//button[@aria-label = "Search button"]').click()

    # Close Banner
    time.sleep(5)
    try:
        driver.find_element(By.XPATH, '//div[@class = "ub-emb-iframe-wrapper ub-emb-visible"]/button').click()
    except:
        pass
    ## Triggering mail subscription banner 
    jobs_block = driver.find_element(By.XPATH, '//div[@class = "Box__StyledBox-sc-pr7b7l-0 eKoPLS Flex__StyledFlex-sc-11ryoct-0 lfUEDh ExploreTabsc__Flex-sc-gs9c0s-7 ercRa-D"]')
    driver.execute_script("arguments[0].scrollIntoView();", jobs_block)
    try:
        driver.find_element(By.XPATH, '//div[@class = "ModalStyle__ModalContentArea-sc-bg1vyz-5 iRgfrD modal-content"]/header/button').click()
    except:
        pass

    # Scrolling the page
    for page in range(1,n_pages+1):
        print(f'Scrolling on page: {page}')
        time.sleep(2)
        scroll = driver.find_element(By.XPATH, '//div[@class = "InfiniteScrollsc__InfiniteScrollContainer-sc-1nmx8l5-0 ineNGa"]')
        driver.execute_script("arguments[0].scrollIntoView();", scroll)
    
    # Scroll to top page
    top_page = driver.find_element(By.XPATH, '//div[@class = "Box__StyledBox-sc-pr7b7l-0 fVZtqT"]')
    driver.execute_script("arguments[0].scrollIntoView();", top_page)

    # Get all links for these offers
    links = []
    print('Links are being collected now.')
    jobs_list= jobs_block.find_elements(By.XPATH, '//div[@class = "JobCardsc__JobcardContainer-sc-1f9hdu8-0 hvpJwO CompactOpportunityCardsc__CompactJobCardWrapper-sc-1y4v110-0 dLzoMG compact_job_card"]')
    for job in jobs_list:
        all_links = job.find_elements(By.XPATH,'//a[@class = "CompactOpportunityCardsc__CardAnchorWrapper-sc-1y4v110-18 iOjUdU job-search-results_job-card_link"]')
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
    salary = []
    category = []
    type_job = []
    experience = []
    post_dates = []
    job_desc = []

    i = 0
    j = 0
    # Visit each link one by one to scrape the information
    print('Visiting the links and collecting information just started.')
    for i in range(len(links)):
        j += 1
        print(f'Scraping the Job Offer {j}')
        try:
            driver.get(links[i])
            i=i+1
            time.sleep(2)
            # Close Banner
            try:
                driver.find_element(By.XPATH, '//div[@class = "ub-emb-iframe-wrapper ub-emb-visible"]/button').click()
            except:
                pass

            # Scraping the data
            card = driver.find_element(By.XPATH, '//main[@class = "Opportunitysc__Main-sc-1gsvee3-3 Cglas"]')
            driver.execute_script("arguments[0].scrollIntoView();", card)
            job_titles.append(card.find_element(By.XPATH, '//h1[@class = "TopFoldsc__JobOverViewTitle-sc-kklg8i-3 fFAcsE"]').text)
            company_names.append(card.find_element(By.XPATH, '//div[@class = "TopFoldsc__JobOverViewCompanyName-sc-kklg8i-5 eLQvRY"]').text)
            card_details = card.find_element(By.XPATH, '//div[@class = "TopFoldsc__JobOverViewInfoContainer-sc-kklg8i-8 fgSCsF"]')
            try:
                salary.append(card_details.find_element(By.XPATH, '//div[@class = "TopFoldsc__JobOverViewInfo-sc-kklg8i-9 TopFoldsc__SalaryJobOverview-sc-kklg8i-29 EWOdY daspSa"]').text)
            except:
                salary.append("")
            try:
                company_locations.append(card_details.find_element(By.XPATH, '//label[@class = "BreadcrumbStyle__BreadcrumbItemWrapper-sc-eq3cq-0 dsnNWZ aries-breadcrumb-item"][3]').text)
            except:
                company_locations.append("")
            try:
                category.append(card_details.find_element(By.XPATH, '//a[contains(@href, "category")]').text)
            except:
                category.append("")
            try:
                type_job.append(card_details.find_element(By.XPATH, '//div[@class = "TopFoldsc__JobOverViewInfo-sc-kklg8i-9 EWOdY"][2]').text)
            except:
                type_job.append("")
            try:
                experience.append(card_details.find_element(By.XPATH, '//div[@class = "TopFoldsc__JobOverViewInfo-sc-kklg8i-9 EWOdY"][3]').text)
            except:
                experience.append("")
            try:
                post_dates.append(card_details.find_element(By.XPATH, '//span[contains(@class, "TopFoldsc__PostedAt")]').text)
            except:
                post_dates.append("")
        except:
            pass
        try:
            description = driver.find_element(By.XPATH, '//div[@class = "Opportunitysc__JobDescriptionContainer-sc-1gsvee3-6 jJdHiW"]')
            driver.execute_script("arguments[0].scrollIntoView();", description)
            try:
                description.find_element(By.XPATH, '//div[@class = "JobDescriptionsc__ReadButton-sc-1jylha1-3 eyhdGn"]/button/span').click()
            except:
                description.find_element(By.XPATH, '//div[@class = "JobDescriptionsc__ReadButton-sc-1jylha1-3 eyhdGn"]/button/span').click()
        except:
            pass
        time.sleep(2)
        try:
            job_text = driver.find_element(By.XPATH, '//div[contains(@class, "JobDescriptionContainer")]').text
            job_desc.append(job_text)
        except:
            job_desc.append("")

    # Creating the dataframe 
    df = pd.DataFrame(list(zip(job_titles,company_names,
                        company_locations,post_dates,salary, category, type_job, experience, job_desc)),
                        columns =['Job Title', 'Company Name',
                            'Company Location','Post Date', 'Salary', 'Category', 
                            'Type Job', 'Experience', 'Job Description'])

    # Storing the data to csv file
    df.to_csv(csv_file, index=False)