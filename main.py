from dotenv import load_dotenv
from itertools import count
from math import ceil
import os
import requests
from pprint import pprint


def get_filtered_vacancies_page_hh(user_agent_name, filtering_options={}):
    hh_api_url = "https://api.hh.ru/vacancies"
    vacancies_request_parameters = dict({
        "specialization": "",
        "area": "",
        "period": "",
        "text": "",
        "page": "",
    }, **filtering_options)
    vacancies_request_header = {"User-Agent": user_agent_name}
    vacancies_page_response = requests.get(
        hh_api_url,
        params=vacancies_request_parameters,
        headers=vacancies_request_header,
    )
    vacancies_page_response.raise_for_status()
    vacancies_page_json = vacancies_page_response.json()

    return vacancies_page_json


def get_filtered_vacancies_generator_hh(user_agent_name, filtering_options={}):  # TODO: Добавь Try Except
    total_pages_number = 0
    for vacancies_page_index in count():
        if total_pages_number and vacancies_page_index >= total_pages_number:
            break
        filtering_options["page"] = vacancies_page_index
        vacancies_page_hh = get_filtered_vacancies_page_hh(
            user_agent_name,
            filtering_options,
        )
        total_pages_number = vacancies_page_hh["pages"]  # TODO вынеси принт в main
        vacancies_page_number = vacancies_page_hh["page"] + 1
        print(
            "hh.ru {}: {} from {} downloaded.".format(
                filtering_options["text"], vacancies_page_number, total_pages_number
            )
        )

        yield vacancies_page_hh["items"]


def get_actual_programming_vacancies_moscow_hh(programming_language, user_agent_name):
    language_vacancies_hh = get_filtered_vacancies_generator_hh(
        user_agent_name,
        filtering_options={
            "specialization": "1.221",  # Programming specialization id
            "area": 1,  # Moscow id
            "period": 30,  # days
            "text": programming_language,  # text to search in vacancies
        },
    )
    return language_vacancies_hh


def get_filtered_vacancies_sj(authorization_key, filtering_options={}):
    superjob_api_url = "https://api.superjob.ru/2.0/vacancies"
    superjob_authorisation_header = {"X-Api-App-ID": authorization_key}
    superjob_request_parameters = dict({
        "town": "",
        "catalogues": "",
        "count": 20,
        "keyword": "",
    }, **filtering_options)
    is_more_pages = True
    for page_index in count():
        if not is_more_pages:
            break
        superjob_request_parameters["page"] = page_index
        superjob_response = requests.get(  # TODO: Выдели в отдельную функцию или две.
            superjob_api_url,
            params=superjob_request_parameters,
            headers=superjob_authorisation_header,
        )
        superjob_response.raise_for_status()
        superjob_response_json = superjob_response.json()
        page_number = page_index + 1
        vacancies_per_page = superjob_request_parameters["count"]
        total_vacancies_quantity = superjob_response_json["total"]
        total_pages_quantity = ceil(total_vacancies_quantity / vacancies_per_page)
        print(
            "superjob.ru {}: {} from {} pages downloaded".format(
                superjob_request_parameters["keyword"], page_number, total_pages_quantity
            )
        )
        is_more_pages = superjob_response_json["more"]
        yield superjob_response_json["objects"]


def get_actual_programming_vacancies_moscow_sj(programming_language, authorization_key):
    language_vacancies_superjob = get_filtered_vacancies_sj(
        authorization_key,
        filtering_options={
            "town": 4,  # Moscow id
            "catalogues": 48,  # Programming category id
            "keyword": programming_language,
        },
    )
    return language_vacancies_superjob


def predict_salary(salary_from, salary_to):
    if not salary_from and not salary_to:
        return None
    if not salary_from:
        return int(salary_to * 0.8)
    if not salary_to:
        return int(salary_from * 1.2)
    else:
        return int((salary_from + salary_to) / 2)


def predict_rub_salary_hh(vacancy_hh):
    vacancy_salary = vacancy_hh["salary"]
    if not vacancy_salary or vacancy_salary["currency"] != "RUR":
        return None
    return predict_salary(vacancy_salary["from"], vacancy_salary["to"])


def predict_rub_salary_sj(vacancy_sj):
    if vacancy_sj["currency"] != "rub":
        return None
    return predict_salary(vacancy_sj["payment_from"], vacancy_sj["payment_to"])


def predict_average_salary(vacancies_predicted_salary):
    vacancies_quantity = len(vacancies_predicted_salary)
    processed_vacancies_salary = list(filter(lambda salary: type(salary) is int, vacancies_predicted_salary))
    processed_vacancies_quantity = len(processed_vacancies_salary)
    average_salary = int(sum(processed_vacancies_salary) / processed_vacancies_quantity)
    return {
        "vacancies_found": vacancies_quantity,
        "vacancies_processed": processed_vacancies_quantity,
        "average_salary": average_salary,
    }


def predict_average_rub_salary_hh(hh_vacancies_generator):  # TODO: избавиться от функций hh и sj
    vacancies_predicted_rub_salary = []
    for hh_vacancies_page in hh_vacancies_generator:
        vacancies_predicted_rub_salary += [
            predict_rub_salary_hh(vacancy) for vacancy in hh_vacancies_page
        ]
    return predict_average_salary(vacancies_predicted_rub_salary)


def predict_average_rub_salary_sj(sj_vacancies_generator):
    vacancies_predicted_rub_salary = []
    for sj_vacancies_page in sj_vacancies_generator:
        vacancies_predicted_rub_salary += [
            predict_rub_salary_sj(vacancy) for vacancy in sj_vacancies_page
        ]
    return predict_average_salary(vacancies_predicted_rub_salary)


if __name__ == "__main__":
    load_dotenv()
    superjob_api_key = os.getenv("SUPERJOB_API_KEY")
    programming_languages = [
        "TypeScript", "Swift", ##"Scala", "Objective-C", "Shell", "JavaScript",
        # "Go", "C", "C#", "C++", "PHP", "Ruby", "Python", "Java",
    ]
    average_rub_salary_by_languages_hh = {}
    average_rub_salary_by_languages_sj = {}
    for programming_language in programming_languages:
        language_vacancies_generator_hh = get_actual_programming_vacancies_moscow_hh(
            programming_language, "Api-test-agent")
        language_vacancies_generator_superjob = get_actual_programming_vacancies_moscow_sj(
            programming_language, superjob_api_key
        )
        try:
            average_rub_salary_by_language_hh = predict_average_rub_salary_hh(language_vacancies_generator_hh)
            average_rub_salary_by_languages_hh[programming_language] = average_rub_salary_by_language_hh

            average_rub_salary_by_language_sj = predict_average_rub_salary_sj(language_vacancies_generator_superjob)
            average_rub_salary_by_languages_sj[programming_language] = average_rub_salary_by_language_sj
        except Exception:
            print("Ойойойойойойо!")
            exit()
    pprint(average_rub_salary_by_languages_hh)
    pprint(average_rub_salary_by_languages_sj)
