# mar/18/2014 09:29:12 by RouterOS 6.10
# software id = WLVA-21HW
#

/certificate
remove numbers=[/certificate find ]
import file-name=server.crt passphrase=""
import file-name=server.key passphrase=""
import file-name=ca.crt passphrase=""


