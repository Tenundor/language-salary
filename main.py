from dotenv import load_dotenv
from itertools import count
import os
import requests
from pprint import pprint


def get_filtered_vacancies_hh(
        user_agent_name,
        specialization_id="",
        area="",
        period="",
        search_text="",
):
    hh_api_url = "https://api.hh.ru/vacancies"
    vacancies_request_parameters = {
        "specialization": specialization_id,
        "area": area,
        "period": period,
        "text": search_text,
    }
    vacancies_request_header = {"User-Agent": user_agent_name}
    total_pages_number = 0
    for vacancies_page_number in count():
        if total_pages_number and vacancies_page_number >= total_pages_number:
            break
        vacancies_request_parameters["page"] = vacancies_page_number
        vacancies_page_response = requests.get(
            hh_api_url,
            params=vacancies_request_parameters,
            headers=vacancies_request_header,
        )
        vacancies_page_response.raise_for_status()
        vacancies_page_json = vacancies_page_response.json()
        total_pages_number = vacancies_page_json["pages"]
        yield vacancies_page_json


def predict_rub_salary_hh(vacancy_hh):
    vacancy_salary = vacancy_hh["salary"]
    if vacancy_salary is None or vacancy_salary["currency"] != "RUR":
        return None
    rub_salary_from = vacancy_salary["from"]
    rub_salary_to = vacancy_salary["to"]
    if rub_salary_from is None:
        return int(rub_salary_to * 0.8)
    if rub_salary_to is None:
        return int(rub_salary_from * 1.2)
    else:
        return int((rub_salary_from + rub_salary_to) / 2)


def predict_average_rub_salary(hh_vacancies_generator):
    vacancies_predicted_rub_salary = []
    for hh_vacancies_page in hh_vacancies_generator:
        current_page_number = hh_vacancies_page["page"] + 1
        total_pages_number = hh_vacancies_page["pages"]
        print("{} from {} pages downloaded.".format(current_page_number, total_pages_number))
        vacancies_predicted_rub_salary += [
        predict_rub_salary_hh(vacancy) for vacancy in hh_vacancies_page["items"]
    ]
    quantity_founded_vacancies = len(vacancies_predicted_rub_salary)
    correct_vacancies_salary = list(filter(lambda salary: type(salary) is int, vacancies_predicted_rub_salary))
    quantity_correct_vacancies_salary = len(correct_vacancies_salary)
    average_language_salary = int(sum(correct_vacancies_salary) / quantity_correct_vacancies_salary)
    return {
        "vacancies_found": quantity_founded_vacancies,
        "vacancies_processed": quantity_correct_vacancies_salary,
        "average_salary": average_language_salary,
    }


def get_filtered_vacancies_superjob(
        authorization_key,
        town_superjob_id,
        catalogues_superjob,

):
    superjob_api_url = "https://api.superjob.ru/2.0/vacancies"
    superjob_authorisation_header = {
        "X-Api-App-ID": authorization_key
    }
    superjob_response_parameters = {
        "town": town_superjob_id,
        "catalogues": catalogues_superjob,
    }
    superjob_request = requests.get(
        superjob_api_url,
        params=superjob_response_parameters,
        headers=superjob_authorisation_header,
    )
    superjob_request.raise_for_status()
    return superjob_request.json()


if __name__ == "__main__":
    load_dotenv()
    superjob_api_key = os.getenv("SUPERJOB_API_KEY")
    programming_languages = [
        "TypeScript", # "Swift", "Scala", "Objective-C", "Shell", "JavaScript",
        # "Go", "C", "C#", "C++", "PHP", "Ruby", "Python", "Java",
    ]

    programming_specialisation_id = "1.221"
    Moscow_id = "1"
    search_period_days = "30"
    user_agent_name = "Api-test-agent"
    average_rub_salary_by_languages = {}

    for programming_language in programming_languages:
        print("Язык программирования:", programming_language)
        language_vacancies_hh = get_filtered_vacancies_hh(
            user_agent_name=user_agent_name,
            specialization_id=programming_specialisation_id,
            area=Moscow_id,
            period=search_period_days,
            search_text=programming_language,
        )
        average_rub_salary_by_languages[programming_language] = predict_average_rub_salary(language_vacancies_hh)
    pprint(average_rub_salary_by_languages)
    moscow_superjob_id = 4
    superjob_programming_category_key = 48
    superjob_vacancies = get_filtered_vacancies_superjob(
        superjob_api_key,
        town_superjob_id=moscow_superjob_id,
        catalogues_superjob=superjob_programming_category_key
    )["objects"]

    for superjob_vacancy in superjob_vacancies:
        vacancy_name = superjob_vacancy["profession"]
        vacancy_town = superjob_vacancy["town"]["title"]
        print(vacancy_name, vacancy_town, sep=", ")



