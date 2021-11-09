listOfNumbers = input('Wprowadź listę liczb' + "\n")
teortycznaSuma = int(input())
wprowadzonaLista = listOfNumbers.split()


def check(wprLista, suma):
    RESULT = False
    for i in range(len(wprLista)):
        for j in range(i + 1, len(wprLista)):
            wprLista[i] = int(wprLista[i])
            wprLista[j] = int(wprLista[j])

            if wprLista[i] + wprLista[j] == suma:
                RESULT = True
                break
    if RESULT:
        print("True")
    else:
        print("False")


if __name__ == '__main__':
    check(wprowadzonaLista, teortycznaSuma)
