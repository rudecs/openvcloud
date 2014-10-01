import yaml


def main(j, args, params, tags, tasklet):
    def _showexample():
        out = """Actions must be in yaml form.
eg:
{{actions: 
- display: Disable
  action: /restmachine/cloudbroker/account/disable?accountname=${name}&reason=cbportal

- display: Enable
  action: /restmachine/cloudbroker/account/enable?accountname=${name}&reason=cbportal
}}
"""
        params.result = (out, args.doc)
        return params

    page = args.page
    macrostr = args.macrostr.strip()
    content = "\n".join(macrostr.split("\n")[1:-1])

    if not content:
        return _showexample()

    actionoptions = dict()
    actions = yaml.load(content)
    if actions == content:
        return _showexample()

    for actiondata in actions:
        actionoptions.update({actiondata['display']: actiondata['action']})

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
