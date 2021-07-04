G1 = []
G2 = []
CA = []

G2CodePhase = [(2,6),(3,7),(4,8),(5,9),(1,9),(2,10),(1,8),(2,9),(3,10),(2,3),(3,4),(5,6),(6,7),(7,8),(8,9),(9,10),(1,4),(2,5),(3,6),(4,7),(5,8),(6,9),(1,3),(4,6),(5,7),(6,8),(7,9),(8,10),(1,6),(2,7),(3,8),(4,9),(5,10),(4,10),(1,7),(2,8),(4,10)]
OctalChips = [0o1440, 0o1620, 0o1710, 0o1744, 0o1133, 0o1455, 0o1131, 0o1454, 0o1626, 0o1504, 0o1642, 0o1750, 0o1764, 0o1772, 0o1775, 0o1776, 0o1156, 0o1467, 0o1633, 0o1715, 0o1746, 0o1763, 0o1063, 0o1706, 0o1743, 0o1761, 0o1770, 0o1774, 0o1127, 0o1453, 0o1625, 0o1712, 0o1745, 0o1713, 0o1134, 0o1456, 0o1713]

def shiftG1():
    global G1
    G1.insert(0,(G1[3-1] + G1[10-1]) % 2)
    return G1.pop()

def shiftG2(SatID):
    global G2
    g2 = ((G2[(G2CodePhase[SatID][0]-1)] + G2[(G2CodePhase[SatID][1]-1)]) % 2)
    G2.insert(0,(G2[2-1] + G2[3-1] + G2[6-1] + G2[8-1] + G2[9-1] + G2[10-1]) % 2)
    G2.pop()
    return g2

def genCA(SatID):
    global G1, G2, CA

    G1 =[1 for n in range(10)]
    G2 =[1 for n in range(10)]
    CA = []

    for i in range(1030):
        g1 = shiftG1()
        g2 = shiftG2(SatID-1)

        ca = (g1 + g2) % 2
        CA.append(ca)

    #print ("code_sv_" + str(SatID) + "=" + str(CA))

    #     binCA = ''.join(map(str,CA))
    #     octCA = oct(int(binCA,2))

    # print(str(i) + '\t' + str(ca) + '\t' + str(g1) + "-" + ''.join(map(str,G1)) + '\t' + str(g2) + "-" + ''.join(map(str,G2)) + '\t' + binCA + '\t\t\t' + octCA)

        # if (i == 10-1 and octCA == oct(OctalChips[SatID-1])):
        #         print (str(octCA) + " - Octal Chip Check Verified for SatID " + str(SatID))
        #         return

    return CA

#for i in range(1,38):
#    genCA(i)