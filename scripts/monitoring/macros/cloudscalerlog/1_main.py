def main(j, args, params, tags, tasklet):
    import time
    import datetime
    from JumpScale import portal

    params.merge(args)
    doc = params.doc
    out = ""
    cl = j.core.osis.getClientByInstance('main')

    osis_ecos = j.core.osis.getClientForCategory(cl, "system", "eco")
    osis_logs = j.core.osis.getClientForCategory(cl, "system", "log")

    #last 20 logs

    log_query = {"query": {"bool": {"must": [{"term": {"category": "machine_history_ui"}}]}}, "sort" :[{"epoch":{"order":"desc"}}]}
    eco_query ={"query": {"bool": {"must": [{"match_all":{}}]}}, "sort" :[{"epoch":{"order":"desc"}}]}

    logs = osis_logs.search(log_query,size=20)['hits']['hits']
    print logs
    ecos = osis_ecos.search(eco_query,size=20)['result']

    out+='h3. Cloudscalers 10.101.175.1 status page\n\n'

    out+='h4. Last successfull actions\n\n'
    out+='||Date || action || Vmid ||\n'
    import ipdb
    for log in logs:
        date = str(datetime.datetime.fromtimestamp(int(log['_source']['epoch'])).strftime('%Y-%m-%d %H:%M:%S'))
        action = log['_source']['message']
        vmid = log['_source']['tags']
        out+='|%s|%s|%s|\n' % (date, action, vmid)

    out+='h4. Last errors on the platform\n\n'

    for eco in ecos:    
        date = str(datetime.datetime.fromtimestamp(int(eco['_source']['epoch'])).strftime('%Y-%m-%d %H:%M:%S'))
        error = eco['_source']['errormessage']
        out+='Time: %s\n\n' % date
        out+='Errormessage: %s \n\n' % error


    params.result = (out, params.doc)
    return params


def match(j, args, params,  tags, tasklet):
    return True
