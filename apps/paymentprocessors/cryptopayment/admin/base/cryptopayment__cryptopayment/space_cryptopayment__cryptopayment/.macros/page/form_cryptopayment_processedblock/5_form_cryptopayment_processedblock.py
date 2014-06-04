
def main(j,args,params,tags,tasklet):
    
    page=args.page

    mod=j.html.getPageModifierBootstrapForm(page)

    appname="cryptopayment"
    actorname="cryptopayment"
    modelname="processedblock"

    if not args.paramsExtra.has_key("guid"):
        raise RuntimeError("ERROR: guid was not known when requesting this page, needs to be an arg")
    guid=args.paramsExtra["guid"]

    actor=j.apps.cryptopayment.cryptopayment
    model=actor.models.processedblock.get(guid=guid)

    form=mod.getForm("processedblock",actor)

    form.addTextInput("blocktime",reference=form.getReference(model,"blocktime"),default="",help="")
    form.addTextInput("hash",reference=form.getReference(model,"hash"),default="",help="")
    form.addTextInput("coin",reference=form.getReference(model,"coin"),default="",help="")
    form.addTextInput("id",reference=form.getReference(model,"id"),default="",help="")


    params.result=mod.addForm(form)    

    return params


def match(j,args,params,tags,tasklet):
    return True

