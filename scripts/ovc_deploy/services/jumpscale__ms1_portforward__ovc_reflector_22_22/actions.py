from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def configure(self, serviceObj):
        ms1ClientHRD = j.application.getAppInstanceHRD('ms1_client', 'main')
        spacesecret = ms1ClientHRD.getStr('instance.param.secret')

        protocol = serviceObj.hrd.getStr('instance.param.protocol')
        spacePort = serviceObj.hrd.getInt('instance.param.space.port')
        vmName = serviceObj.hrd.getStr('instance.param.vm.name')
        vmPort = serviceObj.hrd.getInt('instance.param.vm.port')

        if protocol.lower() == 'tcp':
            j.tools.ms1.createTcpPortForwardRule(spacesecret, vmName, vmPort, pubipport=spacePort)
        elif protocol.lower() == 'udp':
            j.tools.ms1.createUdpPortForwardRule(spacesecret, vmName, vmPort, pubipport=spacePort)

        return True

    def removedata(self, serviceObj):
        ms1ClientHRD = j.application.getAppInstanceHRD('ms1_client', 'main')
        spacesecret = ms1ClientHRD.getStr('instance.param.secret')

        protocol = serviceObj.hrd.getStr('instance.param.protocol')
        spacePort = serviceObj.hrd.getInt('instance.param.space.port')
        vmName = serviceObj.hrd.getStr('instance.param.vm.name')
        vmPort = serviceObj.hrd.getInt('instance.param.vm.port')

        if protocol.lower() == 'tcp':
            j.tools.ms1.deleteTcpPortForwardRule(spacesecret, vmName, vmPort, pubipport=spacePort)
        elif protocol.lower() == 'udp':
            j.tools.ms1.deleteUdpPortForwardRule(spacesecret, vmName, vmPort, pubipport=spacePort)

        return True
