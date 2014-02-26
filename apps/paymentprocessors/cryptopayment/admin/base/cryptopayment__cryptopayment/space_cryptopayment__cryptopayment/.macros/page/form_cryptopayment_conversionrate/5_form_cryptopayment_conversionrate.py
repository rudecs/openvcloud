
def main(j,args,params,tags,tasklet):
    
    page=args.page

    mod=j.html.getPageModifierBootstrapForm(page)

    appname="cryptopayment"
    actorname="cryptopayment"
    modelname="conversionrate"

    if not args.paramsExtra.has_key("guid"):
        raise RuntimeError("ERROR: guid was not known when requesting this page, needs to be an arg")
    guid=args.paramsExtra["guid"]

    actor=j.apps.cryptopayment.cryptopayment
    model=actor.models.conversionrate.get(guid=guid)

    form=mod.getForm("conversionrate",actor)

    form.addTextInput("time",reference=form.getReference(model,"time"),default="",help="")
    form.addTextInput("currency",reference=form.getReference(model,"currency"),default="",help="")
    form.addTextInput("value",reference=form.getReference(model,"value"),default="",help="")
    form.addTextInput("id",reference=form.getReference(model,"id"),default="",help="")


    params.result=mod.addForm(form)    

    return params


def match(j,args,params,tags,tasklet):
    return True

