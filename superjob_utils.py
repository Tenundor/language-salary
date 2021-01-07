from itertools import count

import requests

from utils import predict_salary, predict_average_salary


def get_filtered_vacancies_sj(
        authorization_key,
        town="",
        catalogues="",
        keyword=""):
    api_url = "https://api.superjob.ru/2.0/vacancies"
    authorisation_header = {"X-Api-App-ID": authorization_key}
    is_more_pages = True
    for page_index in count():
        if not is_more_pages:
            break
        response = requests.get(
            api_url,
            params={
                "town": town,
                "catalogues": catalogues,
                "keyword": keyword,
                "page": page_index,
            },
            headers=authorisation_header,
        )
        response.raise_for_status()
        vacancies_page = response.json()
        is_more_pages = vacancies_page["more"]
        yield vacancies_page["objects"]


def get_monthly_moscow_vacancies_sj(search_text, authorization_key):
    moscow_id = "4"
    programming_specialization_id = "48"
    return get_filtered_vacancies_sj(
        authorization_key,
        town=moscow_id,
        catalogues=programming_specialization_id,
        keyword=search_text,
    )


def predict_rub_salary_for_superjob(vacancy):
    if vacancy["currency"] != "rub":
        return None
    return predict_salary(vacancy["payment_from"], vacancy["payment_to"])


def predict_average_rub_salary_sj(vacancy_pages):
    predicted_salary = []
    for page in vacancy_pages:
        predicted_salary.extend([
            predict_rub_salary_for_superjob(vacancy) for vacancy in page
        ])
    return predict_average_salary(predicted_salary)
