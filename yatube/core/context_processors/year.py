import datetime as dt


def year(request):
    """Добавляет переменную с текущим годом."""
    return {'year': dt.date.today().year}
# В шаблоне footer исправил на {% now "Y" %}, как бы вроде этот
# файл больше не нужен, но удалив его тесты не проходят, просят этот файл
