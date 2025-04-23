from typing import Any

import requests



def get_employers_hh(search_text, max_employers=100):
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


def get_employer_vacancies_hh(employer_id: int, limit_vacancies: int = 20) -> list[dict[str, Any]]:
    """Получение вакансий по ID работодателя"""
    url = "https://api.hh.ru/vacancies"
    params = {"employer_id": employer_id, "per_page": 100, "page": 0}
    vacancies = []
    try:
        while True:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if len(vacancies) > limit_vacancies:
                break
            vacancies.extend(data.get("items", []))
            if params["page"] >= data.get("pages", 0) - 1:
                break
            params["page"] += 1

        return vacancies[:limit_vacancies]
    except Exception as e:
        print(f"Ошибка при получении вакансий компании {employer_id}: {e}")
        return []




if __name__ == "__main__":
    # print(get_employers("яндекс"))
    print(get_employer_vacancies("1740"))
