from utils import predict_salary, predict_average_salary
from itertools import count
import requests


def get_filtered_vacancies_page_hh(user_agent_name, filtering_options):
    hh_api_url = "https://api.hh.ru/vacancies"
    vacancies_page_response = requests.get(
        hh_api_url,
        params=filtering_options,
        headers={"User-Agent": user_agent_name},
    )
    vacancies_page_response.raise_for_status()
    return vacancies_page_response.json()


def get_filtered_vacancies_generator_hh(
        user_agent_name,
        filtering_options=None
):
    if filtering_options is None:
        filtering_options = {}
    else:
        filtering_options = filtering_options.copy()
    total_pages = 0
    for vacancies_page_index in count():
        if total_pages and vacancies_page_index >= total_pages:
            break
        filtering_options["page"] = vacancies_page_index
        vacancies_page_hh = get_filtered_vacancies_page_hh(
            user_agent_name,
            filtering_options,
        )
        total_pages = vacancies_page_hh["pages"]

        yield vacancies_page_hh["items"]


def get_monthly_moscow_vacancies_generator_hh(user_agent_name, search_text=""):
    return get_filtered_vacancies_generator_hh(
        user_agent_name,
        filtering_options={
            "specialization": "1.221",      # Programming specialization id
            "area": 1,                      # Moscow id
            "period": 30,                   # days
            "text": search_text,            # text to search in vacancies
        },
    )


def predict_rub_salary_for_headhunter(vacancy_hh):
    vacancy_salary = vacancy_hh["salary"]
    if not vacancy_salary or vacancy_salary["currency"] != "RUR":
        return None
    return predict_salary(vacancy_salary["from"], vacancy_salary["to"])



def predict_average_rub_salary_hh(hh_vacancies_generator):
    vacancies_predicted_rub_salary = []
    for hh_vacancies_page in hh_vacancies_generator:
        vacancies_predicted_rub_salary += [
            predict_rub_salary_for_headhunter(vacancy) for vacancy in hh_vacancies_page
        ]
    return predict_average_salary(vacancies_predicted_rub_salary)



