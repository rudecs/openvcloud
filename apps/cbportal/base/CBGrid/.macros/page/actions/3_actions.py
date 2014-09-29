try:
    import ujson as json
except:
    import json


def main(j, args, params, tags, tasklet):
    page = args.page
    actions = args.getTag('actions')

    if not actions:
        out = 'Missing param "actions". Should be in form of dict.'
        params.result = (out, args.doc)
        return params



    actionoptions = dict()
    try:
      actions = json.loads(actions)
    except Exception:
        out = 'Actions must be in form of dict. eg: actions:{"Disable":"/restmachine/cloudapi/account/disable?accountname=${name}&reason=cbportal","Enable":"/restmachine/cloudapi/account/enable?accountname=${name}&reason=cbportal"} '
        params.result = (out, args.doc)
        return params

    for display, action in actions.iteritems():                
        actionoptions[display] = action

    id = page.addComboBox(actionoptions)

    page.addJS(None, """
        $(document).ready(function() {
            $("#%s").change(function () {
                $.ajax({
                   type: "POST",
                   url: $("#%s").val(),
                });
            });
        });
        """ % (id, id))


    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
