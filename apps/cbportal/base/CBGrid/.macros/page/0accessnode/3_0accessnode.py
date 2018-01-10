import requests
import json

def main(j, args, params, tags, tasklet):
    page = args.page
    remote = args.requestContext.params.get('ip')
    jwt = args.requestContext.env['beaker.session'].get('jwt')
    if jwt:
        resp = requests.get('http://0access:5001/provision/{}'.format(remote), headers={'Authorization': 'Bearer {jwt}'.format(jwt=jwt)})
        if resp.status_code == 200:
            ssh = resp.json()
            username=ssh['username']
            ip=ssh['ssh_ip']
            port=ssh['ssh_port']
            link = "chrome-extension://pnhechapfaindjhompbnflcldabbghjo/html/nassh.html#{username}@{ip}:{port}".format(username=username, ip=ip, port=port)
            ssh_command2 = 'You can click this link if you have secure shell plugin installed <a href="{link}">connect with secure shell</a> \
            <br /> or use the following info to connect from terminal'.format(link=link)
            ssh_command = "ssh {username}@{ip} -p {port}".format(username=username, ip=ip, port=port)
            page.addHTML(ssh_command2)
            page.addCodeBlock(ssh_command, template='bash')
        else:
            page.addCodeBlock("Can not get provisioning data may be jwt has expired", template='bash')
    else:
        page.addCodeBlock("No jwt found in your session please logout and in again", template='bash')

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
