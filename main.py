import time, json, asyncio
from selenium import webdriver
from bs4 import BeautifulSoup


def run_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver


def main(driver):
    # try:
        # while True:
            # Load the HTML content
            driver.get('https://www.niche.com/colleges/yale-university/')

            # Extract HTML content
            html_content = driver.page_source

            # Parse the HTML using BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extracting data
            data = {}

            # Title
            data['Title'] = soup.find('h1', class_='postcard__title').text.strip()

            # Images
            image_container = soup.find('div', class_='postcard__image-container')
            images = [img['srcset'] for img in image_container.find_all('source')]
            data['Images'] = images

            # Badge
            data['Badge'] = soup.find('div', class_='postcard__badge').text.strip()

            # Facts
            facts = soup.select('.postcard__attr.postcard-fact')
            fact_list = [fact.text.strip() for fact in facts]
            data['Facts'] = fact_list

            # Ratings
            rating_reviews = soup.find('li', class_='postcard__attr--has-reviews').text.strip().split(' \xa0')
            data['Ratings'] = rating_reviews[0]

            # No of Reviews
            data['No of Reviews'] = rating_reviews[1]

            # Extracting report_card data
            report_card = {}

            # Overall Grade
            overall_grade = soup.find('div', class_='overall-grade__niche-grade').text.strip().replace('\xa0', ' ')
            report_card['Overall Grade'] = overall_grade

            # Other Grades
            grades = soup.find_all('div', class_='profile-grade--two')
            for grade in grades:
                label = grade.find('div', class_='profile-grade__label').text.strip()
                value = grade.find('div', class_='niche__grade').text.strip().replace('\xa0', ' ')
                report_card[label] = value

            data['Report Card'] = report_card
            data['editorial'] = soup.find('span', class_='bare-value').text.strip()

            about = {}

            # Website
            website = soup.find(class_='profile__website__link').get('href')
            about['Website'] = website

            # Address
            address = soup.find(class_='profile__address--compact').get_text(separator=' ', strip=True)
            about['Address'] = address

            # About
            about_text = [item.get_text() for item in soup.select('.search-tags__wrap__list__tag__a')]
            about['About'] = about_text

            # Athletic Division
            athletic_division = soup.find(class_='scalar__value').get_text(strip=True)
            about['Athletic Division'] = athletic_division

            # Athletic Conference
            athletic_conference = soup.find_all(class_='scalar__value')[1].get_text(strip=True)
            about['Athletic Conference'] = athletic_conference

            data['About'] = about

            # Extracting the rankings
            rankings = []

            # Find all ranking items
            ranking_items = soup.find_all('li', class_='rankings__collection__item')

            # Iterate through each ranking item
            for item in ranking_items:
                # Extract ranking name
                ranking_name = item.find('div', class_='rankings__collection__name').get_text()
                # Extract ranking value
                ranking_value = item.find('span', class_='rankings__collection__ordinal').get_text()
                # Append to the rankings list
                rankings.append({ranking_name: ranking_value})
            
            data['Rankings'] = rankings
            print(data)

            # Close the WebDriver
            driver.quit()


    # except Exception as e:
    #     print(f"Error in main function: {e}")


if __name__ == "__main__":
    driver = run_driver()
    main(driver)
