import requests
import json

def main(j, args, params, tags, tasklet):
    page = args.page
    counter = """
<script>
window.onload=function(){
var counter = %s;
var interval = setInterval(function() {
    counter--;
    document.getElementById('counter').innerText = "The following data will be expired in " + counter + " seconds if you didn't use it"
    if (counter <= 0) {
        document.getElementById('counter').innerText = "this data is no longer valid"
    }
}, 1000);
}
</script>
    """
    remote = args.requestContext.params.get('ip')
    oauth = j.clients.oauth.get(instance='itsyouonline')
    jwt = oauth.get_active_jwt(session=args.requestContext.env['beaker.session'])
    if jwt:
        init_time_data = j.apps.cloudbroker.zeroaccess.getSessionInitTime(ctx=args.requestContext)
        if init_time_data:
            session_init_time = init_time_data['session_init_time']
        else:
            session_init_time = 60
        counter = counter % (session_init_time)
        session_data = j.apps.cloudbroker.zeroaccess.provision(remote=remote, ctx=args.requestContext)
        if session_data:
            username=session_data['username']
            ip=session_data['ssh_ip']
            port=session_data['ssh_port']
            link = "chrome-extension://pnhechapfaindjhompbnflcldabbghjo/html/nassh.html#{username}@{ip}:{port}".format(username=username, ip=ip, port=port)
            ssh_command2 = '<h4><span id="counter"></span></h4> You can click this link if you have secure shell plugin installed <a href="{link}">connect with secure shell</a> \
            <br /> or use the following info to connect from terminal'.format(link=link)
            ssh_command = "ssh {username}@{ip} -p {port}".format(username=username, ip=ip, port=port)
            page.addHTML(ssh_command2)
            page.addCodeBlock(ssh_command, template='bash')
            page.addHTML(counter)
        else:
            page.addCodeBlock("Can not get provisioning data may be jwt has expired", template='bash')
    else:
        page.addCodeBlock("No jwt found in your session please logout and in again", template='bash')

    params.result = page
    return params