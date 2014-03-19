
#if customizations are required when doing a a linking of the jpackage code to the OS

def main(j,jp,force=True):
    recipe=jp.getCodeMgmtRecipe()
    recipe.link(force=force)

