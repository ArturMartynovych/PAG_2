from tqdm import tqdm
from scipy import stats
import pandas as pd
import os
import requests
import zipfile


def check_folder(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def downloadFiles(year, month):
    url = f'https://dane.imgw.pl/datastore/getfiledown/Arch/Telemetria/Meteo/{year}/Meteo_{year}-{month}.zip'
    response = requests.get(url, stream=True)
    folder_path = 'dane-imgw'
    check_folder(folder_path)
    fileName = f'{folder_path}\Meteo_{year}-{month}.zip'
    with open(fileName, 'wb') as handle:
        for data in tqdm(response.iter_content()):
            handle.write(data)


def unzipFiles(year, month):
    zip_path = f"dane-imgw\Meteo_{year}-{month}.zip"
    extract_path = f"dane-imgw-{year}-{month}"
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)
    return extract_path


def readCSV(path):
    data = pd.read_csv(path, header=None, sep=';', decimal=',')
    data = data[data.columns[:-1]]
    data.columns = ['Name', 'Code', 'Date', 'Value']
    data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d %H:%M')
    return data


listOfCodes = ["B00300S", "B00305A", "B00202A", "B00702A", "B00703A", "B00608S",
               "B00604S", "B00606S", "B00802A", "B00714A", "B00910A"]


def getStatistics(data):
    data_mean = data.groupby([data['Date'].dt.day])['Value'].mean()
    data_median = data.groupby([data['Date'].dt.day])['Value'].median()
    data_trim_mean = stats.trim_mean(data_mean, 0.1)
    frame = {'Mean': data_mean, 'Median': data_median}
    result = pd.DataFrame(frame)
    return result, data_trim_mean


def listOfCoordinated(path):
    lista = []

    with open(path) as f:
        geoData = geojson.load(f)

    for feature in geoData['features']:
        ID = feature['properties']['ifcid']
        Coordinates = feature['geometry']['coordinates']
        items = (ID, Coordinates)
        lista.append(items)
    return lista


PATH = 'effacility.geojson'


def main():
    # year = input("Podaj rok: ")
    year = '2021'
    month = '09'
    # month = input("Podaj miesiąc: ")
    # downloadFiles(year, month)
    # filesPath = unzipFiles(year, month)
    # data = readCSV(f'{filesPath}\{listOfCodes[0]}_{year}_{month}.csv')
    # year = input("Podaj rok: ")
    year = '2021'
    month = '09'
    # month = input("Podaj miesiąc: ")
    # downloadFiles(year, month)
    filesPath = unzipFiles(year, month)
    data = readCSV(f'{filesPath}\{listOfCodes[0]}_{year}_{month}.csv')
    listOfID_and_Coordinates = listOfCoordinated(PATH)
    # print(int(len(myList)))
    for i in range(len(listOfID_and_Coordinates)):
        print(listOfID_and_Coordinates[i][1])
    getStatistics(data)

if __name__ == "__main__":
    main()
    print("GitHub jest bardzo głupi")
