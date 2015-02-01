from JumpScale import j
from JumpScale import grid
import ujson
cloudbroker = j.clients.osis.getNamespace('cloudbroker')
#this script except user information created on a ceph cluster in the correct
#format.
#The information in the user file should be in the correct order
#And you should change the following infomration:
# * Input file 
# * Start end end of the cloudspaceId range
# * start point of accounts E.g account[i - x]
#
#

f = j.system.fs.fileGetContents('/root/york.0000300-0002000')
accounts = ujson.loads(f)
for i in range(301, 2001):
    account = accounts[i - 301]
    s3u = cloudbroker.s3user.new()
    s3u.location = 'ca1'
    s3u.name = account['user_id']
    s3u.accesskey = account['keys'][0]['access_key']
    s3u.secretkey = account['keys'][0]['secret_key']
    s3u.s3url = 's3-ca1.mothership1.com'
    s3u.cloudspaceId = i
    print 's3u %s %s ' % (s3u.name, s3u.cloudspaceId)
    cloudbroker.s3user.set(s3u)
