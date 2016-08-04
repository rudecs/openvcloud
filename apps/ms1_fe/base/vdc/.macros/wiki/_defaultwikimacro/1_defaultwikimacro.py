
def main(j, args, params, tags, tasklet):

    doc = args.doc

    out = "I am the included macro\n"

    # the output of this tasklet (params.result) needs to be wiki content
    # the macro will be replaced with the output in the originating wiki doc
    # play with it you can debug in this tasklet
    # use
    #from pylabs.Shell import ipshellDebug,ipshell
    # print "DEBUG NOW IN TEST TASKLET FOR MACRO"
    # ipshell()

    params.result = (out, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True
