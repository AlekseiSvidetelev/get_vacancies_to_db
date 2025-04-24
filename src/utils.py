import re
from typing import Any

from src.hh_api import get_employer_vacancies_hh, get_employers_hh


def get_list_employers(employer_name_list: list[str]) -> list[dict[str, Any]]:
    """Получение списка работодателей по поисковому запросу"""
    list_vacancies = []
    try:
        for name in employer_name_list:
            result = get_employers_hh(name)
            list_vacancies.extend(result)
        return list_vacancies
    except Exception as e:
        print(f"Ошибка получения работодателей: {e}")
        return []


def parser_and_sorted_employers(list_employers: list[dict[str, Any]], top_employers: int = 10) -> list[dict[str, Any]]:
    """Получение топ компании с максимальным количеством открытых вакансий"""
    try:
        list_employers.sort(key=lambda x: x["open_vacancies"], reverse=True)  # Фильтрация по количеству вакансий
        result = list_employers[:top_employers]
        return result
    except Exception as e:
        print(f"Ошибка получения топ вакансий: {e}")
        return []


def clean_split_str(update_str: str) -> list[str]:
    """Убирает символы из строки и разделяет по пробелу"""
    try:
        if not isinstance(update_str, str):
            raise ValueError("Запрос не является строкой")
        clean_update_str = (re.sub(r"[^\w\s]", "", update_str)).lower()
        word_list = clean_update_str.split()
        return word_list
    except Exception as e:
        print(f"Ошибка преобразования слов фильтрации: {e}")
        return []


def parse_vacancies(vacancy_data: dict[str, Any]) -> dict[str, Any]:
    """Извлекает из ответа api нужную информацию о вакансиях"""
    try:
        salary = vacancy_data.get("salary")
        update_vacancy_data = {
            "id": vacancy_data.get("id"),
            "title": vacancy_data.get("name"),
            "salary_from": salary.get("from") if salary else None,
            "salary_to": salary.get("to") if salary else None,
            "url": vacancy_data.get("alternate_url"),
            "employer_id": vacancy_data.get("employer", {}).get("id"),
            "requirement": vacancy_data.get("snippet", {}).get("requirement"),
        }
        return update_vacancy_data
    except Exception as e:
        print(f"Ошибка преобразования списка вакансий: {e}")
        return {}


def format_count_vacancies_user_output(data: list[tuple[str, str]]) -> None:
    """Форматирование ответа о количестве вакансий для пользователя БД для пользователя и вывод в терминал"""
    for i in data:
        print(f"Компания: {i[0]}\n" f"Количество вакансий: {i[1]}\n" f"------")


def format_vacancies_info_user_output(data: list[tuple[str, str, str, str, str]]) -> None:
    """Форматирование ответа о вакансии для пользователя и вывод в терминал"""
    for i in data:
        company_name = i[0]
        title = i[1]
        salary_from = i[2] or "не указана"
        salary_to = i[3] or "не указана"
        url = i[4]
        print(
            f"Компания: {company_name}\n"
            f"Вакансия: {title}\n"
            f"Зарплата: {salary_from} - {salary_to}\n"
            f"Ссылка: {url}\n"
            f"-----"
        )


if __name__ == "__main__":
    # res = get_employer_vacancies_hh("1740")
    # for employer in res:
    #     print(parse_vacancies(employer))

    print(clean_split_str(" Да"))
