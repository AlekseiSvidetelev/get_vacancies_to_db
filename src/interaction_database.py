import os
from configparser import ConfigParser
from typing import Any, Optional

import psycopg2

from config import ROOT_DIR
from src.utils import clean_split_str


class DBManager:
    """Класс для работы с работодателем и вакансиями из БД"""

    config_file: str
    section: str
    table_name_for_employers: str
    table_name_for_vacancies: str

    def __init__(
        self,
        config_file: Optional[str] = None,
        section: Optional[str] = None,
        table_name_for_employers: Optional[str] = None,
        table_name_for_vacancies: Optional[str] = None,
    ) -> None:
        """Инициализация подключения к базе данных"""
        self.__config_file = config_file if config_file is not None else "database.ini"
        self.__section = section if section is not None else "postgresql"
        self.__employers = table_name_for_employers if table_name_for_employers is not None else "employers"
        self.__vacancies = table_name_for_vacancies if table_name_for_vacancies is not None else "vacancies"

    @staticmethod
    def _get_config(file_name: str, section: str) -> dict[str, Any]:
        try:
            parser = ConfigParser()
            parser.read(os.path.join(ROOT_DIR, file_name))
            db = {}
            if parser.has_section(section):
                params = parser.items(section)
                for param in params:
                    db[param[0]] = param[1]
            else:
                raise Exception("Section {0} is not found in the {1} file.".format(section, file_name))
            return db
        except Exception as e:
            print(f"Ошибка получения параметра для подключения к БД: {e}")
            return {}

    def _request_database(self, query: str, params: Optional[Any]=None) -> Any:
        """Метод выполнения запросов"""
        try:

            config = self._get_config(self.__config_file, self.__section)
            with psycopg2.connect(**config) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params if params else None)
                    return cur.fetchall()
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return []

    def get_companies_and_vacancies_count(self) -> Any:
        """Получает список всех компаний и количество вакансий у каждой компании."""
        try:
            request_sql = f"""
                    SELECT {self.__employers}.name AS company, COUNT({self.__vacancies}.vacancy_id) AS vacancies_count
                    FROM {self.__employers}
                    LEFT JOIN {self.__vacancies} ON {self.__employers}.employer_id = {self.__vacancies}.employer_id
                    GROUP BY {self.__employers}.name ORDER BY vacancies_count DESC
                """
            result = self._request_database(request_sql)
            return result
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            return []

    def get_all_vacancies(self) -> Any:
        """Получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию."""
        try:
            request_sql = f"""
                    SELECT {self.__employers}.name AS company_name, {self.__vacancies}.title AS vacancy_title,
                    {self.__vacancies}.salary_from, {self.__vacancies}.salary_to, {self.__vacancies}.url AS vacancy_url
                    FROM {self.__vacancies}
                    INNER JOIN {self.__employers} ON {self.__vacancies}.employer_id = {self.__employers}.employer_id
                """
            result = self._request_database(request_sql)
            return result
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            return []

    def get_avg_salary(self) -> float:
        """Получает среднюю зарплату по вакансиям."""
        try:
            request_sql = f"""
                        SELECT AVG(({self.__vacancies}.salary_from + {self.__vacancies}.salary_to) / 2)
                        FROM {self.__vacancies}
                        WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL
                    """
            result = self._request_database(request_sql)
            return round(float(result[0][0]),2) if result else 0.0
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            return 0.0

    def get_vacancies_with_higher_salary(self) -> Any:
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям."""
        try:
            avg_salary = self.get_avg_salary()
            request_sql = f"""
                    SELECT {self.__employers}.name, {self.__vacancies}.title, {self.__vacancies}.salary_from,
                            {self.__vacancies}.salary_to, {self.__vacancies}.url
                    FROM {self.__vacancies}
                    JOIN {self.__employers} ON {self.__vacancies}.employer_id = {self.__employers}.employer_id
                    WHERE (({self.__vacancies}.salary_from + {self.__vacancies}.salary_to) / 2) > %s
                    ORDER BY ({self.__vacancies}.salary_from + {self.__vacancies}.salary_to) / 2 DESC;
                """
            result = self._request_database(request_sql, (avg_salary,))
            return result
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            return []

    def get_vacancies_with_keyword(self, search_str: str)  -> list[tuple[Any, ...]]:
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова"""
        try:
            word_list = clean_split_str(search_str)
            search_vacancy = []
            for word in word_list:
                search_pattern:str = f"%{word}%"
                request_sql = f"""
                        SELECT {self.__employers}.name, {self.__vacancies}.title, {self.__vacancies}.salary_from,
                        {self.__vacancies}.salary_to, {self.__vacancies}.url
                        FROM {self.__vacancies}
                        JOIN {self.__employers} ON {self.__vacancies}.employer_id = {self.__employers}.employer_id
                        WHERE {self.__vacancies}.title ILIKE %s
                    """
                result = self._request_database(request_sql, (search_pattern, ))
                search_vacancy.extend(result)
            return search_vacancy
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            return []


if __name__ == "__main__":
    res = DBManager()
    print(res.get_companies_and_vacancies_count())
    print(res.get_all_vacancies())
    print(res.get_avg_salary())
    print(res.get_vacancies_with_higher_salary())
    print(res.get_vacancies_with_keyword("Qa, инженер"))
