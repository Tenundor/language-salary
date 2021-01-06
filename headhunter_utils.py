from utils import predict_salary, predict_average_salary
from itertools import count
import requests


def get_filtered_vacancies_hh(
        user_agent_name,
        specialization="",
        area="",
        period="",
        search_text="",
):
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
    if not vacancy_salary or vacancy_salary["currency"] != "RUR":
        return None
    return predict_salary(vacancy_salary["from"], vacancy_salary["to"])


def predict_average_rub_salary_hh(vacancies):
    predicted_salary = []
    for page in vacancies:
        predicted_salary.extend([
            predict_rub_salary_for_headhunter(vacancy) for vacancy in page
        ])
    return predict_average_salary(predicted_salary)
