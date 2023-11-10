import re
import time
import pandas as pd

import requests
from bs4 import BeautifulSoup


def get_apartment_data(url):
    response = requests.get(url)
    time.sleep(1)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extracting room count
    title_text = soup.find("div", class_="offer__advert-title").find("h1").text
    room_count_match = re.search(r'(\d+)-комнатная', title_text)
    room_count = int(room_count_match.group(1)) if room_count_match else None

    # Extracting quadrature
    quadrature = float(title_text.split(',')[1].split()[0])

    # Extracting floor
    floor_div = soup.find("div", {"data-name": "flat.floor"})
    floor_info_text = floor_div.find("div", class_="offer__advert-short-info").text
    floor_info = floor_info_text.split('из')
    floor_text = floor_info[0].strip()+"/"+floor_info[1].strip()
    floor = round(float(floor_info[0].strip()) / float(floor_info[1].strip()), 2)

    # Extracting region
    region_text = soup.find("div", class_="offer__location offer__advert-short-info").find("span").text.split(',')[1].strip()
    if region_text == 'Алатауский р-н':
        region = 0+1e-10
    elif region_text == 'Алмалинский р-н':
        region = 0.075
    elif region_text == 'Ауэзовский р-н':
        region = 0.51
    elif region_text == 'Бостандыкский р-н':
        region = 1
    elif region_text == 'Жетысуский р-н':
        region = 0.076
    elif region_text == 'Медеуский р-н':
        region = 0.69
    elif region_text == 'Наурызбайский р-н':
        region = 0.11
    elif region_text == 'Турксибский р-н':
        region = 0.083

    # Extracting year
    year_div = soup.find("div", {"data-name": "house.year"})
    year_text = year_div.find("div", class_="offer__advert-short-info").text
    year = int(''.join(filter(str.isdigit, year_text)))

    # Extracting price
    price_text = soup.find("div", class_="offer__price").text
    price = int("".join(filter(str.isdigit, price_text)))

    # Extracting about
    about_dict = {}

    apartmentAbout = soup.find("div", class_="offer__parameters")

    if len(apartmentAbout) != 1:
        desired_data_names = ['flat.toilet', 'flat.balcony', 'flat.balcony_g', 'flat.door', 'inet.type', 'flat.parking',
                              'live.furniture', 'flat.flooring']

        for desired_data_name in desired_data_names:
            # Find the dt element with the specified data-name
            dt_element = apartmentAbout.find('dt', {"data-name": desired_data_name})

            about_name = desired_data_name.replace('.', '_')
            # print(about_name)
            # If the dt element is found, extract the dd value
            if dt_element:
                dd_element = dt_element.find_next_sibling("dd")
                if dd_element:
                    about_dict[about_name] = dd_element.get_text().strip()
                    # print(dd_element.get_text().strip())
            else:
                about_dict[about_name] = 'no_info'

    # Extracting ceiling
    dt_element = apartmentAbout.find('dt', {"data-name": 'ceiling'})

    if dt_element:
        dd_element = dt_element.find_next_sibling("dd")
        if dd_element:
            about_dict['ceiling'] = dd_element.get_text().strip().split()[0]
    else:
        about_dict['ceiling'] = None

    # Extracting flat.priv_dorm
    dt_element = apartmentAbout.find('dt', {"data-name": 'flat.priv_dorm'})

    if dt_element:
        dd_element = dt_element.find_next_sibling("dd")
        if dd_element:
            if dd_element.get_text().strip() == 'да':
                about_dict['flat_priv_dorm'] = 1
            else:
                about_dict['flat_priv_dorm'] = 0
    else:
        about_dict['flat_priv_dorm'] = 0

    total_dict = {"price": price,
                  "room_count": room_count,
                  "quadrature": quadrature,
                  "floor_text": floor_text,
                  "floor": floor,
                  "region_text": region_text,
                  "region": region,
                  "year": year}
    total_dict.update(about_dict)
    # print(total_dict)
    return total_dict

data = []

df = pd.read_csv('test.csv')
links = df.iloc[:, 0].values
for link in links[0:5]:
    try:
        print(link)
        apartment_data = get_apartment_data(link)
        data.append(apartment_data)
    except Exception as e:
        print(f"Failed to extract data from {link}. Error: {e}")

df = pd.DataFrame(data, columns=["price", "room_count", "quadrature", "floor_text", "floor", "region_text", "region", "year",
                                 "flat_toilet", "flat_balcony", "flat_balcony_g",
                                 "flat_door", "inet_type", "flat_parking", "live_furniture",
                                 "flat_flooring", "ceiling"])
df.to_csv("apartments_data.csv", index=False)