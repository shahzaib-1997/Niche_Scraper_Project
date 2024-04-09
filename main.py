import time, json
from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


def run_driver():
    options = ChromeOptions()
    driver = Chrome(options=options)
    driver.maximize_window()
    return driver


def main(driver):
    # try:
    # while True:
    # Load the HTML content
    driver.get("https://www.niche.com/colleges/yale-university/")
    input("..")

    # Extract HTML content
    html_content = driver.page_source

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Extracting data
    data = {}

    wait = WebDriverWait(driver, 20)

    try:
        # Wait for the OK button to be clickable
        cookies_button = wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "cookie-banner__confirm-button"))
        )

        # Click on the OK button
        cookies_button.click()
    except:
        pass

    # Title
    data["Title"] = soup.find(
        "h1", class_="postcard__title postcard__title--claimed"
    ).text.strip()

    # Images
    image_container = soup.find("div", class_="postcard__image-container")
    images = [img["srcset"] for img in image_container.find_all("source")]
    data["Images"] = images

    # Badge
    data["Badge"] = soup.find("div", class_="postcard__badge").text.strip()

    # Facts
    facts = soup.select(".postcard__attr.postcard-fact")
    fact_list = [fact.text.strip() for fact in facts]
    data["Facts"] = fact_list

    # Ratings
    rating_reviews = (
        soup.find("li", class_="postcard__attr--has-reviews")
        .text.strip()
        .split(" \xa0")
    )
    data["Ratings"] = rating_reviews[0]

    # No of Reviews
    data["No of Reviews"] = rating_reviews[1]

    # Extracting report_card data
    report_card = {}

    # Overall Grade
    overall_grade = (
        soup.find("div", class_="overall-grade__niche-grade")
        .text.strip()
        .replace("\xa0", " ")
    )
    report_card["Overall Grade"] = overall_grade

    # Other Grades
    grades = soup.find_all("div", class_="profile-grade--two")
    for grade in grades:
        label = grade.find("div", class_="profile-grade__label").text.strip()
        value = (
            grade.find("div", class_="niche__grade").text.strip().replace("\xa0", " ")
        )
        report_card[label] = value

    data["Report Card"] = report_card
    data["editorial"] = soup.find("span", class_="bare-value").text.strip()

    about = {}

    # Website
    website = soup.find(class_="profile__website__link").get("href")
    about["Website"] = website

    # Address
    address = soup.find(class_="profile__address--compact").get_text(
        separator=" ", strip=True
    )
    about["Address"] = address

    # About
    about_text = [
        item.get_text() for item in soup.select(".search-tags__wrap__list__tag__a")
    ]
    about["About"] = about_text

    # Athletic Division
    athletic_division = soup.find(class_="scalar__value").get_text(strip=True)
    about["Athletic Division"] = athletic_division

    # Athletic Conference
    athletic_conference = soup.find_all(class_="scalar__value")[1].get_text(strip=True)
    about["Athletic Conference"] = athletic_conference

    data["About"] = about

    # Extracting the rankings
    rankings = []

    # Find all ranking items
    ranking_items = soup.find_all("li", class_="rankings__collection__item")

    # Iterate through each ranking item
    for item in ranking_items:
        # Extract ranking name
        ranking_name = item.find("div", class_="rankings__collection__name").get_text()
        # Extract ranking value
        ranking_value = item.find(
            "div", class_="rankings__collection__ranking"
        ).get_text()
        # Append to the rankings list
        rankings.append({ranking_name: ranking_value})

    data["Rankings"] = rankings

    # Extracting the required data
    admissions_data = {}

    admissions_link = driver.find_element(
        By.XPATH,
        "(//a[@class='expansion-link__text'])[2]",
    )
    admissions_link.click()

    # Acceptance Rate Description
    acceptance_rate_description = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "(//div[@class='profile__bucket--1'])[2]")
        )
    )
    admissions_data["description"] = acceptance_rate_description.text

    admission_page_source = driver.page_source
    admission_page_soup = BeautifulSoup(admission_page_source, "html.parser")

    # Extract data from the "Admissions Statistics" section
    admissions_statistics_section = admission_page_soup.find(
        "section", {"id": "admissions-statistics"}
    )

    if admissions_statistics_section:
        # Extract Acceptance Rate
        acceptance_rate = (
            admissions_statistics_section.find("div", string="Acceptance Rate")
            .find_next_sibling("div", class_="scalar__value")
            .get_text(strip=True)
        )
        admissions_data["acceptance_rate"] = acceptance_rate

        # Extract SAT Range
        sat_range = (
            admissions_statistics_section.find("div", string="SAT Range")
            .find_next_sibling("div", class_="scalar__value")
            .get_text(strip=True)
        )
        admissions_data["SAT_Range"] = sat_range

        # Extract SAT Reading
        sat_reading = (
            admissions_statistics_section.find("div", string="SAT Reading")
            .find_next_sibling("div", class_="scalar__value")
            .get_text(strip=True)
        )
        admissions_data["SAT_Reading"] = sat_reading

        # Extract SAT Math
        sat_math = (
            admissions_statistics_section.find("div", string="SAT Math")
            .find_next_sibling("div", class_="scalar__value")
            .get_text(strip=True)
        )
        admissions_data["SAT_MATH"] = sat_math

        # Extract Students Submitting SAT
        submitting_sat = (
            admissions_statistics_section.find("div", string="Students Submitting SAT")
            .find_next_sibling("div", class_="scalar__value")
            .get_text(strip=True)
        )
        admissions_data["submitting_SAT"] = submitting_sat
        
        try:
            # Extract Early Decision Acceptance Rate
            early_decision_acceptance_rate = (
                admissions_statistics_section.find(
                    "div", string="Early Decision Acceptance Rate"
                )
                .find_next_sibling("div", class_="scalar__value")
                .get_text(strip=True)
            )
        except:
            early_decision_acceptance_rate = "—"
        admissions_data["early_decision_acceptance_rate"] = early_decision_acceptance_rate

        # Extract Total Applicants
        total_applicants = (
            admissions_statistics_section.find("div", string="Total Applicants")
            .find_next_sibling("div", class_="scalar__value")
            .get_text(strip=True)
        )
        admissions_data["total_applicants"] = total_applicants

        # Extract ACT Range
        act_range = (
            admissions_statistics_section.find("div", string="ACT Range")
            .find_next_sibling("div", class_="scalar__value")
            .get_text(strip=True)
        )
        admissions_data["ACT_Range"] = act_range

        # Extract ACT English
        act_english = (
            admissions_statistics_section.find("div", string="ACT English")
            .find_next_sibling("div", class_="scalar__value")
            .get_text(strip=True)
        )
        admissions_data["ACT_English"] = act_english

        # Extract ACT Math
        act_math = (
            admissions_statistics_section.find("div", string="ACT Math")
            .find_next_sibling("div", class_="scalar__value")
            .get_text(strip=True)
        )
        admissions_data["ACT_MATH"] = act_math

        try:
            # Extract ACT Writing
            act_writing = (
                admissions_statistics_section.find("div", string="ACT Writing")
                .find_next_sibling("div", class_="scalar__value")
                .get_text(strip=True)
            )
        except:
            act_writing = "—"
        admissions_data["ACT_writing"] = act_writing

        # Extract Students Submitting ACT
        students_submitting_act = (
            admissions_statistics_section.find("div", string="Students Submitting ACT")
            .find_next_sibling("div", class_="scalar__value")
            .get_text(strip=True)
        )
        admissions_data["Student_submiting_act"] = students_submitting_act

    # Extract data from the "Admissions Deadlines" section
    admissions_deadlines_section = admission_page_soup.find("section", {"id": "admissions-deadlines"})
    if admissions_deadlines_section:
        # Extract Application Deadline
        application_deadline = (
            admissions_deadlines_section.find("div", string="Application Deadline")
            .find_next_sibling("div", class_="scalar__value")
            .get_text(strip=True)
        )
        admissions_data["application_deadline"] = application_deadline

        try:
            # Extract Early Decision Deadline
            early_decision_deadline = (
                admissions_deadlines_section.find("div", string="Early Decision Deadline")
                .find_next_sibling("div", class_="scalar__value")
                .get_text(strip=True)
            )
        except:
            early_decision_deadline = "—"
        admissions_data["early_decision_deadline"] = early_decision_deadline

        # Extract Early Action Deadline
        early_action_deadline = (
            admissions_deadlines_section.find("div", string="Early Action Deadline")
            .find_next_sibling("div", class_="scalar__value")
            .get_text(strip=True)
        )
        admissions_data["early_action_deadline"] = early_action_deadline

        # Extract Offers Early Decision
        offers_early_decision = (
            admissions_deadlines_section.find("div", string="Offers Early Decision")
            .find_next_sibling("div", class_="scalar__value")
            .get_text(strip=True)
        )
        admissions_data["offers_early_decision"] = offers_early_decision

        # Extract Offers Early Action
        offers_early_action = (
            admissions_deadlines_section.find("div", string="Offers Early Action")
            .find_next_sibling("div", class_="scalar__value")
            .get_text(strip=True)
        )
        admissions_data["offers_early_action"] = offers_early_action

        # Application Fee
        application_fee = (
            admissions_deadlines_section.find_all(
                "div", class_="scalar__label"
            )[5].find_next_sibling("div", class_="scalar__value")
            .get_text(strip=True)
        )
        admissions_data["application_fee"] = application_fee

        # Application Website
        application_website = (
            admissions_deadlines_section.find("div", class_="profile__website")
            .find("a", class_="profile__website__link")
            .get("href")
        )
        admissions_data["application_website"] = application_website

        # Extract Accepts Common App
        accepts_common_app = (
            admissions_deadlines_section.find("div", string="Accepts Common App")
            .find_next_sibling("div", class_="scalar__value")
            .get_text(strip=True)
        )
        admissions_data["accepts_common_app"] = accepts_common_app

        # Extract Accepts Coalition App
        accepts_coalition_app = (
            admissions_deadlines_section.find("div", string="Accepts Coalition App")
            .find_next_sibling("div", class_="scalar__value")
            .get_text(strip=True)
        )
        admissions_data["accepts_coalition_app"] = accepts_coalition_app

    # Extract data from the "Admissions Requirements" section
    admissions_requirements_section = admission_page_soup.find(
        "section", {"id": "admissions-requirements"}
    )

    if admissions_requirements_section:
        # Extract High School GPA
        high_school_gpa = (
            admissions_requirements_section.find("div", string="High School GPA")
            .find_next_sibling("div", class_="fact__table__row__value")
            .get_text(strip=True)
        )
        admissions_data["high_school_gpa"] = high_school_gpa

        # Extract High School Rank
        high_school_rank = (
            admissions_requirements_section.find("div", string="High School Rank")
            .find_next_sibling("div", class_="fact__table__row__value")
            .get_text(strip=True)
        )
        admissions_data["high_school_rank"] = high_school_rank

        # Extract High School Transcript
        high_school_transcript = (
            admissions_requirements_section.find(
                "div", string="High School Transcript"
            )
            .find_next_sibling("div", class_="fact__table__row__value")
            .get_text(strip=True)
        )
        admissions_data["high_school_transcript"] = high_school_transcript

        # Extract College Prep Courses
        college_prep_courses = (
            admissions_requirements_section.find("div", string="College Prep Courses")
            .find_next_sibling("div", class_="fact__table__row__value")
            .get_text(strip=True)
        )
        admissions_data["college_prep_courses"] = college_prep_courses

        # Extract SAT/ACT
        sat_act = (
            admissions_requirements_section.find("div", string="SAT/ACT")
            .find_next_sibling("div", class_="fact__table__row__value")
            .get_text(strip=True)
        )
        admissions_data["SAT/ACT"] = sat_act

        # Extract Recommendations
        recommendations = (
            admissions_requirements_section.find("div", string="Recommendations")
            .find_next_sibling("div", class_="fact__table__row__value")
            .get_text(strip=True)
        )
        admissions_data["Recommendations"] = recommendations

    data["Admissions"] = admissions_data

    # Navigate to the previous page
    driver.back()

    # Cost
    cost_data = {}

    # Net Price
    net_price_label = soup.find("div", class_="scalar__label", string="Net Price")
    net_price_value = None

    # Find the following sibling div with class 'scalar__value'
    if net_price_label:
        net_price_element = net_price_label.find_next_sibling(
            "div", class_="scalar__value"
        )
        if net_price_element:
            net_price_value = net_price_element.get_text(strip=True)
            print(net_price_value)

    cost_data["net_price"] = net_price_value

    # Average Total Aid Awarded
    avg_total_aid_element = soup.find(
        "div", class_="scalar__label", string="Average Total Aid Awarded"
    )
    if avg_total_aid_element:
        avg_total_aid_value = avg_total_aid_element.find_next_sibling(
            "div", class_="scalar__value"
        ).get_text(strip=True)
        cost_data["avg_total_aid_awarded"] = avg_total_aid_value

    # Students Receiving Financial Aid
    students_receiving_aid_element = soup.find(
        "div", class_="scalar__label", string="Students Receiving Financial Aid"
    )
    if students_receiving_aid_element:
        students_receiving_aid_value = students_receiving_aid_element.find_next_sibling(
            "div", class_="scalar__value"
        ).get_text(strip=True)
        cost_data["students_receiving_financial_aid"] = students_receiving_aid_value

    # In-State Tuition
    in_state_tuition_element = soup.find(
        "div", class_="scalar__label", string="In-State Tuition"
    )
    if in_state_tuition_element:
        in_state_tuition_value = in_state_tuition_element.find_next_sibling(
            "div", class_="scalar__value"
        ).get_text(strip=True)
        cost_data["in_state_tuition"] = in_state_tuition_value

    # Average Housing Cost
    average_housing_cost_element = soup.find(
        "div", class_="scalar__label", string="Average Housing Cost"
    )
    if average_housing_cost_element:
        average_housing_cost_value = average_housing_cost_element.find_next_sibling(
            "div", class_="scalar__value"
        ).get_text(strip=True)
        cost_data["average_housing_cost"] = average_housing_cost_value

    # Average Meal Plan Cost
    average_meal_plan_cost_element = soup.find(
        "div", class_="scalar__label", string="Average Meal Plan Cost"
    )
    if average_meal_plan_cost_element:
        average_meal_plan_cost_value = average_meal_plan_cost_element.find_next_sibling(
            "div", class_="scalar__value"
        ).get_text(strip=True)
        cost_data["average_meal_plan_cost"] = average_meal_plan_cost_value

    # Books and Supplies
    books_supplies_element = soup.find(
        "div", class_="scalar__label", string="Books and Supplies"
    )
    if books_supplies_element:
        books_supplies_value = books_supplies_element.find_next_sibling(
            "div", class_="scalar__value"
        ).get_text(strip=True)
        cost_data["book_and_supplies"] = books_supplies_value

    # Out-of-State Tuition
    out_of_state_tuition_element = soup.find(
        "div", class_="scalar__label", string="Out-of-State Tuition"
    )
    if out_of_state_tuition_element:
        out_of_state_tuition_value = out_of_state_tuition_element.find_next_sibling(
            "div", class_="scalar__value"
        ).get_text(strip=True)
        cost_data["out_of_state_tuition"] = out_of_state_tuition_value

    # Tuition Guarantee Plan
    tuition_guarantee_element = soup.find(
        "div", class_="scalar__label", string="Tuition Guarantee Plan"
    )
    if tuition_guarantee_element:
        tuition_guarantee_value = tuition_guarantee_element.find_next_sibling(
            "div", class_="scalar__value"
        ).get_text(strip=True)
        cost_data["tuition_gurantee_plan"] = tuition_guarantee_value

    # Tuition Payment Plan
    tuition_payment_plan_element = soup.find(
        "div", class_="scalar__label", string="Tuition Payment Plan"
    )
    if tuition_payment_plan_element:
        tuition_payment_plan_value = tuition_payment_plan_element.find_next_sibling(
            "div", class_="scalar__value"
        ).get_text(strip=True)
        cost_data["tuition_payment_plan"] = tuition_payment_plan_value

    # Prepaid Tuition Plan
    prepaid_tuition_plan_element = soup.find(
        "div", class_="scalar__label", string="Prepaid Tuition Plan"
    )
    if prepaid_tuition_plan_element:
        prepaid_tuition_plan_value = prepaid_tuition_plan_element.find_next_sibling(
            "div", class_="scalar__value"
        ).get_text(strip=True)
        cost_data["prepaid_tution_plan"] = prepaid_tuition_plan_value

    data["Cost"] = cost_data

    print(data)

    # Close the WebDriver
    driver.quit()

    # Open the JSON file for writing
    with open("data.json", "w") as file:
        # Write JSON data to the file
        json.dump(data, file)


# except Exception as e:
#     print(f"Error in main function: {e}")


if __name__ == "__main__":
    driver = run_driver()
    main(driver)
