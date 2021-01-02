from dotenv import load_dotenv
from terminaltables import AsciiTable
from itertools import count
from math import ceil
import os
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


def print_vacancies_download_progress(
        job_search_service,
        page_number,
        total_pages,
        vacancy_keyword="all",
):
    print(
        f"{job_search_service} {vacancy_keyword} vacancies: {page_number} from {total_pages} pages downloaded."
    )


def get_filtered_vacancies_generator_hh(user_agent_name, filtering_options=None, reporthook=None):
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
        if reporthook:
            reporthook(
                job_search_service="hh.ru",
                vacancy_keyword=filtering_options["text"],
                page_number=vacancies_page_hh["page"] + 1,
                total_pages=total_pages,
            )

        yield vacancies_page_hh["items"]


def get_monthly_moscow_vacancies_generator_hh(user_agent_name, search_text="", reporthook=None):
    return get_filtered_vacancies_generator_hh(
        user_agent_name,
        filtering_options={
            "specialization": "1.221",      # Programming specialization id
            "area": 1,                      # Moscow id
            "period": 30,                   # days
            "text": search_text,            # text to search in vacancies
        },
        reporthook=reporthook,
    )


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


def get_filtered_vacancies_generator_sj(authorization_key, filtering_options=None, reporthook=None):
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
        vacancies_page_sj = get_filtered_vacancies_page_sj(authorization_key, filtering_options)
        if reporthook:
            vacancies_per_page = filtering_options["count"]
            total_vacancies_quantity = vacancies_page_sj["total"]
            total_pages_quantity = ceil(total_vacancies_quantity / vacancies_per_page)
            reporthook(
                job_search_service="SuperJob.ru",
                vacancy_keyword=filtering_options["keyword"],
                page_number=page_index + 1,
                total_pages=total_pages_quantity,
            )
        is_more_pages = vacancies_page_sj["more"]
        yield vacancies_page_sj["objects"]


def get_monthly_moscow_vacancies_generator_sj(search_text, authorization_key, reporthook=None):
    language_vacancies_superjob = get_filtered_vacancies_generator_sj(
        authorization_key,
        filtering_options={
            "town": 4,               # Moscow id
            "catalogues": 48,        # Programming specialization id
            "keyword": search_text,  # text to search in vacancies
        },
        reporthook=reporthook,
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


def predict_rub_salary_for_headhunter(vacancy_hh):
    vacancy_salary = vacancy_hh["salary"]
    if not vacancy_salary or vacancy_salary["currency"] != "RUR":
        return None
    return predict_salary(vacancy_salary["from"], vacancy_salary["to"])


def predict_rub_salary_for_superjob(vacancy_sj):
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


def predict_average_rub_salary_hh(hh_vacancies_generator):
    vacancies_predicted_rub_salary = []
    for hh_vacancies_page in hh_vacancies_generator:
        vacancies_predicted_rub_salary += [
            predict_rub_salary_for_headhunter(vacancy) for vacancy in hh_vacancies_page
        ]
    return predict_average_salary(vacancies_predicted_rub_salary)


def predict_average_rub_salary_sj(sj_vacancies_generator):
    vacancies_predicted_rub_salary = []
    for sj_vacancies_page in sj_vacancies_generator:
        vacancies_predicted_rub_salary += [
            predict_rub_salary_for_superjob(vacancy) for vacancy in sj_vacancies_page
        ]
    return predict_average_salary(vacancies_predicted_rub_salary)


def prepare_average_salary_for_table_print(vacancies_average_salary):
    column_headers = [
        "Язык программирования",
        "Вакансий найдено",
        "Вакансий обработано",
        "Средняя зарплата",
    ]
    vacancies_average_salary_list = [column_headers]
    for programming_language, average_salary in vacancies_average_salary.items():
        table_row = [
            programming_language,
            average_salary["vacancies_found"],
            average_salary["vacancies_processed"],
            average_salary["average_salary"],
        ]
        vacancies_average_salary_list.append(table_row)
    return vacancies_average_salary_list


def print_vacancies_average_salary_table(vacancies_average_salary, table_title=""):
    average_salary_list = prepare_average_salary_for_table_print(vacancies_average_salary)
    average_salary_table_instanse = AsciiTable(
        average_salary_list,
        title=table_title,
    )
    print(average_salary_table_instanse.table)


programming_languages = [
        "TypeScript", "Swift", "Scala", "Objective-C", "Shell", "JavaScript",
        "Go", "C", "C#", "C++", "PHP", "Ruby", "Python", "Java",
    ]

if __name__ == "__main__":
    load_dotenv()
    superjob_api_key = os.getenv("SUPERJOB_API_KEY")
    average_salary_by_languages_rub_hh = {}
    average_salary_by_languages_rub_sj = {}
    for programming_language in programming_languages:
        language_vacancies_generator_hh = get_monthly_moscow_vacancies_generator_hh(
            user_agent_name="Api-test-agent",
            search_text=programming_language,
            reporthook=print_vacancies_download_progress,
        )
        language_vacancies_generator_superjob = get_monthly_moscow_vacancies_generator_sj(
            search_text=programming_language,
            authorization_key=superjob_api_key,
            reporthook=print_vacancies_download_progress,
        )
        try:
            average_language_salary_rub_hh = predict_average_rub_salary_hh(language_vacancies_generator_hh)
            average_salary_by_languages_rub_hh[programming_language] = average_language_salary_rub_hh
            average_language_salary_rub_sj = predict_average_rub_salary_sj(language_vacancies_generator_superjob)
            average_salary_by_languages_rub_sj[programming_language] = average_language_salary_rub_sj
        except requests.exceptions.ConnectionError:
            print("Ошибка соединения.")
            exit()
        except requests.exceptions.HTTPError as http_error:
            print(http_error)
            exit()
Доб    print("\n")
    print_vacancies_average_salary_table(average_salary_by_languages_rub_hh, "Head Hunter")
    print("\n")
    print_vacancies_average_salary_table(average_salary_by_languages_rub_sj, "Super Job")
