import os

from dotenv import load_dotenv
import requests
from terminaltables import AsciiTable

from headhunter_utils import get_monthly_moscow_vacancies_hh
from headhunter_utils import predict_average_rub_salary_hh
from superjob_utils import get_monthly_moscow_vacancies_sj
from superjob_utils import predict_average_rub_salary_sj


def prepare_average_salary_for_table_print(vacancies_average_salary):
    column_headers = [
        "Язык программирования",
        "Вакансий найдено",
        "Вакансий обработано",
        "Средняя зарплата",
    ]
    average_salaries = [column_headers]
    for language, average_salary in vacancies_average_salary.items():
        table_row = [
            language,
            average_salary["vacancies_found"],
            average_salary["vacancies_processed"],
            average_salary["average_salary"],
        ]
        average_salaries.append(table_row)
    return average_salaries


def assemble_vacancies_average_salary_table(
        vacancies_average_salary,
        table_title=""):
    average_salaries = prepare_average_salary_for_table_print(
        vacancies_average_salary
    )
    table_instance = AsciiTable(
        average_salaries,
        title=table_title,
    )
    return table_instance.table


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


def collect_average_salary_moscow_sj(programming_languages):
    load_dotenv()
    api_key = os.getenv("SUPERJOB_API_KEY")
    average_salary_by_languages = {}
    for programming_language in programming_languages:
        language_vacancies = get_monthly_moscow_vacancies_sj(
            search_text=programming_language,
            authorization_key=api_key,
        )
        average_salary = predict_average_rub_salary_sj(language_vacancies)
        average_salary_by_languages[programming_language] = average_salary

    return average_salary_by_languages


def main():
    programming_languages = [
        "TypeScript", "Swift", "Scala", "Objective-C", "Shell", "JavaScript",
        "Go", "C", "C#", "C++", "PHP", "Ruby", "Python", "Java",
    ]
    try:
        average_salary_by_languages_hh = collect_average_salary_moscow_hh(
            programming_languages
        )
        average_salary_by_languages_sj = collect_average_salary_moscow_sj(
            programming_languages
        )
    except requests.exceptions.ConnectionError:
        print("Ошибка соединения.")
        exit()
    except requests.exceptions.HTTPError as http_error:
        print(http_error)
        exit()
    average_salary_table_hh = assemble_vacancies_average_salary_table(
        average_salary_by_languages_hh, "Head Hunter"
    )
    average_salary_table_sj = assemble_vacancies_average_salary_table(
        average_salary_by_languages_sj, "Super Job"
    )
    print(average_salary_table_hh, average_salary_table_sj, sep="\n")


if __name__ == "__main__":
    main()
