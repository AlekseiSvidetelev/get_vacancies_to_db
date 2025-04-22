import json
import os
from typing import Any

import requests

from config import DATA_DIR


def get_employers(search_text, max_employers=10):
    """Получение вакансий по поисковому запросу"""
    url = "https://api.hh.ru/employers"
    params = {"text": search_text, "per_page": max_employers}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        employers = []
        for item in data.get("items", []):
            employer = {
                "id": item.get("id"),
                "name": item.get("name"),
                "url": item.get("alternate_url"),
                "open_vacancies": item.get("open_vacancies", 0),
            }
            employers.append(employer)
        return employers
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе: {e}")
        return []


def get_employer_vacancies(employer_id: int) -> list[dict[str, Any]]:
    """Получение вакансий по ID работодателя"""
    url = "https://api.hh.ru/vacancies"
    params = {"employer_id": employer_id, "per_page": 100, "page": 0}
    vacancies = []
    try:
        while True:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            vacancies.extend(data.get("items", []))
            if params["page"] >= data.get("pages", 0) - 1:
                break
            params["page"] += 1
    except Exception as e:
        print(f"Ошибка при получении вакансий компании {employer_id}: {e}")
    with open(os.path.join(DATA_DIR, "vacancies.json"), "w", encoding="utf-8") as f:
        json.dump(vacancies, f, ensure_ascii=False, indent=4)
    return vacancies


if __name__ == "__main__":
    print(get_employers("яндекс"))
    # print(get_employer_vacancies("1740"))
