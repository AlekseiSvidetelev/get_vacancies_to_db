from src.utils import create_database, create_table_database, clean_split_str, filling_employer_data_db


def user_interaction() -> None:
    """ Функция для взаимодействия с пользователем """
    try:
        print("Привет!")
        platforms = ["HeadHunter"]
        create_database() # Создание БД
        create_table_database() # Создание таблиц
        search_query = input(f"Введите название компаний для поиска {platforms}: ")
        print("Выполняется поиск. Ждите...")
        search_word_list = clean_split_str(search_query)
        filling_employer_data_db(search_word_list)



    except Exception as e:
        print(f"Ошибка работы программы: {e}")


if __name__ == '__main__':
    user_interaction()

