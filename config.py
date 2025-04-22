import os
from configparser import ConfigParser

ROOT_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(ROOT_DIR, "data")


def config(filename: str ="database.ini", section: str ="postgresql")-> dict[str, str]:
    """ Чтение параметров для подключения к БД из файла database.ini"""
    try:
        parser = ConfigParser()
        parser.read(os.path.join(ROOT_DIR, filename))
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception(
                'Section {0} is not found in the {1} file.'.format(section, filename))
        return db
    except Exception as e:
        print(f"Ошибка получения параметра для подключения к БД: {e}")
        return {}


if __name__ == "__main__":
    print(ROOT_DIR)
    print(DATA_DIR)
    print(config())
