
#if customizations are required when doing a export of the jpackage code 

def main(j,jp):
    recipe=jp.getCodeMgmtRecipe()
    recipe.export()

