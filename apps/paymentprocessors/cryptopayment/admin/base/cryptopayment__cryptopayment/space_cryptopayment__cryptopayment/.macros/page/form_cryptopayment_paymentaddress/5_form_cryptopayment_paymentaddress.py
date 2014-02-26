
def main(j,args,params,tags,tasklet):
    
    page=args.page

    mod=j.html.getPageModifierBootstrapForm(page)

    appname="cryptopayment"
    actorname="cryptopayment"
    modelname="paymentaddress"

    if not args.paramsExtra.has_key("guid"):
        raise RuntimeError("ERROR: guid was not known when requesting this page, needs to be an arg")
    guid=args.paramsExtra["guid"]

    actor=j.apps.cryptopayment.cryptopayment
    model=actor.models.paymentaddress.get(guid=guid)

    form=mod.getForm("paymentaddress",actor)

    form.addTextInput("id",reference=form.getReference(model,"id"),default="",help="")
    form.addTextInput("coin",reference=form.getReference(model,"coin"),default="",help="")
    form.addTextInput("accountId",reference=form.getReference(model,"accountId"),default="",help="")


    params.result=mod.addForm(form)    

    return params


def match(j,args,params,tags,tasklet):
    return True

