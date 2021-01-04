from terminaltables import AsciiTable


def predict_salary(salary_from, salary_to):
    if not salary_from and not salary_to:
        return None
    if not salary_from:
        return int(salary_to * 0.8)
    if not salary_to:
        return int(salary_from * 1.2)
    else:
        return int((salary_from + salary_to) / 2)


def predict_average_salary(vacancies_predicted_salary):
    vacancies_quantity = len(vacancies_predicted_salary)
    processed_vacancies_salary = list(
        filter(lambda salary: type(salary) is int, vacancies_predicted_salary)
    )
    processed_vacancies_quantity = len(processed_vacancies_salary)
    if processed_vacancies_quantity:
        average_salary = int(
            sum(processed_vacancies_salary) / processed_vacancies_quantity
        )
    else:
        average_salary = None
    return {
        "vacancies_found": vacancies_quantity,
        "vacancies_processed": processed_vacancies_quantity,
        "average_salary": average_salary,
    }


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


def print_vacancies_average_salary_table(
        vacancies_average_salary,
        table_title="",
):
    average_salary_list = prepare_average_salary_for_table_print(
        vacancies_average_salary
    )
    average_salary_table_instance = AsciiTable(
        average_salary_list,
        title=table_title,
    )
    print(average_salary_table_instance.table)

