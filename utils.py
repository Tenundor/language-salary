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
    processed_salary = list(
        filter(lambda salary: type(salary) is int, vacancies_predicted_salary)
    )
    processed_vacancies_quantity = len(processed_salary)
    if processed_vacancies_quantity:
        average_salary = int(
            sum(processed_salary) / processed_vacancies_quantity
        )
    else:
        average_salary = None
    return {
        "vacancies_found": vacancies_quantity,
        "vacancies_processed": processed_vacancies_quantity,
        "average_salary": average_salary,
    }
