from dotenv import load_dotenv
import os
import requests
from headhunter_utils import get_monthly_moscow_vacancies_generator_hh
from headhunter_utils import predict_average_rub_salary_hh
from superjob_utils import get_monthly_moscow_vacancies_generator_sj
from superjob_utils import predict_average_rub_salary_sj
from utils import print_vacancies_average_salary_table


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
        )
        language_vacancies_generator_superjob = get_monthly_moscow_vacancies_generator_sj(
            search_text=programming_language,
            authorization_key=superjob_api_key,
        )
        try:
            average_language_salary_rub_hh = predict_average_rub_salary_hh(
                language_vacancies_generator_hh
            )
            average_salary_by_languages_rub_hh[
                programming_language
            ] = average_language_salary_rub_hh
            average_language_salary_rub_sj = predict_average_rub_salary_sj(
                language_vacancies_generator_superjob
            )
            average_salary_by_languages_rub_sj[
                programming_language
            ] = average_language_salary_rub_sj
        except requests.exceptions.ConnectionError:
            print("Ошибка соединения.")
            exit()
        except requests.exceptions.HTTPError as http_error:
            print(http_error)
            exit()
    print("\n")
    print_vacancies_average_salary_table(
        average_salary_by_languages_rub_hh, "Head Hunter"
    )
    print("\n")
    print_vacancies_average_salary_table(
        average_salary_by_languages_rub_sj, "Super Job"
    )
