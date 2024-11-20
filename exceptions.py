# exceptions.py

class ApiServiceError(Exception):
    """Что-то пошло не так с API"""
    pass

class KeyCreationError(ApiServiceError):
    """Ошибка API: не удалось создать ключ"""
    pass

class KeyRenamingError(ApiServiceError):
    """Ошибка API: не удалось переименовать созданный ключ"""
    pass

class InvalidServerIdError(Exception):
    """ID сервера не существует"""
    pass

# Добавлены новые исключения:
class NetworkError(Exception):
    """Ошибка сети при обращении к серверу"""
    pass

class AuthorizationError(Exception):
    """Ошибка авторизации при доступе к серверу"""
    pass
