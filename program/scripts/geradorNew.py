from .jornalistChef import *
#aqui ele vai pegar as funções de jornalistChef, e vai retornar uma nóticia apenas

def PrintNews(n):
    for x in range(n):
        print(getOneNews())

def getANews():
    return getOneNews()


