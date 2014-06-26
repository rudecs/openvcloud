from JumpScale import j

parentclass=j.core.osis.getOsisImplementationParentClass("cloudbroker")  #is the name of the namespace


class mainclass(parentclass):

    def init(self, path, namespace,categoryname):
        """
        gets executed when catgory in osis gets loaded by osiscmds.py (.init method)
        """
        self.initall( path, namespace,categoryname,db=True)

