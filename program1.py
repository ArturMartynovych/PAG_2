def check(lista, suma):
    RESULT = False
    for i in range(len(lista)):
        for j in range(i + 1, len(lista)):
            lista[i] = int(lista[i])
            lista[j] = int(lista[j])

            if lista[i] + lista[j] == suma:
                RESULT = True
                break
    if RESULT:
        print("True")
    else:
        print("False")


def main():
    listOfNumbers = input('Wprowadź listę liczb' + "\n")
    teortycznaSuma = int(input())
    wprowadzonaLista = listOfNumbers.split()
    check(wprowadzonaLista, teortycznaSuma)


if __name__ == '__main__':
    main()
