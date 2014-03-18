
#if customizations are required when doing a commit of the jpackage

def main(j,jp):
    recipe=jp.getCodeMgmtRecipe()
    recipe.commit()

