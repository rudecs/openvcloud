def main(j,jp):
   
    #stop the application (only relevant for server apps)
    
    jp.log("stop $(jp.name)")

    if j.tools.startupmanager.existsJPackage(jp):
        
        j.tools.startupmanager.stopJPackage(jp)

        for port in jp.tcpPorts:
            j.system.process.killProcessByPort(port)

        jp.waitDown(timeout=20)


