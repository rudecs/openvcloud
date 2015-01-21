import requests
import hashlib



authenticationparams = dict(

                            username = 'api',

                            password = hashlib.md5('kmmlqwkerjoi324mmkkjhapl02bc').hexdigest(),

                            accesskey = 'mmqewnlzklpo89ka234mkm2o1287kmmzbpldgej3'

                            )



def add_product(ptype, gid, product_id, name, description, pricing_fixed, pricing_variable):



    params = dict(

                  action = 'addproduct',

                  responsetype = 'json',

                  type = ptype,

                  name = name,

                  gid = gid,

                  description = description,

                  paytype = 'recurring')

    params['pricing[1][monthly]'] = pricing_variable

    params.update(authenticationparams)

    response = requests.post('http://whmcsdev/whmcs/includes/api.php',data=params)
    #import ipdb
    #ipdb.set_trace()




if __name__ == '__main__':

    params = {}

    #add_product('server', 1, 'l2', 'Linux Machine 2 GB', 'Linux Machine 2 GB Memory, 2 cores, 10 GB Storage SSD', 0, 20)
    #add_product('server', 1, 'l4', 'Linux Machine 4 GB', 'Linux Machine 4 GB Memory, 2 cores, 10 GB Storage SSD', 0, 36)
    #add_product('server', 1, 'l8', 'Linux Machine 8 GB', 'Linux Machine 8 GB Memory, 4 cores, 10 GB Storage SSD', 0, 64)
    #add_product('server', 1, 'l4d', 'Linux Machine 4 GB', 'Linux Machine 4 GB Memory, 2 cores dedicated, 40 GB Storage SSD', 0, 50)
    #add_product('server', 1, 'l8d', 'Linux Machine 7.5 GB', 'Linux Machine 7.5 GB Memory, 2 cores dedicated, 50 GB Storage SSD', 0, 80)
    #add_product('server', 1, 'l16d', 'Linux Machine 15 GB', 'Linux Machine 15 GB Memory, 4 cores dedicated, 100 GB Storage SSD', 0, 120)
    #add_product('server', 1, 'l30d', 'Linux Machine 30 GB', 'Linux Machine 30 GB Memory, 8 cores dedicated, 200 GB Storage SSD', 0, 220)
    #add_product('server', 1, 'w2', 'Windows Machine 2 GB', 'Linux Machine 2 GB Memory, 2 cores, 10 GB Storage SSD', 0, 20)
    #add_product('server', 1, 'w4', 'Windows Machine 4 GB', 'Linux Machine 4 GB Memory, 2 cores, 10 GB Storage SSD', 0, 36)
    #add_product('server', 1, 'w8', 'Windows Machine 8 GB', 'Linux Machine 8 GB Memory, 4 cores, 10 GB Storage SSD', 0, 64)
    #add_product('server', 1, 'w4d', 'Windows Machine 4 GB, dedicated cores', 'Windows Machine 4 GB Memory, 2 cores dedicated, 40 GB Storage SSD', 0, 50)
    #add_product('server', 1, 'w8d', 'Windows Machine 7.5 GB, dedicated cores', 'Windows Machine 7.5 GB Memory, 2 cores dedicated, 50 GB Storage SSD', 0, 80)
    #add_product('server', 1, 'w16d', 'Windows Machine 15 GB, dedicated cores', 'Windows Machine 15 GB Memory, 4 cores dedicated, 100 GB Storage SSD', 0, 120)
    #add_product('server', 1, 'w30d', 'Windows Machine 30 GB, dedicated cores', 'Windows Machine 30 GB Memory, 8 cores dedicated, 200 GB Storage SSD', 0, 220)

    #add_product('other', 2, 'ssd', '1 GB SSD Storage', '1 GB SSD Storage (high performance)', 0, 0.3)
    #add_product('other', 2, 'backup', '1 GB Managed Backup', '1 GB Managed Backup', 0, 0.2)
    #add_product('other', 2, 'vsan', '1 GB Virtual SAN Storage', '1 GB Virtual SAN Storage (clustered, 3 copies)', 0, 0.15)
    #add_product('other', 2, 'stor', '1 GB Generic Storage On Storage Cloud', '1GB Generic Storage On Storage Cloud (S3 Interface)', 0, 0.025)


    #add_product('other', 3, 'cb_base', 'Cloudesktop Basic', 'Zentyal Small Business Server ', 0, 80)
    #add_product('other', 3, 'cb_lin', 'Cloudesktop Linux', 'Cloud Desktop Professional (per user, minimal 5) ', 0, 25)
    #add_product('other', 3, 'cb_win', 'Cloudesktop Windows', 'Cloud Desktop Professional (per user, minimal 5)', 0, 50)
    #add_product('other', 3, 'cb_base_cl', 'Cloudesktop clustered', 'Zentyall Small Business Server Clustered', 0, 250)

    #add_product('other', 4, 'sp1', 'Service Credits', 'Service pack for 10 Service Credits (1 time)', 200, 0)
    #add_product('other', 4, 'sp2', 'Service Credits 50', 'Service pack for 50 Service Credits (/month)', 500, 500)
    #add_product('other', 4, 'sp3', 'Service Credits 100', 'Service pack for 100 Service Credits (/month)', 950, 950)
    #add_product('other', 4, 'sp4', 'Service Credits 200', 'Service pack for 200 Service Credits (/month)', 1800, 1800)

    #add_product('other', 5, 'csp', 'Cloudspace', 'Cloudspace + Defense Shield + IP Address (= Enterprise Capable Firewall) ', 0, 10)
    #add_product('other', 5, 'ipaddr', 'Addional IPv4 ip address', 'Addional IPv4 ip address per month ', 0, 2.5)

    add_product('other', 6, 'mon', '24h 7/7 monitoring', '24h 7/7 monitoring of application & recovery services (only for supported apps)', 0, 20)
