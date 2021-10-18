def check(agg, list):
    result = False
    for i in range(len(list)):
        for j in range(i + 1, len(list)):
            if list[i] + list[j] == agg:
                result = True
                print('True')
                break
    if not result:
        print('False')


def main():
    aggregate = int(input('Suma: '))
    list = [int(x) for x in input('Tablica liczb: ').split()]
    check(aggregate, list)


if __name__ == '__main__':
    main()