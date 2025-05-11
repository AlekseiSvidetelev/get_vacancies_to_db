from typing import Any

import psycopg2

from config import config
from src.hh_api import get_employer_vacancies_hh
from src.utils import parse_vacancies


def create_database() -> None:
    """Создание базы данных"""
    params:dict[str, Any] = config()
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
    params:dict[str, Any] = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {employers_table}
            (employer_id INTEGER PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            url VARCHAR(255))
        """
        )

        cur.execute(
            f"""
                CREATE TABLE IF NOT EXISTS {vacancies_table}(
                vacancy_id INTEGER PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                salary_from INTEGER,
                salary_to INTEGER,
                requirement VARCHAR(255),
                employer_id INTEGER REFERENCES {employers_table}(employer_id) ON DELETE CASCADE,
                url VARCHAR(255))
            """
        )
        conn.commit()
    except Exception as e:
        print(f"Ошибка при создании таблиц в БД: {e}")
    finally:
        cur.close()
        conn.close()


def entry_employer_to_database(list_employers: list[dict[str, Any]], table_name: str = "employers") -> None:
    """Заполнение данных о работодателе в таблицу"""
    params:dict[str, Any] = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    try:
        for employer in list_employers:
            cur.execute(f"SELECT employer_id FROM {table_name} WHERE employer_id = {int(employer['id'])}")
            result = cur.fetchall()
            if len(result) == 0:
                cur.execute(
                    f"INSERT INTO {table_name}(employer_id, name, url) VALUES (%s, %s, %s)",
                    (int(employer["id"]), employer["name"], employer["url"]),
                )
            else:
                continue
        conn.commit()
    except Exception as e:
        print(f"Ошибка добавления данных в таблицу: {e}")
    finally:
        cur.close()
        conn.close()


def entry_vacancies_to_database(vacancy: dict[str, Any], table_name: str = "vacancies") -> None:
    """Запись вакансий в БД"""
    params:dict[str, Any] = config()
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
                (
                    int(vacancy["id"]),
                    vacancy["title"],
                    vacancy["salary_from"],
                    vacancy["salary_to"],
                    vacancy["requirement"],
                    int(vacancy["employer_id"]),
                    vacancy["url"],
                ),
            )
        conn.commit()
    except Exception as e:
        print(f"Ошибка добавления данных в таблицу: {e}")
    finally:
        cur.close()
        conn.close()


def record_vacancies_in_database(employers_list: list[dict[str, Any]]) -> None:
    """Получение вакансий по ID работодателя и запись в БД"""
    try:
        for employer in employers_list:
            vacancies = get_employer_vacancies_hh(employer["id"])
            for vacancy in vacancies:
                normalize_vacancy = parse_vacancies(vacancy)
                entry_vacancies_to_database(normalize_vacancy)
    except Exception as e:
        print(f"Ошибка получения записи вакансий в БД: {e}")


if __name__ == "__main__":
    res = get_employer_vacancies_hh(1740)
    for employer in res:
        print(parse_vacancies(employer))
    entry_vacancies_to_database(
        {
            "id": "119810244",
            "title": "Менеджер проектов",
            "salary_from": None,
            "salary_to": None,
            "url": "https://hh.ru/vacancy/119810244",
            "employer_id": "1740",
            "requirement": """Умеете работать с большим количеством данных. Уверенно владеете Microsoft Excel.
            Эффективно работаете при многозадачности, способны вести несколько проектов одновременно и...""",
        }
    )
