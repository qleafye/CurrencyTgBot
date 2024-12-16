from bestchange_api import BestChange


def get_min_rate(give_id, get_id):
    """
    Функция для получения минимального курса обмена для заданных ID валют.

    :param give_id: ID валюты, которую отдаёте.
    :param get_id: ID валюты, которую получаете.
    :return: Минимальный курс обмена или None, если обменов нет.
    """
    # Инициализация API
    api = BestChange()

    # Получение всех доступных курсов
    rates = api.rates().get()

    # Список для хранения курсов
    rates_list = []

    # Поиск нужного курса
    for rate in rates:
        if rate['give_id'] == give_id and rate['get_id'] == get_id:
            rates_list.append(rate['rate'])

    # Возвращаем минимальный курс, если он найден
    if rates_list:
        return min(rates_list)
    else:
        return None
