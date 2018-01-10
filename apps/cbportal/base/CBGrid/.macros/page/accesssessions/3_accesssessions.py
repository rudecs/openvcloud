import requests
import json

def main(j, args, params, tags, tasklet):
    jwt = args.requestContext.env['beaker.session'].get('jwt')
    remote = args.requestContext.params.get('ip')
    if jwt:
        resp = requests.get('http://0access:5001/sessions', params={'remote': remote}, headers={'Authorization': 'Bearer {jwt}'.format(jwt=jwt)})
        if resp.status_code == 200:
            sessions = resp.json()['page']['sessions']
            aaData = list()
            for session in sessions:
                itemdata = ['<a href="%s">%s</a>' % (session['href'], session['href'].split('/')[-1])]
                itemdata.append(session['user']['username'])
                itemdata.append(session['remote'])
                itemdata.append(str(session['start']))
                itemdata.append(str(session['end']))
                aaData.append(itemdata)
        else:
            aaData = [['Can not get data from 0-access server jwt may be expired please logout and login again', '', '', '', '']]
    else:
        aaData = [['No jwt found please login and out', '', '', '', '']]

    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    fieldnames = ['Session ID', 'Username', 'Remote', 'Start', 'End']
    page.addList(aaData, fieldnames)
    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
