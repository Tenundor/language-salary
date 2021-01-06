import requests
from itertools import count
from utils import predict_salary, predict_average_salary


def get_filtered_vacancies_generator_sj(
        authorization_key,
        town="",
        catalogues="",
        keyword="",
):
    superjob_api_url = "https://api.superjob.ru/2.0/vacancies"
    superjob_authorisation_header = {"X-Api-App-ID": authorization_key}
    is_more_pages = True
    for page_index in count():
        if not is_more_pages:
            break
        superjob_page_response = requests.get(
            superjob_api_url,
            params={
                "town": town,
                "catalogues": catalogues,
                "keyword": keyword,
                "page": page_index,
            },
            headers=superjob_authorisation_header,
        )
        superjob_page_response.raise_for_status()
        vacancies_page_sj = superjob_page_response.json()
        is_more_pages = vacancies_page_sj["more"]
        yield vacancies_page_sj["objects"]


def get_monthly_moscow_vacancies_generator_sj(search_text, authorization_key):
    moscow_id = "4"
    programming_specialization_id = "48"
    language_vacancies_superjob = get_filtered_vacancies_generator_sj(
        authorization_key,
        town=moscow_id,
        catalogues=programming_specialization_id,
        keyword=search_text,
    )
    return language_vacancies_superjob


def predict_rub_salary_for_superjob(vacancy_sj):
    if vacancy_sj["currency"] != "rub":
        return None
    return predict_salary(vacancy_sj["payment_from"], vacancy_sj["payment_to"])


def predict_average_rub_salary_sj(sj_vacancies_generator):
    vacancies_predicted_rub_salary = []
    for sj_vacancies_page in sj_vacancies_generator:
        vacancies_predicted_rub_salary.extend([
            predict_rub_salary_for_superjob(vacancy) for vacancy in sj_vacancies_page
        ])
    return predict_average_salary(vacancies_predicted_rub_salary)

