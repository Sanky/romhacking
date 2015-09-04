#!/usr/bin/python3

MAP_NAMES = """Diagon Alley
Cauldron Shop
Apothecary
Owl Shop
Wand Shop
Book Shop
Robe Shop
Sweets Shop
Gringotts Entrance
Gringotts Dungeon 1
Crossing the Lake
Hogwarts Dungeon 1
Hogwarts Dungeon 2
Hogwarts Dungeon 3
Hogwarts Express
Ancient Runes classroom
Arithmacy classroom
Armor Gallery
Astronomy Classroom
Bed Pan Room
Broom Shop
Charms Classroom
Dark Arts Classroom
Mirror of Erised
Forbidden Forest 1
Forbidden Forest 2
Forbidden Forest 3
Forbidden Forest 4
Forbidden Forest 5
Forbidden Forest 6
Final Dungeon 1
Final Dungeon 2
Final Dungeon 3
Final Dungeon 4
Final Dungeon 5
Final Dungeon 6
Flitwick's Office
Empty Class
Empty Class
Forbidden Hallway
Greenhouse
Girls' Bathroom
Hogwarts Main Grounds 1
Hagrid's Hut Interior
Floor 1 Hallway
Floor 2 Hallway
Floor 3 Hallway
Floor 4 Hallway
Floor 5 Hallway
Floor 6 Hallway
Floor 7 Hallway
Healer's Shop
History of Magic class
Hospital Ward
Library 1
Library 2
McGonagall's Office
Muggle Studies class
Pomfrey's Office
Potions classroom
Quirrell's office
Snape's office
Sprout's office
Storeroom
Transfiguration class
Trophy Room
Gringotts Dungeon 2
Platform 9 3/4
Lake Shore
Hogwarts Entrance Hall
Gryffindor boys' dorm
Gryffindor Common Room
Broom Cupboard
Filch's Office
Hogwarts Great Hall
Hogwarts Staff Room
Portrait Room
Floor 0 Dungeons
Potion 2
Gringotts Vault
Astronomy Corridor
Hogwarts Main Grounds 2
Hogwarts Main Grounds 3
Hogwarts Main Grounds 4
Hagrid's Hut Exterior
Card Trading Club
Great Hall - Empty
Muggle Secret Room
Writing Supplies
Boys' Bathroom
Muggle Music Class
Muggle Art Class
Card Vault
6th Floor Secret Hallway
Binns' Office
Empty Class""".split('\n')

rom = open("hp1.gbc", "rb")

class NotPointerException(ValueError): pass

def readpointer(bank=None):
    if not bank: bank = rom.tell()/0x4000
    s = readshort()
    if 0x4000 > s or 0x8000 <= s:
        raise NotPointerException(s)
    return (bank * 0x4000) + (s - 0x4000)

def readshort():
    return readbyte() + (readbyte() << 8)

def readbyte():
    return ord(rom.read(1))

map_groups = []
for i, map_name in enumerate(MAP_NAMES):
    print("{}:".format(map_name))
    groups = []
    for j in range(4):
        group = []
        rom.seek((3*0x4000)+0x214e+i*2)
        rom.seek(readpointer()+j*2)
        rom.seek(readpointer())
        group.append(readbyte())
        group.append(readbyte())
        group.append(readbyte())
        groups.append(group)
    map_groups.append(groups)
    print(" {}".format(groups))

#for map_name, groups in zip(MAP_NAMES, map_groups):
#    print("{} groups:".format(map_name))
#    print(" {}".format(groups))
    




