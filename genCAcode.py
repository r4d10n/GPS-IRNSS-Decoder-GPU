G1 = []
G2 = []
CA = []

# GPS L2
GPS_G2CodePhase = [(2,6),(3,7),(4,8),(5,9),(1,9),(2,10),(1,8),(2,9),(3,10),(2,3),(3,4),(5,6),(6,7),(7,8),(8,9),(9,10),(1,4),(2,5),(3,6),(4,7),(5,8),(6,9),(1,3),(4,6),(5,7),(6,8),(7,9),(8,10),(1,6),(2,7),(3,8),(4,9),(5,10),(4,10),(1,7),(2,8),(4,10)]
GPS_OctalChips = [0o1440, 0o1620, 0o1710, 0o1744, 0o1133, 0o1455, 0o1131, 0o1454, 0o1626, 0o1504, 0o1642, 0o1750, 0o1764, 0o1772, 0o1775, 0o1776, 0o1156, 0o1467, 0o1633, 0o1715, 0o1746, 0o1763, 0o1063, 0o1706, 0o1743, 0o1761, 0o1770, 0o1774, 0o1127, 0o1453, 0o1625, 0o1712, 0o1745, 0o1713, 0o1134, 0o1456, 0o1713]

# IRNSS L5 SPS
IRNSS_G2Init = [0b1110100111,0b0000100110,0b1000110100,0b0101110010,0b1110110000,0b0001101011,0b0000010100,0b0100110000,0b0010011000,0b1101100100,0b0001001100,0b1101111100,0b1011010010,0b0111101010]
IRNSS_OctalChips = [0o0130,0o1731,0o0713,0o1215,0o0117,0o1624,0o1753,0o1317,0o1547,0o0233,0o1663,0o0203,0o0455,0o1025]

Constellation = "GPS"
SVcount = len(GPS_G2CodePhase)
#Constellation = "IRNSS"
#SVcount = len(IRNSS_G2Init)

def _G1(index): return G1[index-1]
def _G2(index): return G2[index-1]

def revbits(bits): return int('{:010b}'.format(bits)[::-1], 2)

def shiftG1():
    global G1
    G1.insert(0,(_G1(3) + _G1(10)) % 2) # G1 = 1 (+) X^3 (+) X^10
    return G1.pop()

def shiftG2(SatID):
    global G2

    if (Constellation == "GPS"):
        g2 = ((_G2(GPS_G2CodePhase[SatID][0]) + _G2(GPS_G2CodePhase[SatID][1])) % 2)
        G2.insert(0,(_G2(2) + _G2(3) + _G2(6) + _G2(8) + _G2(9) + _G2(10)) % 2) # G2 = 1 (+) X^10 (+) X^9 (+) X^8 (+) X^6 (+) X^3 (+) X^2
        G2.pop()
        return g2

    if (Constellation == "IRNSS"):
        G2.insert(0,(_G2(2) + _G2(3) + _G2(6) + _G2(8) + _G2(9) + _G2(10)) % 2) # G2 = 1 (+) X^10 (+) X^9 (+) X^8 (+) X^6 (+) X^3 (+) X^2
        return G2.pop()

def genCA(SatID, nrz = True, sampsPerChip = 16):
    global G1, G2, CA

    G1 = [1 for n in range(10)]
    if (Constellation == "GPS"): G2 = [1 for n in range(10)]
    if (Constellation == "IRNSS"): G2 = [int(d) for d in f'{revbits(IRNSS_G2Init[SatID-1]):011b}']

    CA = []

    for i in range(1023):
        g1 = shiftG1()
        g2 = shiftG2(SatID-1)

        ca = (g1 + g2) % 2
        if (nrz and ca == 0): ca = -1
        CA.extend([ca] * sampsPerChip)

        # binCA = ''.join(map(str,CA[:10]))
        # octCA = oct(int(binCA,2))

        # print(str(i) + '\tg1: ' + str(g1) + "-" + ''.join(map(str,G1)) + '\tg2: ' + str(g2) + "-" + ''.join(map(str,G2)) + '\toc: ' + oct(IRNSS_OctalChips[SatID-1]) + '\t' + bin(IRNSS_OctalChips[SatID-1])  + '\tca:' + str(ca) + '\tCA:' + binCA + '\t' + octCA )
        # if (i==10): return CA

    return CA

def verifyCA(SatID,CA):
    binCA = ''.join(map(str,CA[:10]))
    octCA = oct(int(binCA,2))

    print(binCA + " " + octCA + " " +oct(IRNSS_OctalChips[SatID-1]))

    if (Constellation == "GPS" and octCA == oct(GPS_OctalChips[SatID-1])):
        print (str(octCA) + " - Octal Chip Check Verified for GPS SatID " + str(SatID))
    if (Constellation == "IRNSS" and octCA == oct(IRNSS_OctalChips[SatID-1])):
        print (str(octCA) + " - Octal Chip Check Verified for IRNSS SatID " + str(SatID))

if __name__ == '__main__':
    for i in range(1,SVcount+1):
        print("*** sv: " +  str(i))
        CA = genCA(i, False, 1)
        verifyCA(i, CA)