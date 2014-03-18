def main(j,jp):
   
    #configure the application to no longer autostart
    
    jp.log("remove autostart $(jp.name)")
    jp.kill()
    j.tools.startupmanager.removeProcess(jp.name)


