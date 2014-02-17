from JumpScale import j

class cryptopayment_processor(j.code.classGetBase()):
    """
    API Actor api for processing payments with cryptocurrency
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="processor"
        self.appname="cryptopayment"
        #cryptopayment_processor_osis.__init__(self)
