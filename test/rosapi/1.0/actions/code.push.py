
#if customizations are required when doing a push of the code of the jpackage back to their repo

def main(j,jp):
    recipe=jp.getCodeMgmtRecipe()
    recipe.push()

