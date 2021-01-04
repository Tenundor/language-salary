import requests
from itertools import count
from utils import predict_salary, predict_average_salary


def get_filtered_vacancies_page_sj(authorization_key, filtering_options):
    superjob_api_url = "https://api.superjob.ru/2.0/vacancies"
    superjob_authorisation_header = {"X-Api-App-ID": authorization_key}
    superjob_page_response = requests.get(
        superjob_api_url,
        params=filtering_options,
        headers=superjob_authorisation_header,
    )
    superjob_page_response.raise_for_status()
    return superjob_page_response.json()


def get_filtered_vacancies_generator_sj(
        authorization_key,
        filtering_options=None
):
    if filtering_options is None:
        filtering_options = {}
    else:
        filtering_options = filtering_options.copy()
    filtering_options = dict({
        "count": 20  # Default vacancies count per page
    }, **filtering_options)
    is_more_pages = True
    for page_index in count():
        if not is_more_pages:
            break
        filtering_options["page"] = page_index
        vacancies_page_sj = get_filtered_vacancies_page_sj(
            authorization_key,
            filtering_options,
        )
        is_more_pages = vacancies_page_sj["more"]
        yield vacancies_page_sj["objects"]


def get_monthly_moscow_vacancies_generator_sj(search_text, authorization_key):
    language_vacancies_superjob = get_filtered_vacancies_generator_sj(
        authorization_key,
        filtering_options={
            "town": 4,               # Moscow id
            "catalogues": 48,        # Programming specialization id
            "keyword": search_text,  # text to search in vacancies
        },
    )
    return language_vacancies_superjob


def predict_rub_salary_for_superjob(vacancy_sj):
    if vacancy_sj["currency"] != "rub":
        return None
    return predict_salary(vacancy_sj["payment_from"], vacancy_sj["payment_to"])


def predict_average_rub_salary_sj(sj_vacancies_generator):
    vacancies_predicted_rub_salary = []
    for sj_vacancies_page in sj_vacancies_generator:
        vacancies_predicted_rub_salary += [
            predict_rub_salary_for_superjob(vacancy) for vacancy in sj_vacancies_page
        ]
    return predict_average_salary(vacancies_predicted_rub_salary)

