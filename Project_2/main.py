from tqdm import tqdm
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
    zip_path = f'dane-imgw\Meteo_{year}-{month}.zip'
    extract_path = f'dane-imgw-{year}-{month}'
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)


def main():
    year = input('Podaj rok: ')
    month = input('Podaj miesiąc: ')
    downloadFiles(year, month)
    unzipFiles(year, month)


if __name__ == '__main__':
    main()
