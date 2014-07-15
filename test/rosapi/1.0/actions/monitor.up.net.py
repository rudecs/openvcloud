def main(j,jp,ipaddr):
   
    #monitor the app if it is performing well, this is for the remote tests

    test=True

    #can use this to test remotely 

    for port in jp.tcpPorts:
        test =test & j.system.net.tcpPortConnectionTest(ipaddr, port)

    #test 2
    ##e.g. an http test

    return test    
