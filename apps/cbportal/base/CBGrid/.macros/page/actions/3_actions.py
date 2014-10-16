def main(j, args, params, tags, tasklet):
    import json
    import yaml
    def _showexample():
        out = """Actions must be in yaml form.
eg:
{{actions:
- display: Start
  input: 
  - reason
  - spacename
  action: /restmachine/cloudbroker/machine/start
  data: 
   machineId: $$id
   accountName: $$accountname

- display: Stop
  action: /restmachine/cloudbroker/machine/stop?machineId=$$id&reason=ops&accountName=$$accountname&spaceName=$$spacename
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
        actionurl = actiondata['action']
        display = actiondata['display']
        inputs = actiondata.get('input', '')
        data = actiondata.get('data', {})
        actionid = display.replace(' ', '')
        actionoptions.update({display: actionid})

        action = """
<div class="container">
  <div id="action-%s" class="modal fade" style="text-align: initial;">
       <div class="modal-dialog">
           <div class="modal-content">
               <div class="modal-header">
                   <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                   <h4 class="modal-title">Confirm Action %s</h4>
               </div>
               <div class="modal-body">
               """ % (actionid, display)
        if inputs:
            actions = action+"\nFill out these values\n"
            for var in inputs:
                action = action+"""
                       <p>%s</p>
                       <input data-name="%s" class="action-input"  />
                       """ % (var, var)
        action = action + """
               </div>
               <div class="modal-footer">
                   <button type="button" class="modal-ok-btn btn btn-primary">OK</button>
                   <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
               </div>
           </div>
       </div>
   </div>
</div>"""

        page.addHTML(action)

        js = """
    $(document).ready(function() {
          // on-ok-button event
         $("#action-%s .modal-ok-btn").click(function(){
          // get values
          var data = %s;
          var inputs = $("#action-%s .action-input");
          for (var i=0; i < inputs.length; i++) {
              var input = $(inputs[i]);
              data[input.data('name')] = input.val();
          }
          $.ajax({
                   type: "POST",
                   url: "%s",
                   data: data,
                });
         });
         // on-cancel-button event
         $(".modal-cancel-btn").click(function(){
             // 
         });
    });
            """ % (actionid, json.dumps(data), actionid, actionurl)
        page.addJS(None, js)

    id = page.addComboBox(actionoptions, {'#': 'Choose Action'})
    page.addJS(None, """
        $(document).ready(function() {
            $("#%(id)s").change(function () {
                 var actionid = $("#%(id)s").val();
                 if (actionid != '#'){
                    $('#action-'+actionid).modal('show');
                 }
            });
        });
        """ % ({'id':id}))
    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
