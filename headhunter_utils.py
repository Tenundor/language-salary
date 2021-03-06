from itertools import count

import requests

from utils import predict_salary, predict_average_salary


def get_filtered_vacancies_hh(
        user_agent_name,
        specialization="",
        area="",
        period="",
        search_text=""):
    api_url = "https://api.hh.ru/vacancies"
    total_pages = 0
    for page_index in count():
        if total_pages and page_index >= total_pages:
            break
        response = requests.get(
            api_url,
            params={
                "specialization": specialization,
                "area": area,
                "period": period,
                "text": search_text,
                "page": page_index,
            },
            headers={"User-Agent": user_agent_name},
        )
        response.raise_for_status()
        vacancies_page_hh = response.json()
        total_pages = vacancies_page_hh["pages"]

        yield vacancies_page_hh["items"]


def get_monthly_moscow_vacancies_hh(user_agent_name, search_text=""):
    moscow_id = "1"
    programming_specialization_id = "1.221"
    search_period_days = "30"

    return get_filtered_vacancies_hh(
        user_agent_name,
        specialization=programming_specialization_id,
        area=moscow_id,
        period=search_period_days,
        search_text=search_text,
    )


def predict_rub_salary_for_headhunter(vacancy):
    vacancy_salary = vacancy["salary"]
    if vacancy_salary and vacancy_salary["currency"] == "RUR":
        return predict_salary(vacancy_salary["from"], vacancy_salary["to"])


def predict_average_rub_salary_hh(vacancy_pages):
    predicted_salary = []
    for page in vacancy_pages:
        predicted_salary.extend([
            predict_rub_salary_for_headhunter(vacancy) for vacancy in page
        ])
    return predict_average_salary(predicted_salary)


def collect_average_salary_moscow_hh(programming_languages):
    average_salary_by_languages = {}
    for programming_language in programming_languages:
        language_vacancies = get_monthly_moscow_vacancies_hh(
            user_agent_name="Api-test-agent",
            search_text=programming_language,
        )
        average_salary = predict_average_rub_salary_hh(language_vacancies)
        average_salary_by_languages[programming_language] = average_salary

    return average_salary_by_languages
