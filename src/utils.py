import re
from typing import Any

import psycopg2
from src.hh_api import get_employers

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
            f"employer_id INTEGER REFERENCES {vacancies_table}(employer_id) ON DELETE CASCADE, "
            f"url VARCHAR(255)"
            f")"
        )
        conn.commit()
    except Exception as e:
        print(f"Ошибка при создании таблиц в БД: {e}")
    finally:
        cur.close()
        conn.close()


def get_employers_id(employer_name_list: list[str], top_employers:int = 10) -> list[dict[str, Any]]:
    """Получение топ компании по поисковому списку названий"""
    list_employers = []
    try:
        for name in employer_name_list:
            res = get_employers(name)
            list_employers.extend(res)
        list_employers.sort(key=lambda x: x['open_vacancies'], reverse=True)
        top_employers = list_employers[:top_employers]
        return top_employers
    except Exception as e:
        print(f"Ошибка получения топ вакансий: {e}")
        return []

def filling_employer_data_db(list_search_employers: list[str], table_name:str = "employers")->None:
    """Заполнение данных о работодателе в таблицу"""
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    search_employers = get_employers_id(list_search_employers)
    try:
        for employ in search_employers:
            cur.execute(f"SELECT employer_id FROM {table_name} WHERE employer_id = {int(employ['id'])}")
            result = cur.fetchall()
            if len(result) == 0:
                cur.execute(
                    f"INSERT INTO {table_name}(employer_id, name, url) VALUES (%s, %s, %s)",
                    (int(employ['id']), employ['name'], employ['url'])
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


if __name__ == "__main__":
    # create_database()
    # create_table_database()
    print(filling_employer_data_db(["Яндекс", "Сбер", "VK Group", "Газпром нефть", "Mail.Ru Group", "Роснефть", "X5 Retail Group", "Ростелеком", "МТС", "Северсталь"]))
    # print(clean_split_str("Яндекс Сбер, VK Group, Газпром нефть, Mail.Ru Group, Роснефть, X5 Retail Group, Ростелеком, МТС, Северсталь"))