import db
from datetime import datetime

class FeatureToggleService:
    #Значение переменной используется для поиска в базе
    exampleFeatureToggle = "exampleFeatureToggle"
    checkCodeInPrivateChatFT = "checkCodeInPrivateChatFT"
    partnerContributeShowInMainMenu = "showPartnerButtonInMainMenu"
    
    def memoize(func):
        cache = {}
        cacheTimeInSeconds = 5 * 60

        def wrapper(*args):
            timestamp = datetime.now()
            if args in cache:
                oldResult = cache[args]
                if ((timestamp - oldResult["timestamp"]).total_seconds()) < cacheTimeInSeconds:
                    return oldResult["result"]
            result = func(*args)
            cache[args] = {"timestamp": timestamp, "result": result}
            return result

        return wrapper

    @memoize
    def getFeatureToggleState(self, ftName) -> bool:
        allft = db.getFeatureToggles()
        ft = next(filter(lambda x: x.name == ftName, list(allft)))
        return ft.enabled

if __name__ == "__main__":
    service = FeatureToggleService()
    service.getFeatureToggleState(service.exampleFeatureToggle)