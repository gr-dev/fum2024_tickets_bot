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
    #TODO: не удается прокинуть переменную в этот класс. КОСТЫЛЬ! ОПАСНО! ИЗБАВИТЬСЯ!
    #Добавил, когда не удавалось нормально управлять миграциями
    if "ENVIRONMENT" in os.environ.keys():
        print(f"ENVIRONMENT file is: .{os.environ['ENVIRONMENT']}.env")
        model_config = SettingsConfigDict(env_file=f".{os.environ['ENVIRONMENT']}.env", env_file_encoding='utf-8', extra="allow")
    else:
        print(f"Warning! Default config is using! .DEBUG.env")
        model_config = SettingsConfigDict(env_file=f".DEBUG.env", env_file_encoding='utf-8', extra="allow")


# При импорте файла сразу создастся 
# и провалидируется объект конфига, 
# который можно далее импортировать из разных мест
config = Settings()