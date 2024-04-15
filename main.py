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


def remove_unicode_chars(data):
    cleaned_dict = {}
    if isinstance(data, dict):
        for key, value in data.items():
            cleaned_dict[key] = remove_unicode_chars(value)
    elif isinstance(data, list):
        return [remove_unicode_chars(item) for item in data]
    elif isinstance(data, str):
        return data.replace("\u00a0", "").replace("\u2014", "").replace("National", " National ").replace("\xa0", " ")
    return cleaned_dict


def main(driver):
    # try:
    # while True:
    wait = WebDriverWait(driver, 20)
    driver.get("https://www.niche.com/")
    input("..")

    try:
        # Wait for the OK button to be clickable
        cookies_button = wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "cookie-banner__confirm-button"))
        )

        # Click on the OK button
        cookies_button.click()
    except:
        pass

    colleges_button = driver.find_element(By.XPATH, "(//li[@class='home-hero__cta'])[2]")
    colleges_button.click()

    total_pages = int(wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//button[contains(@class, "nss-1bxikzx")]')))[-1].text)
    search_url = driver.current_url
    for i in range(total_pages):
        colleges_link = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@class, "search-result__link")]')))
        urls = [link.get_attribute("href") for link in colleges_link]

        for url in urls:
            driver.get(url)

            # Extract HTML content
            html_content = driver.page_source

            # Parse the HTML using BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")

            # Extracting data
            data = {}

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
            )
            report_card["Overall Grade"] = overall_grade

            # Other Grades
            grades = soup.find_all("div", class_="profile-grade--two")
            for grade in grades:
                label = grade.find("div", class_="profile-grade__label").text.strip()
                value = (
                    grade.find("div", class_="niche__grade").text.strip()
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

            url = driver.current_url
            driver.get(f"{url}rankings/")

            # Extracting the rankings
            rankings = []

            rankings_page_source = driver.page_source
            rankings_page_soup = BeautifulSoup(rankings_page_source, "html.parser")

            # Find all ranking items
            ranking_names = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="rankings-card__link__title"]')))

            # Iterate through each ranking item
            for item in ranking_names:
                # Extract ranking name
                ranking_name = item.text
                # Extract ranking value
                ranking_value = item.find_element(By.XPATH,
                    "following-sibling::div"
                ).text
                # Append to the rankings list
                rankings.append({ranking_name: ranking_value})

            data["Rankings"] = rankings

            # Extracting the required data
            admissions_data = {}
            driver.get(f"{url}admissions/")

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
                    early_decision_acceptance_rate = "NA"
                admissions_data["early_decision_acceptance_rate"] = (
                    early_decision_acceptance_rate
                )

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
            admissions_deadlines_section = admission_page_soup.find(
                "section", {"id": "admissions-deadlines"}
            )
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
                        admissions_deadlines_section.find(
                            "div", string="Early Decision Deadline"
                        )
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
                    admissions_deadlines_section.find_all("div", class_="scalar__label")[5]
                    .find_next_sibling("div", class_="scalar__value")
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
                    admissions_requirements_section.find("div", string="High School Transcript")
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

            # Cost
            cost_data = {}

            # Navigate to the cost page
            driver.get(f"{url}cost/")
            time.sleep(5)

            cost_page_source = driver.page_source
            cost_page_soup = BeautifulSoup(cost_page_source, "html.parser")

            # Net Price
            net_price_label = cost_page_soup.find(
                "div", class_="scalar__label", string="Net Price"
            )
            net_price_value = None

            # Find the following sibling div with class 'scalar__value'
            if net_price_label:
                net_price_element = net_price_label.find_next_sibling(
                    "div", class_="scalar__value"
                )
                if net_price_element:
                    net_price_value = net_price_element.get_text(strip=True)

            cost_data["net_price"] = net_price_value

            # Average Total Aid Awarded
            avg_total_aid_element = cost_page_soup.find(
                "div", class_="scalar__label", string="Average Total Aid Awarded"
            )
            if avg_total_aid_element:
                avg_total_aid_value = avg_total_aid_element.find_next_sibling(
                    "div", class_="scalar__value"
                ).get_text(strip=True)
                cost_data["avg_total_aid_awarded"] = avg_total_aid_value

            # Students Receiving Financial Aid
            students_receiving_aid_element = cost_page_soup.find(
                "div", class_="scalar__label", string="Students Receiving Financial Aid"
            )
            if students_receiving_aid_element:
                students_receiving_aid_value = students_receiving_aid_element.find_next_sibling(
                    "div", class_="scalar__value"
                ).get_text(strip=True)
                cost_data["students_receiving_financial_aid"] = students_receiving_aid_value

            # In-State Tuition
            in_state_tuition_element = cost_page_soup.find(
                "div", class_="scalar__label", string="In-State Tuition"
            )
            if in_state_tuition_element:
                in_state_tuition_value = in_state_tuition_element.find_next_sibling(
                    "div", class_="scalar__value"
                ).get_text(strip=True)
                cost_data["in_state_tuition"] = in_state_tuition_value

            # Out-of-State Tuition
            out_of_state_tuition_element = cost_page_soup.find(
                "div", class_="scalar__label", string="Out-of-State Tuition"
            )
            if out_of_state_tuition_element:
                out_of_state_tuition_value = out_of_state_tuition_element.find_next_sibling("div", class_="scalar__value").get_text(strip=True)
                cost_data["out_of_state_tuition"] = out_of_state_tuition_value

            # Average Housing Cost
            average_housing_cost_element = cost_page_soup.find(
                "div", class_="scalar__label", string="Average Housing Cost"
            )
            if average_housing_cost_element:
                average_housing_cost_value = average_housing_cost_element.find_next_sibling(
                    "div", class_="scalar__value"
                ).get_text(strip=True)
                cost_data["average_housing_cost"] = average_housing_cost_value

            # Average Meal Plan Cost
            average_meal_plan_cost_element = cost_page_soup.find(
                "div", class_="scalar__label", string="Average Meal Plan Cost"
            )
            if average_meal_plan_cost_element:
                average_meal_plan_cost_value = average_meal_plan_cost_element.find_next_sibling(
                    "div", class_="scalar__value"
                ).get_text(strip=True)
                cost_data["average_meal_plan_cost"] = average_meal_plan_cost_value

            # Books and Supplies
            books_supplies_element = cost_page_soup.find(
                "div", class_="scalar__label", string="Books & Supplies"
            )
            if books_supplies_element:
                books_supplies_value_element = books_supplies_element.find_next_sibling(
                    "div", class_="scalar__value"
                )
                books_supplies_value = books_supplies_value_element.get_text(strip=True)
                cost_data["book_and_supplies"] = books_supplies_value

            # Tuition Guarantee Plan
            tuition_guarantee_value_element = books_supplies_value_element.find_next(
                "div", class_="scalar__value"
            )
            tuition_guarantee_value = tuition_guarantee_value_element.get_text(strip=True)
            cost_data["tuition_gurantee_plan"] = tuition_guarantee_value

            # Tuition Payment Plan
            tuition_payment_plan_value_element = tuition_guarantee_value_element.find_next(
                "div", class_="scalar__value"
            )
            tuition_payment_plan_value = tuition_payment_plan_value_element.get_text(strip=True)
            cost_data["tuition_payment_plan"] = tuition_payment_plan_value

            # Prepaid Tuition Plan
            prepaid_tuition_plan_value = tuition_payment_plan_value_element.find_next(
                "div", class_="scalar__value"
            ).get_text(strip=True)
            cost_data["prepaid_tution_plan"] = prepaid_tuition_plan_value

            data["Cost"] = cost_data

            academics_data = {}
            driver.get(f"{url}academics/")
            time.sleep(5)

            academics_page_source = driver.page_source
            academics_page_soup = BeautifulSoup(academics_page_source, "html.parser")

            graduation_rate_element = academics_page_soup.find(
                "div", class_="scalar__label", string="Graduation Rate"
            )
            graduation_rate_value_element = graduation_rate_element.find_next(
                "div", class_="scalar__value"
            )
            academics_data["graduation_rate"] = graduation_rate_value_element.text

            full_time_retention_rate_value_element = graduation_rate_value_element.find_next(
                "div", class_="scalar__label"
            ).find_next_sibling("div")
            academics_data["full_time_retention_rate"] = (
                full_time_retention_rate_value_element.text
            )

            part_time_retention_rate_value_element = (
                full_time_retention_rate_value_element.find_next(
                    "div", class_="scalar__label"
                ).find_next_sibling("div")
            )
            academics_data["part_time_retention_rate"] = (
                part_time_retention_rate_value_element.text
            )

            academic_calendar_value_element = part_time_retention_rate_value_element.find_next(
                "div", class_="scalar__label"
            ).find_next_sibling("div")
            academics_data["academic_calendar"] = academic_calendar_value_element.text

            research_funding_student_value_element = academic_calendar_value_element.find_next(
                "div", class_="scalar__label"
            ).find_next_sibling("div")
            academics_data["research_funding_student"] = (
                research_funding_student_value_element.text
            )

            non_traditional_learning_elements = academics_page_soup.find_all(
                "li", class_="fact__table__row"
            )[:3]
            academics_data["evening_degree_programs"] = (
                non_traditional_learning_elements[0]
                .find("div", class_="fact__table__row__value")
                .text
            )
            academics_data["teacher_certification"] = (
                non_traditional_learning_elements[1]
                .find("div", class_="fact__table__row__value")
                .text
            )
            academics_data["study_abroad"] = (
                non_traditional_learning_elements[2]
                .find("div", class_="fact__table__row__value")
                .text
            )

            faculty = {}

            faculty_section = academics_page_soup.find(
                "section", {"id": "about-the-professors"}
            )
            student_faculty_ratio_element = faculty_section.find(
                "div", class_="scalar__label", string="Student Faculty Ratio"
            )
            student_faculty_ratio_value_element = student_faculty_ratio_element.find_next(
                "div", class_="scalar__value"
            )
            faculty["student_faculty_ratio"] = student_faculty_ratio_value_element.text

            female_professors_value_element = student_faculty_ratio_value_element.find_next(
                "div", class_="scalar__label"
            ).find_next_sibling("div")
            faculty["female_professors"] = female_professors_value_element.text

            male_professors_value_element = female_professors_value_element.find_next(
                "div", class_="scalar__label"
            ).find_next_sibling("div")
            faculty["male_professors"] = male_professors_value_element.text

            average_professor_salary_value_element = male_professors_value_element.find_next(
                "div", class_="scalar__label"
            ).find_next_sibling("div")
            faculty["average_professor_salary"] = average_professor_salary_value_element.text

            faculty_poll_value_element = average_professor_salary_value_element.find_next(
                "div"
            ).find("div", class_="poll__single__percent poll__single__percent__label")
            faculty["faculty_poll"] = faculty_poll_value_element.text

            academics_data["faculty"] = faculty
            data["Academics"] = academics_data

            majors = {}
            majors_section = soup.find("section", {"id": "majors"})
            if majors_section:
                majors_names = majors_section.find_all("div", class_="popular-entity__name")
                for m in majors_names:
                    majors[m.text] = m.find_next("div").text

            data["Majors"] = majors

            online = {}
            online_section = soup.find("section", {"id": "online"})
            if online_section:
                online_labels = online_section.find_all("div", class_="scalar__label")
                for o in online_labels:
                    online[o.find("span").text] = o.find_next_sibling("div").text

            data["Online"] = online

            students = {}
            students_section = soup.find("section", {"id": "students"})
            if students_section:
                students_labels = students_section.find_all("div", class_="scalar__label")
                for s in students_labels:
                    students[s.text] = s.find_next("div").text

            data["Students"] = students

            campus_life = {}
            driver.get(f"{url}campus-life/")
            time.sleep(5)

            campus_life_page_source = driver.page_source
            campus_life_page_soup = BeautifulSoup(campus_life_page_source, "html.parser")
            campus_life_labels = campus_life_page_soup.find_all("div", class_="scalar__label")
            for s in campus_life_labels:
                campus_life[s.text] = s.find_next("div").text

            data["Campus Life"] = campus_life

            after_college = {}
            after_college_section = soup.find("section", {"id": "after"})
            if after_college_section:
                after_college_labels = after_college_section.find_all("div", class_="scalar__label")
                for s in after_college_labels:
                    after_college[s.text] = s.find_next("div").text

            data["after_college"] = after_college

            reviews = []
            driver.get(f"{url}reviews/")
            time.sleep(5)

            reviews_page_source = driver.page_source
            reviews_page_soup = BeautifulSoup(reviews_page_source, "html.parser")
            reviews_section = reviews_page_soup.find("section", class_="reviews-expansion-bucket")
            review_stars = reviews_section.find_all("div", class_="review__stars")
            for s in review_stars:
                reviews.append({
                    "rating": s.text,
                    "text": s.find_next("div").text
                }) 

            data["Reviews"] = reviews

            cleaned_data = remove_unicode_chars(data)

            # Open the JSON file for writing
            with open("data.json", "a") as file:
                # Write JSON data to the file
                json.dump(cleaned_data, file)
                file.write('\n')

            break
        driver.get(f"{search_url}?page={i+2}")
        if i >= 1:
            break
    # Close the WebDriver
    driver.quit()

# except Exception as e:
#     print(f"Error in main function: {e}")


if __name__ == "__main__":
    driver = run_driver()
    main(driver)
