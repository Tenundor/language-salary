from utils import predict_salary, predict_average_salary
from itertools import count
import requests


def get_filtered_vacancies_generator_hh(
        user_agent_name,
        specialization="",
        area="",
        period="",
        search_text="",
):
    hh_api_url = "https://api.hh.ru/vacancies"
    total_pages = 0
    for vacancies_page_index in count():
        if total_pages and vacancies_page_index >= total_pages:
            break
        vacancies_page_response = requests.get(
            hh_api_url,
            params={
                "specialization": specialization,
                "area": area,
                "period": period,
                "text": search_text,
                "page": vacancies_page_index,
            },
            headers={"User-Agent": user_agent_name},
        )
        vacancies_page_response.raise_for_status()
        vacancies_page_hh = vacancies_page_response.json()
        total_pages = vacancies_page_hh["pages"]

        yield vacancies_page_hh["items"]


def get_monthly_moscow_vacancies_generator_hh(user_agent_name, search_text=""):
    moscow_id = "1"
    programming_specialization_id = "1.221"
    search_period_days = "30"

    return get_filtered_vacancies_generator_hh(
        user_agent_name,
        specialization=programming_specialization_id,
        area=moscow_id,
        period=search_period_days,
        search_text=search_text,
    )


def predict_rub_salary_for_headhunter(vacancy_hh):
    vacancy_salary = vacancy_hh["salary"]
    if not vacancy_salary or vacancy_salary["currency"] != "RUR":
        return None
    return predict_salary(vacancy_salary["from"], vacancy_salary["to"])


def predict_average_rub_salary_hh(hh_vacancies_generator):
    vacancies_predicted_rub_salary = []
    for hh_vacancies_page in hh_vacancies_generator:
        vacancies_predicted_rub_salary.extend([
            predict_rub_salary_for_headhunter(vacancy) for vacancy in hh_vacancies_page
        ])
    return predict_average_salary(vacancies_predicted_rub_salary)



