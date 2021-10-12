listOfNumbers = input('Wprowadź listę liczb' + "\n")
teortycznaSuma = int(input())
wprowadzonaLista = listOfNumbers.split()


def check(wprowadzonaLista, teortycznaSuma):
    RESULT = False
    for i in range(len(wprowadzonaLista)):
        for j in range(i + 1, len(wprowadzonaLista)):
            wprowadzonaLista[i] = int(wprowadzonaLista[i])
            wprowadzonaLista[j] = int(wprowadzonaLista[j])

            if wprowadzonaLista[i] + wprowadzonaLista[j] == teortycznaSuma:
                RESULT = True
                break
    if RESULT == True:
        print("True")
    else:
        print("False")


if __name__ == '__main__':
    check(wprowadzonaLista, teortycznaSuma)
