import pxssh
import pexpect
import sys

def installAndRunUnixBench(sshhost, sshusername, sshpassword):
    ssh_newkey = 'Are you sure you want to continue connecting'
    # my ssh command line
    p=pexpect.spawn('ssh %s@%s uname -a' % (sshhost, sshusername))
    i=p.expect([ssh_newkey,'password:',pexpect.EOF])
    if i==0:
        print "Continue connection"
        p.sendline('yes')

    s = pxssh.pxssh()
    if not s.login(sshhost, sshusername, sshpassword):
        print "SSH session failed on login."
        print str(s)
    else:
        print "SSH session login successful"
    #print_file('out2.txt', 'SSH login Successful')
    s.sendline('echo %s | sudo -S apt-get install tmux' % sshpassword)
    s.prompt()
    print s.before
    s.sendline(
        'wget https://byte-unixbench.googlecode.com/files/UnixBench5.1.3.tgz')
    s.prompt()
    print s.before
    s.sendline('tar -xzvf UnixBench5.1.3.tgz')
    s.prompt()
    print s.before
    s.sendline('echo %s | sudo -S apt-get install -y gcc make' %
               sshpassword)
    s.prompt()
    print s.before
    s.sendline('cd UnixBench')
    s.prompt()
    print s.before
    s.sendline('echo %s | sudo -S make' % sshpassword)
    s.prompt()
    print s.before
    s.sendline('tmux new-session -s Test -d "echo %s | sudo -S ./Run >> UnixBench5screen"' % sshpassword)
    s.prompt()
    print s.before
    s.logout()

if __name__ == '__main__':
    try:
        host = sys.argv[1]
        username = sys.argv[2]
        passwd = sys.argv[3]
        installAndRunUnixBench(host, username, passwd)
    except IndexError:
        print 'Usage python benchmarkInstaller.py host username password'
