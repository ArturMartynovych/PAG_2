from tqdm import tqdm
from scipy import stats
import pandas as pd
import os
import requests
import zipfile
import geopandas as gpd
import time
import datetime
from astral.sun import sun
from astral import LocationInfo


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

year = '2021'
month = '09'


def imgw_data(year, month):
    filesPath = unzipFiles(year, month)
    data = readCSV(f'{filesPath}\{listOfCodes[0]}_{year}_{month}.csv')
    data['Date'] = pd.to_datetime(data['Date'])
    data['Time'] = data['Date'].dt.time
    data['Date'] = data['Date'].dt.date
    data = data[['Name', 'Code', 'Date', 'Time', 'Value']]
    # print(data)
    return data


def names_of_miejc():
    stacji = gpd.read_file("effacility (1).geojson")
    stacji.set_crs(epsg=2180, inplace=True, allow_override=True)
    stacji.to_crs(epsg=4326, inplace=True)

    powiaty = gpd.read_file("Dane/powiaty.shp")
    powiaty.to_crs(epsg=4326, inplace=True)

    wojew = gpd.read_file("Dane/woj.shp")
    wojew.to_crs(epsg=4326, inplace=True)

    stacji_in_wojew = stacji.sjoin(wojew, how="inner", predicate="intersects")
    stacji_in_wojew = stacji_in_wojew[["ifcid", "name1", "name_right", "geometry"]]
    all_together = stacji_in_wojew.sjoin(powiaty, how="inner", predicate="intersects")
    all_together = all_together[["ifcid", "name1", "name_right", "name", "geometry"]]
    all_together.rename(columns={"name1": "Name of Station", "name_right": "Województwo", "name": "Powiat"},
                        inplace=True)
    # Getting x and y values from geometry
    all_together['lat'] = all_together.geometry.x
    all_together['lon'] = all_together.geometry.y
    return all_together
    # print(all_together)


def merge_all(year, month):
    data = imgw_data(year, month)
    meteo_stations = names_of_miejc()

    data_of_stations = pd.merge(data, meteo_stations, left_on='Name', right_on='ifcid')
    data_of_stations = data_of_stations[['ifcid', 'Name', 'Date', 'Time', 'Value', 'Name of Station',
                                         'Województwo', 'Powiat', 'geometry', 'lat', 'lon']]
    # print(data_of_stations)
    return data_of_stations


def get_sun(date, lat, lon):
    meteo = LocationInfo(lat, lon)
    return sun(meteo.observer, date=date)


def map_get_sun(df):
    return pd.Series(map(get_sun, df['Date'], df['lat'], df['lon']))


def day_or_night(s, time):
    return s["sunrise"].time() < time < s["sunset"].time()


def map_day_or_night(df):
    return pd.Series(map(day_or_night, df['Sun'], df['Time']))


def adding_sun_day(year, month):
    data_stations = merge_all(year, month)

    mask = data_stations.Date.diff() != datetime.timedelta()
    temp = data_stations[mask].copy()

    temp['Sun'] = None
    data_stations['Sun'] = None

    temp.reset_index(drop=False, inplace=True)
    temp['Sun'] = map_get_sun(temp)
    temp.set_index('index', inplace=True)

    data_stations['Sun'] = temp['Sun']
    data_stations['Sun'].fillna(method="ffill", inplace=True)

    data_stations['day'] = map_day_or_night(data_stations)
    # print(data_stations[data_stations.day == True])  # -> Wyświetlanie wartości True kiedy jest dzień
    return data_stations


def value_in(data):
    value_wojew = []
    value_powiat = []

    trim = lambda x: stats.trim_mean(x, 0.1)

    wojew_per_day = data[['Value', 'Województwo', 'Date', 'day']].groupby(
        ['Województwo', 'Date', 'day']).agg({"Value": trim}).reset_index()

    powiat_per_day = data[['Value', 'Powiat', 'Date', 'day']].groupby(
        ['Powiat', 'Date', 'day']).agg({"Value": trim}).reset_index()

    wojew_per_10_min = data[['Value', 'Województwo', 'Date', 'Time', 'day']].groupby(
        ['Województwo', 'Date', 'Time', 'day']).agg({"Value": trim}).reset_index()

    powiat_per_10_min = data[['Value', 'Powiat', 'Date', 'Time', 'day']].groupby(
        ['Powiat', 'Date', 'Time', 'day']).agg({"Value": trim}).reset_index()

    value_wojew.append(wojew_per_day)
    value_wojew.append(wojew_per_10_min)

    value_powiat.append(powiat_per_day)
    value_powiat.append(powiat_per_10_min)
    return value_wojew, value_powiat


def main():
    data_stations = adding_sun_day('2021', '09')
    value_wojew, value_powiat = value_in(data_stations)
    # print(value_wojew[0])       # Value w Województwach dla każdego dnia, w zależności od dnia i nocy
    # print(value_wojew[1])       # Value w Województwach co 10 minut, w zależności od dnia i nocy

    # print(value_powiat[0])      # Value w Powiecie dla każdego dnia, w zależności od dnia i nocy
    print(value_powiat[1])  # Value w Powiecie co 10 minut, w zależności od dnia i nocy


if __name__ == "__main__":
    main()
