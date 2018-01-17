import requests
import json
import datetime

def main(j, args, params, tags, tasklet):
    remote = args.requestContext.params.get('ip')
    remote_data = ', "remote": %s' % remote if remote else ''
    oauth = j.clients.oauth.get(instance='itsyouonline')
    jwt = oauth.get_active_jwt(session=args.requestContext.env['beaker.session'])
    if jwt:
        table_data = j.apps.cloudbroker.zeroaccess.listSessions(remote=remote, ctx=args.requestContext)
        html = """
            <script>
            function testClick() {
                var txt = $("#search-sessions-txt").val();
                $.ajax({
                    type: "POST",
                    url: "/restmachine/cloudbroker/zeroaccess/listSessions",
                    data: {"query": txt %s},
                    crossDomain: true,
                    success: function(msg) {
                        $("#DataTables_Table_1").DataTable().clear();
                        $("#DataTables_Table_1").DataTable().rows.add(msg);
                        $("#DataTables_Table_1").DataTable().draw();
                    },
                    error: function(jq,status) {
                        console.log(jq);
                        console.log(status);
                    }
                });
            }
            </script>
        """ % (remote_data)
    else:
        table_data = [['No jwt found please login and out', '', '', '', '']]

    page = args.page

    fieldnames = ['Session ID', 'Username', 'Remote', 'Start', 'End']
    page.addList(table_data, fieldnames)
    page.addHTML(html)
    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
