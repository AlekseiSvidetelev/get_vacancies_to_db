from src.hh_api import get_employer_vacancies_hh
from src.utils import create_database, create_table_database, clean_split_str, entry_employer_to_database, \
    get_list_employers, parser_and_sorted_employers, parse_vacancies, entry_vacancies_to_database, \
    record_vacancies_in_database


def user_interaction() -> None:
    """ Функция для взаимодействия с пользователем """
    try:
        print("Привет!")
        platforms = ["HeadHunter"]
        create_database() # Создание БД
        create_table_database() # Создание таблиц в БД
        search_query = input(f"Введите название компаний для поиска {platforms}: ")
        search_word_list = clean_split_str(search_query) # Преобразование поискового запроса от пользователя
        print("Выполняется поиск. Ждите...")
        get_employers = get_list_employers(search_word_list)  # Получение вакансий через API запрос
        sorted_employers = parser_and_sorted_employers(get_employers) # Фильтрация работодателей по открытым вакансиям и вывод 10
        entry_employer_to_database(sorted_employers) # Запись работодателей в БД

        # Получение вакансий по ID работодателя и запись в БД
        record_vacancies_in_database(sorted_employers)

        print("Данные успешно получены")










    except Exception as e:
        print(f"Ошибка работы программы: {e}")


if __name__ == '__main__':
    user_interaction()

