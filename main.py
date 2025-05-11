from src.database_updater import (
    create_database,
    create_table_database,
    entry_employer_to_database,
    record_vacancies_in_database,
)
from src.interaction_database import DBManager
from src.utils import (
    clean_split_str,
    format_count_vacancies_user_output,
    format_vacancies_info_user_output,
    get_list_employers,
    parser_and_sorted_employers,
    update_input_str,
)


def user_interaction() -> None:
    """Функция для взаимодействия с пользователем"""
    try:
        print("Привет!")
        platforms = ["HeadHunter"]
        create_database()  # Создание БД
        create_table_database()  # Создание таблиц в БД
        search_query = input(f"Введите название компаний для поиска {platforms}: ")
        search_word_list = clean_split_str(search_query)  # Преобразование поискового запроса от пользователя
        top_employers = update_input_str(
            input("Отсортировать вакансии по максимальному количеству открытых вакансий(да/нет): ")
        )
        print("Выполняется поиск. Ждите...")
        get_employers = get_list_employers(search_word_list)  # Получение вакансий через API запрос
        if top_employers.lower() == "да":
            sorted_employers = parser_and_sorted_employers(
                get_employers
            )  # Фильтрация работодателей по открытым вакансиям и вывод 10
        else:
            sorted_employers = get_employers[:10]  # Ограничение по условию ДЗ
        entry_employer_to_database(sorted_employers)  # Запись работодателей в БД
        record_vacancies_in_database(sorted_employers)
        # Подключение к классу для работы с БД
        result = DBManager()

        # Получение вакансий по ID работодателя и запись в БД
        print("Найдено вакансий: ")
        format_count_vacancies_user_output(result.get_companies_and_vacancies_count())
        print("Информация о работодателях и вакансиях записана в БД.")

        # Вывод информации по найденным вакансиям
        if update_input_str(input("Вывести найденные вакансии? (да/нет): ")) == "да":
            format_vacancies_info_user_output(result.get_vacancies_with_higher_salary())

            # Вывод средней ЗП по вакансиям
            print(f"Средняя заработная плата по вакансиям: {result.get_avg_salary()}")

        # Вывод вакансий с ЗП выше среднего
        if update_input_str(input("Вывести вакансии с заработной платой выше среднего? (да/нет): ")) == "да":
            print(f"Средняя заработная плата по вакансиям: {result.get_avg_salary()}")
            format_vacancies_info_user_output(result.get_vacancies_with_higher_salary())

        # Фильтрация вакансий по ключевым словам
        if update_input_str(input("Отфильтровать вакансии по ключевым словам? (да/нет)")) == "да":
            search_word = input("Введите ключевые слова для фильтрации вакансий: ")
            format_vacancies_info_user_output(result.get_vacancies_with_keyword(search_word))
        print("END")
    except Exception as e:
        print(f"Ошибка работы программы: {e}")


if __name__ == "__main__":
    user_interaction()
