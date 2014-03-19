def main(j,jp,onlycode=False):
   
    #upload jpackage to blobstor
    jp._upload(onlycode=onlycode)