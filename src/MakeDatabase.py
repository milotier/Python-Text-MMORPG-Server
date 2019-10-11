import lmdb
from ast import literal_eval
from struct import pack
from json import load
from sys import exit

env = lmdb.open('../GameDatabase', map_size=1000000, max_dbs=20)

with open('../GameData.json') as GameData:
    GameData = load(GameData)

if 'coordinates' not in GameData:
    print('Coordinates are missing from the GameData file.')
    print('Please be sure to add coordinates to the GameData file.')
    exit()
elif 'static fields' not in GameData:
    print('Static fields are missing from the GameData file.')
    print('Please be sure to add static fields to the GameData file.')
    exit()
elif 'items' not in GameData:
    print('Items are missing from the GameData file.')
    print('Please be sure to add items to the GameData file.')
    exit()
elif 'item locations' not in GameData:
    print('Item locations are missing from the GameData file.')
    print('Please be sure to add item locations to the GameData file.')
    exit()


coordinates = GameData['coordinates']
coordNum = len(coordinates)

staticWorld = GameData['static fields']
staticFieldNum = len(staticWorld)
itemLocations = GameData['item locations']
itemLocationNum = len(itemLocations)
items = GameData['items']

newStaticWorld = {}
for field in staticWorld:
    if type(field) != str:
        print('Invalid coordinates', ' '.join(field), 'found in static fields')
        exit()
    fieldValue = bytes(repr(staticWorld[field]).encode())
    field = field.split(' ')
    try:
        field = list(map(int, field))
    except ValueError:
        print('Invalid coordinates', ' '.join(field), 'found in static fields')
        exit()
    if field not in coordinates:
        print('Coordinates', field, 'found in static fields, but not in coordinates.')
        exit()
    if len(field) == 3:
        field = pack('III', *field)
    else:
        print('Coordinates', field, 'found in static fields. Coordinates must be 3 long.')
        exit()
    newStaticWorld[field] = fieldValue


newItemLocations = {}
for field in itemLocations:
    if type(field) != str:
        print('Invalid coordinates', ' '.join(field), 'found in item locations')
        exit()
    fieldValue = bytes(repr(itemLocations[field]).encode())
    field = field.split(' ')
    try:
        field = list(map(int, field))
    except ValueError:
        print('Invalid coordinates', ' '.join(field), 'found in item locations')
        exit()
    if field not in coordinates:
        print('Coordinates', field, 'found in item locations, but not in coordinates.')
        exit()
    if len(field) == 3:
        field = pack('III', *field)
    else:
        print('Coordinates', field, 'found in item locations. Coordinates must be 3 long.')
        exit()
    newItemLocations[field] = fieldValue

newItems = {}
for item in items:
    itemValue = bytes(repr(items[item]).encode())
    try:
        item = int(item)
        item = pack('I', item)
    except ValueError:
        print('Specified item number', item, 'is not a number.')
        exit()
    newItems[item] = itemValue

newCoordinates = []
for coords in coordinates:
    oldCoords = coordinates[coordinates.index(coords)]
    if type(coords) != list or \
       len(coords) != 3:
        print('Coordinates', coords, 'found in coordinates. Coordinates must be 3 long.')
        exit()
    if pack('III', *coords) not in newStaticWorld:
        print('Coordinates', coords, 'not found in static fields')
        exit()
    if pack('III', *coords) not in newItemLocations:
        print('Warning: coordinates', coords, 'not found in item locations')
        newItemLocations[pack('III', *coords)] = []
    newCoords = pack('III', *oldCoords)
    newCoordinates.append(newCoords)

staticWorldDB = env.open_db(bytes('StaticWorld'.encode()))
txn = env.begin(staticWorldDB, write=True)
for field in newStaticWorld:
    txn.put(field, newStaticWorld[field])
txn.commit()

itemLocationDB = env.open_db(bytes('ItemLocations'.encode()))
txn = env.begin(itemLocationDB, write=True)
for field in newItemLocations:
    txn.put(field, newItemLocations[field])
txn.commit()

itemDB = env.open_db(bytes('Items'.encode()))
txn = env.begin(itemDB, write=True)
for item in newItems:
    txn.put(item, newItems[item])
txn.commit()

characterLocationDB = env.open_db(bytes('CharacterLocations'.encode()))
txn = env.begin(characterLocationDB, write=True)
value = bytes(repr([]).encode())
for coord in newCoordinates:
    txn.put(coord, value)
txn.commit()
print('The database has been successfully made.')
