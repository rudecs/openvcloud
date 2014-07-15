def main(j,jp):
   
    #monitor the app if it is performing well, return False if not, check if up
    #these are the tests which can only be done local to the system where the app is

    jp.log("check monitoring local for $(jp.name)")
    
    #does tcp as well as pid test
    test=j.tools.startupmanager.getStatus4JPackage(jp)

    return test    
