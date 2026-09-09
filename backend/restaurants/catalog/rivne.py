"""Source-backed Rivne catalog records.

Locations are sourced from OpenStreetMap and are published under ODbL 1.0.
Menu, ratings, imagery, and opening hours remain empty until each value is
verified from an authorized or compatible source.
"""


def _venue(
    catalog_key,
    name,
    street,
    house_number,
    latitude,
    longitude,
    cuisine,
    osm_node_id,
):
    address = ", ".join(part for part in (street, house_number, "Рівне") if part)
    return {
        "catalog_key": catalog_key,
        "name": name,
        "description": f"Заклад у Рівному за адресою {address}.",
        "address": address,
        "latitude": latitude,
        "longitude": longitude,
        "cuisine": cuisine,
        "rating": None,
        "review_count": 0,
        "delivery_time": None,
        "image_url": "",
        "opening_hours": {},
        "menu_items": (),
        "provenance": {
            "source_url": f"https://www.openstreetmap.org/node/{osm_node_id}",
            "verified_at": "2026-09-09",
            "license": "ODbL-1.0",
        },
    }


RIVNE_CATALOG = (
    _venue(
        "brovarnia-na-hrushevskoho",
        "Броварня на Грушевського",
        "вулиця Академіка Грушевського",
        "77",
        "50.617499",
        "26.273941",
        "Pub",
        5626631722,
    ),
    _venue("apelsyn", "Апельсин", "вулиця 16 Липня", "36", "50.616418", "26.249366", "Other", 4312747087),
    _venue("arka", "Арка", "Соборна вулиця", "15", "50.618765", "26.254195", "Other", 4482677889),
    _venue("brooklyn", "Бруклин", "вулиця Степана Бандери", "36", "50.612428", "26.263747", "Italian", 4315508039),
    _venue("dorozhnie", "Дорожнє", "Привокзальна площа", "7", "50.628444", "26.240217", "Other", 4312633033),
    _venue("edem", "Едем", "Кавказька вулиця", "2", "50.626168", "26.252098", "Other", 4312438492),
    _venue("kavovi-meshty", "Кавові мешти", "вулиця Степана Бандери", "60а", "50.611262", "26.275236", "Cafe", 4315508073),
    _venue("kofein", "Кофеїн", "вулиця Міцкевича", "34", "50.623490", "26.255532", "Cafe", 4312438506),
    _venue("lanch", "Ланч", "вулиця Соломії Крушельницької", "77", "50.616528", "26.268059", "Other", 11043777814),
    _venue("gruzynski-tradytsii-bandery", "Магазин-пекарня \"Грузинські Традиції\"", "вулиця Степана Бандери", "60а", "50.610806", "26.275706", "Georgian", 5103141190),
    _venue("gruzynski-tradytsii-soborna", "Магазин-пекарня \"Грузинські Традиції\"", "Соборна вулиця", "1", "50.617248", "26.264235", "Georgian", 6593027189),
    _venue("marlen", "Марлен", "вулиця Юрія Гагаріна", "39А", "50.629179", "26.268054", "Other", 6278796215),
    _venue("na-hirtsi", "На гірці", "Соборна вулиця", "3Д", "50.617178", "26.255992", "Italian", 6657689720),
    _venue("pan-khaliavskyi", "Пан Халявський", "вулиця Гетьмана Сагайдачного", "4", "50.621856", "26.245182", "Other", 4312651875),
    _venue("panama", "Панама", "майдан Незалежності", "1", "50.619736", "26.250044", "Italian", 1374756434),
    _venue("sytsyliia", "Сицилія", "проспект Миру", "9", "50.623062", "26.251620", "Other", 4312588555),
    _venue("bazzikalo", "Bazzikalo", "Відінська вулиця", "10", "50.614211", "26.274478", "Cafe", 3645867599),
    _venue("equador-coffee-pokrovsky", "Equador Coffee Pokrovsky", "вулиця Княгині Ольги", "1", "50.616882", "26.264942", "Cafe", 13202281871),
    _venue("fortissimo", "Fortissimo", "вулиця 16 Липня", "7А", "50.619092", "26.250896", "Other", 6211151587),
    _venue("roomzza", "Roomzza", "вулиця Степана Бандери", "47", "50.612553", "26.265866", "Italian", 4315508041),
    _venue("wake-up-rivne", "Wake Up Rivne", "проспект Миру", "9", "50.623161", "26.251567", "Cafe", 4312588556),
    _venue("kaviarnia-seim", "Кав'ярня Сейм", "Відінська вулиця", "38", "50.608183", "26.274979", "Cafe", 9412444176),
    _venue("kava-mava", "Кава Мава", "Відінська вулиця", "33", "50.608593", "26.276089", "Cafe", 9412259341),
    _venue("la-bulka", "Ла Булка", "Фабрична вулиця", "14", "50.641745", "26.275231", "Bakery", 6249659566),
    _venue("levada", "Левада", "вулиця Василя Червонія", "65", "50.633651", "26.276668", "Other", 4744628124),
    _venue("melanzh", "Меланж", "Київська вулиця", "36", "50.615071", "26.282089", "Ukrainian", 4382898103),
    _venue("sokyra", "Сокира", "вулиця Володимира Стельмаха", "1", "50.605036", "26.274793", "Other", 9412217601),
    _venue("tradytsia", "Традиція", "Відінська вулиця", "21", "50.609561", "26.278817", "Other", 5103141188),
    _venue("tundyr-haus", "Тундир • Хаус", "Київська вулиця", "67А", "50.616969", "26.280596", "Georgian", 4720416602),
    _venue("craft", "Craft", "Відінська вулиця", "42а", "50.607511", "26.274286", "Italian", 13990792019),
    _venue("equador-coffee", "Equador Coffee", "Відінська вулиця", "48", "50.605758", "26.272609", "Cafe", 9412217595),
    _venue("granat", "Granat", "вулиця Володимира Стельмаха", "6", "50.604359", "26.274153", "Other", 9412352615),
    _venue("km-coffee", "KM Coffee", "Відінська вулиця", "39", "50.606555", "26.274153", "Cafe", 9412259338),
)