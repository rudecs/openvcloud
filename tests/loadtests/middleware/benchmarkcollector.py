import sys
import commands

def collectNixStats(host, username, passwd):
    fabb_conn = 'fab -H %s -u %s -p %s -- cat UnixBench/UnixBench5screen | grep -i "System Benchmarks Index Score" |  grep -o [0-9].*' % (
            host, username, passwd)
    return commands.getoutput(fabb_conn)

if __name__ == "__main__":
    try:
        host = sys.argv[1]
        username = sys.argv[2]
        passwd = sys.argv[3]
        print collectNixStats(host, username, passwd)
    except IndexError:
        print 'Usage python benchmarkInstaller.py host username password'