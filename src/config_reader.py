from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
import os

class Settings(BaseSettings):
    # Желательно вместо str использовать SecretStr 
    # для конфиденциальных данных, например, токена бота
    bot_token: SecretStr
    connection_string: SecretStr
    admin_group: SecretStr
    PARTNER_EVENT_ID: SecretStr
    ENVIRONMENT: SecretStr
    GOOGLECREDENTIALS: SecretStr
    GOOGLESHEET: SecretStr

    # Начиная со второй версии pydantic, настройки класса настроек задаются
    # через model_config
    # В данном случае будет использоваться файла .env, который будет прочитан
    # с кодировкой UTF-8
    print(f"ENVIRONMENT file is: .{os.environ['ENVIRONMENT']}.env")
    model_config = SettingsConfigDict(env_file=f".{os.environ['ENVIRONMENT']}.env", env_file_encoding='utf-8', extra="allow")


# При импорте файла сразу создастся 
# и провалидируется объект конфига, 
# который можно далее импортировать из разных мест
config = Settings()