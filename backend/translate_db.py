import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from restaurants.models import MenuItem
import re

name_map = {
    'Банош': 'Banosh',
    'Піца Маргарита (Бруклин)': 'Margherita Pizza (Brooklyn)',
    'Піца Маргарита (Панама)': 'Margherita Pizza (Panama)',
    'Паста Карбонара': 'Spaghetti Carbonara',
    'Еспресо (Equador Coffee)': 'Espresso (Equador Coffee)',
    'Еспресо (Wake Up Rivne)': 'Espresso (Wake Up Rivne)',
    'Еспресо (KM Coffee)': 'Espresso (KM Coffee)',
    'Деруни': 'Deruny',
    'Круасан з шоколадом': 'Chocolate Croissant',
    'Багет (Ла Булка)': 'Baguette (La Bulka)',
    'Хінкалі': 'Khinkali',
    'Хачапурі (Тундир • Хаус)': 'Khachapuri (Tandoor House)',
    'Вареники з картоплею': 'Varenyky with Potatoes',
    'Тірамісу': 'Tiramisu',
    'Сінабон': 'Cinnabon',
    'Курячий Вреп': 'Chicken Wrap',
    'Круасан': 'Croissant',
    'Еспресо (Кофеїн)': 'Espresso (Kofein)',
    'Піца Маргарита (Craft)': 'Margherita Pizza (Craft)',
    "Еспресо (Кав'ярня Сейм)": 'Espresso (Seim Coffee Shop)',
    'Лобіо': 'Lobio',
    'Еспресо (Equador Coffee Pokrovsky)': 'Espresso (Equador Coffee Pokrovsky)',
    'Піца Маргарита (Roomzza)': 'Margherita Pizza (Roomzza)',
    'Шашлик': 'Shashlik',
    'Капучино': 'Cappuccino',
    'Еспресо (Bazzikalo)': 'Espresso (Bazzikalo)',
    'Фокачча': 'Focaccia',
    'Піца Маргарита (На гірці)': 'Margherita Pizza (Na Hirtsi)',
    'Еклер': 'Eclair',
    'Чизкейк': 'Cheesecake',
    'Еспресо (Кавові мешти)': 'Espresso (Kavovi Meshty)',
    'Борщ (Меланж)': 'Borscht (Melange)',
    'Еспресо (Кава Мава)': 'Espresso (Kava Mava)',
    'Чорний хліб': 'Rye Bread',
    'Хачапурі (Магазин-пекарня "Грузинські Традиції")': 'Khachapuri (Georgian Traditions Bakery)'
}

desc_map = {
    'Грузинський хліб з сиром': 'Georgian bread with cheese',
    'Страва з квасолі': 'Bean dish',
    'Французький масляний круасан': 'French butter croissant',
    'Класичний чизкейк': 'Classic cheesecake',
    'Кукурудзяна каша з бринзою': 'Corn porridge with brynza',
    'Вареники зі сметаною': 'Varenyky with sour cream',
    'Картопляні млинці': 'Potato pancakes',
    'Класичне еспресо': 'Classic espresso',
    'Еспресо з молочною пінкою': 'Espresso with milk foam',
    'Паста з беконом та пармезаном': 'Pasta with bacon and parmesan',
    'Французький багет': 'French baguette',
    "Грузинські вареники з м'ясом": 'Georgian dumplings with meat',
    'Італійський кавовий десерт': 'Italian coffee dessert',
    'Італійський хліб': 'Italian bread',
    'Свіжий чорний хліб': 'Fresh rye bread',
    'Вреп з куркою та овочами': 'Wrap with chicken and vegetables',
    'Круасан': 'Croissant',
    'Заварне тістечко': 'Choux pastry',
    "Смажене м'ясо": 'Roasted meat',
    'Класична піца з томатами та моцарелою': 'Classic pizza with tomatoes and mozzarella',
    'Булочка з корицею': 'Cinnamon roll',
    'Традиційний український борщ': 'Traditional Ukrainian borscht'
}

cyrillic = re.compile(r'[\u0400-\u04FF]')

for item in MenuItem.objects.all():
    changed = False
    if cyrillic.search(item.name):
        item.name = name_map.get(item.name, 'Legacy Item ' + str(item.id))
        changed = True
    if item.description and cyrillic.search(item.description):
        item.description = desc_map.get(item.description, 'Translated description.')
        changed = True
    
    if changed:
        item.save()

print('Done translating.')
