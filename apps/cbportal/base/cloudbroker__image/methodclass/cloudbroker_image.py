from JumpScale import j
import time, string
from random import choice
from libcloud.compute.base import NodeAuthPassword
import JumpScale.grid.osis
from JumpScale.portal.portal.auth import auth
import urllib,ujson
import urlparse
import JumpScale.baselib.remote.cuisine
import JumpScale.grid.agentcontroller
import JumpScale.lib.whmcs


class cloudbroker_image(j.code.classGetBase()):
    def __init__(self):
        self._te={}
        self.actorname="image"
        self.appname="cloudbroker"
        self.cbcl = j.core.osis.getClientForNamespace('cloudbroker')
        self.libvirtcl = j.core.osis.getClientForNamespace('libvirt')
        self._cb = None
        self.machines_actor = self.cb.extensions.imp.actors.cloudapi.machines
        self.acl = j.clients.agentcontroller.get()

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloudbroker.iaas
        return self._cb

    @auth(['level1',])
    def delete(self, imageId, **kwargs):
        """
        Delete an image
        param:imageId id of image
        result bool
        """
        return True

    @auth(['level1',])
    def enable(self, imageId, **kwargs):
        """
        Enable an image
        param:imageId id of image
        result bool
        """
        return True