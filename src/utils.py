import re
from typing import Any

import psycopg2
from src.hh_api import get_employer_vacancies_hh, get_employers_hh

from config import config


def create_database() -> None:
    """Создание базы данных"""
    params = config()
    conn = psycopg2.connect(
        host=params.get("host"), user=params.get("user"), password=params.get("password"), port=params.get("port")
    )
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    try:
        cur.execute(f"CREATE DATABASE {params.get("database")}")
    except psycopg2.errors.DuplicateDatabase:
        pass
    except Exception as e:
        print(Exception, e)
    finally:
        cur.close()
        conn.close()


def create_table_database(employers_table: str = "employers", vacancies_table: str = "vacancies") -> None:
    """Функция для автоматического создания таблиц БД"""
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    try:
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS {employers_table} "
            f"(employer_id INTEGER PRIMARY KEY, "
            f"name VARCHAR(255) NOT NULL, "
            f"url VARCHAR(255))"
        )

        cur.execute(
            f"CREATE TABLE IF NOT EXISTS {vacancies_table} ("
            f"vacancy_id INTEGER PRIMARY KEY, "
            f"title VARCHAR(255) NOT NULL, "
            f"salary_from INTEGER, "
            f"salary_to INTEGER, "
            f"requirement VARCHAR(255), "
            f"employer_id INTEGER REFERENCES {employers_table}(employer_id) ON DELETE CASCADE, "
            f"url VARCHAR(255)"
            f")"
        )
        conn.commit()
    except Exception as e:
        print(f"Ошибка при создании таблиц в БД: {e}")
    finally:
        cur.close()
        conn.close()


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



def parser_and_sorted_employers(list_employers: list[dict[str, Any]], top_employers:int = 10) -> list[dict[str, Any]]:
    """Получение топ компании с максимальным количеством открытых вакансий"""
    try:
        list_employers.sort(key=lambda x: x['open_vacancies'], reverse=True) # Фильтрация по количеству вакансий
        result = list_employers[:top_employers]
        return result
    except Exception as e:
        print(f"Ошибка получения топ вакансий: {e}")
        return []


def entry_employer_to_database(list_employers: list[dict[str, Any]], table_name:str = "employers")->None:
    """Заполнение данных о работодателе в таблицу"""
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    try:
        for employer in list_employers:
            cur.execute(f"SELECT employer_id FROM {table_name} WHERE employer_id = {int(employer['id'])}")
            result = cur.fetchall()
            if len(result) == 0:
                cur.execute(
                    f"INSERT INTO {table_name}(employer_id, name, url) VALUES (%s, %s, %s)",
                    (int(employer['id']), employer['name'], employer['url'])
                )
            else:
                continue
        conn.commit()
    except Exception as e:
        print(f"Ошибка добавления данных в таблицу: {e}")
    finally:
        cur.close()
        conn.close()


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


def get_list_vacancy(vacancy_id):
    pass


def parse_vacancies(vacancy_data: dict[str, Any]) -> dict[str,Any]:
    """ Извлекает из ответа api нужную информацию о вакансиях """
    try:
        salary = vacancy_data.get("salary")
        update_vacancy_data = {
            "id": vacancy_data.get("id"),
            "title": vacancy_data.get("name"),
            "salary_from": salary.get("from") if salary else None,
            "salary_to": salary.get("to") if salary else None,
            "url": vacancy_data.get("alternate_url"),
            "employer_id": vacancy_data.get("employer", {}).get("id"),
            "requirement": vacancy_data.get("snippet",{}).get("requirement")
        }
        return update_vacancy_data
    except Exception as e:
        print(f"Ошибка преобразования списка вакансий: {e}")
        return {}


def entry_vacancies_to_database(vacancy: dict[str, Any], table_name:str = "vacancies")->None:
    """ Запись вакансий в БД """
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT vacancy_id FROM {table_name} WHERE vacancy_id = {int(vacancy['id'])}")
        result = cur.fetchall()
        if len(result) == 0:
            cur.execute(
                f"INSERT INTO {table_name}"
                f"(vacancy_id, title, salary_from, salary_to, requirement, employer_id, url)"
                f" VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (int(vacancy['id']), vacancy['title'],
                 vacancy['salary_from'], vacancy['salary_to'],
                 vacancy['requirement'], int(vacancy['employer_id']), vacancy['url'])
            )
        conn.commit()
    except Exception as e:
        print(f"Ошибка добавления данных в таблицу: {e}")
    finally:
        cur.close()
        conn.close()


def record_vacancies_in_database(employers_list: list[dict[str, Any]])-> None:
    """ Получение вакансий по ID работодателя и запись в БД """
    try:
        for employer in employers_list:
            vacancies = get_employer_vacancies_hh(employer["id"])
            for vacancy in vacancies:
                normalize_vacancy = parse_vacancies(vacancy)
                entry_vacancies_to_database(normalize_vacancy)
    except Exception as e:
        print(f"Ошибка получения записи вакансий в БД: {e}")




if __name__ == "__main__":
    # create_database()
    # create_table_database()
    # print(filling_employer_data_db(["Яндекс", "Сбер", "VK Group", "Газпром нефть", "Mail.Ru Group", "Роснефть", "X5 Retail Group", "Ростелеком", "МТС", "Северсталь"]))
    # print(res)
    print(parser_and_sorted_employers(get_list_employers(clean_split_str("Яндекс, Сбер, VK Group, Газпром нефть, Mail.Ru Group, Роснефть, X5 Retail Group, Ростелеком, МТС, Северсталь"))))

    res = get_employer_vacancies_hh('1740')
    for employer in res:
        print(parse_vacancies(employer))
    # entry_vacancies_to_database({'id': '119810244', 'title': 'Менеджер проектов', 'salary_from': None, 'salary_to': None, 'url': 'https://hh.ru/vacancy/119810244', 'employer_id': '1740', 'requirement': 'Умеете работать с большим количеством данных. Уверенно владеете Microsoft Excel. Эффективно работаете при многозадачности, способны вести несколько проектов одновременно и...'})

