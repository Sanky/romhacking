#!/usr/bin/python3

# punika is a graphics decompresser for games using the Malias compression,
# roughly designed after LZ77, used in numerous Natsume games.
# Refer to 
# http://wikifang.meowcorp.us/wiki/Wikifang:Telefang_1_Translation_Patch/Malias_compression
# for details.
# punika currently supports Keitai Denjuu Telefang; Medarot 1, 2 and 3; Croc 2.
# punika creates a folder called g and places all game's compressed graphics
# in it raw, so it can be read by your favorite tile editor (Tile Molester, TLP,
# etc.)
# Use the -l option if you want to simply list the locations.
# -- Sanky

import struct
import os
import sys

class InvalidGraphicsError(BaseException):
    pass

def readshort():
    return struct.unpack("<H", rom.read(2))[0]

def readbeshort():
    return struct.unpack(">H", rom.read(2))[0]
    
def readbyte():
    return struct.unpack("<B", rom.read(1))[0]
    
def abspointer(bank, offset):
    return bank*0x4000+offset-0x4000

def decompress(offset):
    rom.seek(offset)
    
    try:
        compressed = readbyte()
        data = bytearray() 
        total = readshort()
        if total > 0:
            if compressed == 0x00:
                for i in range(total):
                    data.append(readbyte())
            else:
                if compressed != 0x01:
                    raise InvalidGraphicsError(compressed)
                while len(data) < total: 
                    modes = readshort()
                    for mode in bin(modes)[2:].zfill(16)[::-1]:
                        if int(mode) == 1:
                            e = rom.read(1)
                            d = rom.read(1)
                            loc = -(struct.unpack("<H", e+d)[0]  & 0x07ff) 
                            num = ((struct.unpack("<B", d)[0] >> 3) & 0x1f) + 0x03 
                            loc += len(data)-1
                            for j in range(num):
                                if loc < 0:
                                    raise InvalidGraphicsError(loc)
                                else:
                                    data.append(data[loc+j])
                        else:
                            data.append(readbyte())
    except (InvalidGraphicsError, struct.error):
        return None, None
                
    return data[:total], compressed
        
graphics = {}


    

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('usage: python3 punika.py rom.gbc (-l)')
    if len(sys.argv) == 3:
        if sys.argv[2] == '-l':
            action = 'list'
    else:
        action = 'extract'
    rom = sys.argv[1]

    if not os.path.exists('g'+os.sep):
        os.makedirs('g')
    
    rom = open(rom, 'rb')
    rom.seek(0x134)
    game = rom.read(8)
    if game == b'TELEFANG':
        rom.seek(0x18000)
        for i in range(0x80):
            bank, target = struct.unpack("<BH", rom.read(3))
            if target > 0x7fff and target < 0xa000:
                graphics[i] = {'target':target, 'bank':bank}
            rom.read(1)
        rom.seek(0x1DE1)
        for i in range(0x80):
            pointer = struct.unpack("<H", rom.read(2))[0]
            if i in graphics:
                if pointer > 0x3fff and pointer < 0x8000:
                    graphics[i]['pointer'] = pointer
                else:
                    del graphics[i]
    elif game == b'MEDAROT ':
        rom.seek(0x10f0)
        for i in range(0x80):
            p = readshort()
            rom.seek(p)
            g = {}
            g['bank'] = readbyte()
            g['pointer'] = readshort()
            g['target'] = readshort()
            if g['target'] > 0x7fff and g['target'] < 0xa000 and g['pointer'] > 0x3fff and g['pointer'] < 0x8000:
                graphics[i] = g
            rom.seek(0x10f0+i*0x2)
    elif game == b'MEDAROT2':
        rom.seek((0x3b*0x4000)+0x282b)
        for i in range(0xff):
            g = {}
            g['bank'] = readbyte()
            g['target'] = readshort()
            rom.seek(0x3a20+(i*0x2))
            g['pointer'] = readshort()
            if g['target'] > 0x7fff and g['target'] < 0xa000 and g['pointer'] > 0x3fff and g['pointer'] < 0x8000:
                graphics[i] = g
            rom.seek((0x3b*0x4000)+0x282b+(i*0x4)+4)
    elif game == b'MEDAROT3':
        rom.seek((0x39*0x4000)+0x306a)
        for i in range(0x1ff):
            g = {}
            g['bank'] = readbyte()
            g['target'] = readshort()
            g['vrambank'] = readbyte()
            rom.seek(0x3995+(i*0x2))
            g['pointer'] = readshort()
            if g['target'] > 0x7fff and g['target'] < 0xa000 and g['pointer'] > 0x3fff and g['pointer'] < 0x8000:
                graphics[i] = g
            rom.seek((0x39*0x4000)+0x306a+(i*0x4)+4)
    elif game == b'MEDAROT5':
        # This is just mugshots.
        rom.seek((0x7b*0x4000)+0x040a)
        for i in range(0xff):
            g = {}
            g['bank'] = readbyte()
            g['pointer'] = readbeshort()
            readbyte()
            readbyte()
            readbyte()
            g['target'] = 0
            graphics[i] = g
    elif game == b'CROC 2\0\0':
        # This game probably sets all offsets manually.  You're on your own here!  Check out RO3F:59F5 for starters.
        graphics = {0:{'bank': 0x3b, 'target': 0x8000, 'vrambank': 0x00, 'pointer': 0x5218},
                    1:{'bank': 0x3d, 'target': 0x9000, 'vrambank': 0x00, 'pointer': 0x5e94},}
    else:
        os.quit('Unsupported ROM.')
    
    if action == 'list':
        locs = {}
        for i, g in graphics.items():
            addr = abspointer(g['bank'], g['pointer'])
            rom.seek(addr)
            compressed = readbyte()
            total = readshort()
            decompress(addr)
            locs[abspointer(g['bank'], g['pointer'])] = rom.tell() - addr
            print ("{:>2x} - bank {:02x}:{:04x} (0x{:>06x}), 0x{:>3x} bytes {} read in {:04x}".format(
            i, g['bank'], g['pointer'], abspointer(g['bank'], g['pointer']), total, "compressed" if compressed else "not compressed", g['target']))
        lastbank = None
        lastend = None
        for loc in sorted(locs.keys()):
            total = locs[loc]
            bank = loc // 0x4000
            if bank == lastbank:
                if loc - lastend != 0:
                    print("{:>4x} bytes between compressed gfx at {:>6x} (bank {:02x})".format(loc-lastend, loc, bank))
            lastbank = bank
            lastend = loc + total
            
    elif action == 'extract':
        for gi, g in graphics.items():
            l = abspointer(g['bank'], g['pointer'])

            data, compressed = decompress(l)

            if data is None:
                print("{} ({}) is invalid!".format(hex(gi), hex(l)))
            elif len(data) == 0:
                print('{} ({}) is blank!'.format(hex(gi), hex(l)))
            else:
                g = open(os.path.join('g', '{}.gb'.format(hex(gi)[2:].zfill(2))), 'wb')
                g.write(data)
                g.close()

                print('{} {} ({})'.format("Decompressed" if compressed else "Exctracted", hex(gi), hex(l)))

    print ("Done..!")
    rom.close()
