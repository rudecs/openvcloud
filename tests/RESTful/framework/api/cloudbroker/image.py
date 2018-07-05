import random
from framework.api import  utils

class Image:
    def __init__(self, api_client):
        self._api = api_client

    def delete(self,imageId):
        return self._api.cloudbroker.image.delete(imageId=imageId)
    
    def disable(self,imageId):
        return self._api.cloudbroker.image.disable(imageId=imageId)   
    
    def enable(self,imageId):
        return self._api.cloudbroker.image.enable(imageId=imageId)   

    def updateNodes(self, imageId, enabledStacks):
        return self._api.cloudbroker.image.updateNodes(imageId=imageId, enabledStacks=enabledStacks)   
    
        
    