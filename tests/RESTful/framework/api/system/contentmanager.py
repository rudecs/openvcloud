from framework.api import utils

class ContentManager:
    def __init__(self ,api_client ):
        self._api = api_client

    def checkEvents(self, cursor):
        return self._api.system.contentmanager.checkEvents(cursor=cursor)

    def getActors(self):
        return self._api.system.contentmanager.getActors()

    def getActorsWithPaths(self):
        return self._api.system.contentmanager.getActorsWithPaths()

    def getSpaces(self):
        return self._api.system.contentmanager.getSpaces()

    def getSpacesWithPaths(self):
        return self._api.system.contentmanager.getSpacesWithPaths()

    def modelobjectlist(self, namespace, category, key):
        return self._api.system.contentmanager.modelobjectlist(
            namespace=namespace,
            category=category,
            key=key
        )

    def modelobjectupdate(self, appname, actorname, key):
        return self._api.system.contentmanager.modelobjectupdate(
            appname=appname,
            actorname=actorname,
            key=key
        )

    def notifyActorModification(self, id):
        return self._api.system.contentmanager.notifyActorModification(id=id)

    def notifyActorNew(self, path, name):
        return self._api.system.contentmanager.notifyActorNew(path=path, name=name)

    def notifySpaceNew(self, path, name):
        return self._api.system.contentmanager.notifySpaceNew(path=path, name=name)

    def prepareActorSpecs(self, app, actor):
        return self._api.system.contentmanager.prepareActorSpecs(app=app, actor=actor)

    def wikisave(self, cachekey, text):
        return self._api.system.contentmanager.wikisave(cachekey=cachekey, text=text)

    
    