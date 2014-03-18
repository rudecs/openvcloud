
#if customizations are required when doing a the packaging of the code for the jpackage, will generate buildnr as well

def main(j,jp):
    recipe=jp.getCodeMgmtRecipe()
    recipe.package(jp)

