import geopandas as gpd
import pandas as pd
import time
import datetime
import os
import zipfile
import pymongo
import geojson
import requests
import redis
from scipy import stats
from astral.sun import sun
from astral import LocationInfo
from tqdm import tqdm


def month_dictionary(text):
    month_dict = {'1': 'styczeń', '2': 'luty', '3': 'marzec', '4': 'kwiecień', '5': 'maj', '6': 'czerwiec',
                        '7': 'lipiec', '8': 'sierpień', '9': 'wrzesień', '10': 'październik', '11': 'listopad',
                                '12': 'grudzień'}
    return month_dict[text]


def month_dictionary_2(text):
    month_dict = {'styczeń': '01', 'luty': '02', 'marzec': '03', 'kwiecień': '04', 'maj': '05', 'czerwiec': '06',
                    'lipiec': '07', 'sierpień': '08', 'wrzesień': '09', 'październik': '10', 'listopad': '11',
                                'grudzień': '12'}
    return month_dict[text]


def code_dictionary(text):
    code_dict = {'Temperatura powietrza [°C]': "B00300S", 'Temperatura gruntu [°C]': "B00305A",
                    'Kierunek wiatru [°]': "B00202A", 'Średnia prędkość wiatru [m/s]': "B00702A",
                        'Maksymalna prędkość wiatur [m/s]': "B00703A", 'Suma opadu 10 minutowego': "B00608S",
                            'Suma opadu dobowego': "B00604S", 'Suma opadu godzinowego': "B00606S",
                                'Względna wilgotność powietrza': "B00802A", 'Największy poryw wiatru': "B00714A",
                                    'Zapas wody w śniegu': "B00910A"}
    return code_dict[text]


def check_folder(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def check_directory(directory):
    if os.path.exists(directory):
        return True
    else:
        return False


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
    downloadFiles(year, month)
    zip_path = f"dane-imgw\Meteo_{year}-{month}.zip"
    extract_path = f"dane-imgw-{year}-{month}"
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)


def readCSV(path):
    data = pd.read_csv(path, header=None, sep=';', decimal=',')
    data = data[data.columns[:-1]]
    data.columns = ['Name', 'Code', 'Date', 'Value']
    data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d %H:%M')
    return data


def imgw_data(year, month, m_type):
    filesPath = f"dane-imgw-{year}-{month}"
    data = readCSV(f'{filesPath}\{m_type}_{year}_{month}.csv')
    data['Date'] = pd.to_datetime(data['Date'])
    data['Time'] = data['Date'].dt.time
    data['Date'] = data['Date'].dt.date
    data = data[['Name', 'Code', 'Date', 'Time', 'Value']]
    return data


def names_of_miejc():
    stacji = gpd.read_file("Dane/effacility.geojson")
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
    all_together['lat'] = all_together.geometry.x
    all_together['lon'] = all_together.geometry.y
    return all_together


def merge_all(year, month, m_type, meteo_stations):
    data = imgw_data(year, month, m_type)
    data_of_stations = pd.merge(data, meteo_stations, left_on='Name', right_on='ifcid')
    data_of_stations = data_of_stations[['ifcid', 'Name', 'Date', 'Time', 'Value', 'Name of Station',
                                         'Województwo', 'Powiat', 'geometry', 'lat', 'lon']]
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


def adding_sun_day(year, month, m_type, meteo_stations):
    data_stations = merge_all(year, month, m_type, meteo_stations)

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

    # powiat_per_day = data[['Value', 'Powiat', 'Date', 'day']].groupby(
    #     ['Powiat', 'Date', 'day']).agg({"Value": trim}).reset_index()

    powiat_per_day = data[['Value', 'Województwo', 'Powiat', 'Date', 'day']].groupby(
        ['Powiat', 'Województwo', 'Date', 'day']).agg({"Value": trim}).reset_index()

    wojew_per_10_min = data[['Value', 'Województwo', 'Date', 'Time', 'day']].groupby(
        ['Województwo', 'Date', 'Time', 'day']).agg({"Value": trim}).reset_index()

    powiat_per_10_min = data[['Value', 'Powiat', 'Date', 'Time', 'day']].groupby(
        ['Powiat', 'Date', 'Time', 'day']).agg({"Value": trim}).reset_index()

    value_wojew.append(wojew_per_day)
    value_wojew.append(wojew_per_10_min)

    value_powiat.append(powiat_per_day)
    value_powiat.append(powiat_per_10_min)
    return value_wojew, value_powiat


def mongo_add_collection(db_name, collection_name, df, changed_columns):
    collection = db_name[collection_name]
    df[changed_columns] = df[changed_columns].astype(str)
    df.reset_index(inplace=True)
    df_dict = df.to_dict('records')
    collection.insert_many(df_dict)


def db_redis(db, df, changed_columns):
    df[changed_columns] = df[changed_columns].astype(str)
    # df.reset_index(inplace=True)
    keys = [str(key) for key in df.iloc[:, :-1].to_dict('records')]
    values = df[['Value']].to_dict('records')

    for key, value in zip(keys, values):
        # print(f'{key}: {value}')
        db.hmset(key, value)


def save2neo4j(graph, wdf, pdf):
    tx = graph.begin()
    for index, row in wdf.iterrows():
        tx.evaluate('''
               MERGE (w:wojew{name:$Województwo})
               MERGE (d:time{date:$Date, day: $day})
               MERGE (v:temp{value: $Value})
               MERGE (v)-[r1:WHEN]->(d)
               MERGE (v)-[r2:LOCATION]->(w)
               ''', parameters={'Województwo': str(row['Województwo']), 'Date': str(row['Date']),
                                'Value': float(row['Value']), 'day': bool(row['day'])})
    graph.commit(tx)
    print("wojew committed")

    tx = graph.begin()
    for index, row in pdf.iterrows():
        tx.evaluate('''
                       MERGE (p:powiat{name:$Powiat, wojewodztwo: $Województwo})
                       MERGE (d:time{date:$Date, day: $day})
                       MERGE (v:temp{value: $Value})
                       MERGE (v)-[r1:WHEN]->(d)
                       MERGE (v)-[r2:LOCATION]->(p)
                       ''', parameters={'Województwo': str(row['Województwo']), 'Powiat': str(row['Powiat']),
                                        'Date': str(row['Date']), 'Value': float(row['Value']),
                                        'day': bool(row['day'])})
    graph.commit(tx)
    tx = graph.begin()
    print("powiaty committed")
    tx.evaluate('''
            MATCH(w: wojew), (p:powiat) WHERE w.name = p.wojewodztwo
            CREATE (p)-[r: IN]->(w)''')
    graph.commit(tx)
    print("match done")


def query_neo4j(query):
    graph = Graph("bolt://localhost:7687", user="neo4j", password="haslo")
    result = graph.run(query).data()
    return result