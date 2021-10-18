def wprList():
    listOfNumbers = input('Wprowadź listę liczb' + "\n")
    wprowadzonaLista = listOfNumbers.split()
    wprowadzonaLista = list(map(int, wprowadzonaLista))
    wprowadzonaLista.sort()
    return wprowadzonaLista


def algEratos(lista):
    maxVal = lista[-1]
    prime = [True] * (maxVal + 1)

    for i in range(2, int(maxVal ** 0.5) + 1):
        if prime[i]:
            for j in range(2 * i, maxVal + 1, i):
                prime[j] = False

    return prime


def main(lista):
    primes = algEratos(lista)
    for p in lista:
        if primes[p] and 0 != p != 1:
            print(str(p))


if __name__ == '__main__':
    tab = wprList()
    main(tab)
