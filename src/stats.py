import struct
from datetime import datetime
from data import *

def checkShiny(pid, otid, secid):
    pida = pid >> 16
    pidb = pid & 0xffff
    ids = otid ^ secid
    pids = pida ^ pidb
    return (ids ^ pids) < 8
    
def checkIVs(b):
    ivs = b[0] + (b[1] << 8) + (b[2] << 16) + (b[3] << 24)
    hp =  (ivs & 0x0000001f)
    atk = (ivs & 0x000003e0) >> 5
    df =  (ivs & 0x00007c00) >> 10
    spe = (ivs & 0x000f8000) >> 15
    spa = (ivs & 0x01f00000) >> 20
    spd = (ivs & 0x3e000000) >> 25
    return (hp, atk, df, spa, spd, spe)

def checkEVs(b):
    hp = b[0]
    atk = b[1]
    df = b[2]
    spe = b[3]
    spa = b[4]
    spd = b[5]
    total = hp + atk + df + spe + spa + spd
    return (hp, atk, df, spa, spd, spe, total)

def statSetup(p, pk6, filePath):
    # For reading the hex values and creating a coherent printout
    pid = p[0x18] + (p[0x19] << 8) + (p[0x1a] << 16) + (p[0x1b] << 24)
    nickname = ''
    if p[0x41] != 0:
        nickname = 'Invalid nickname'
    else:
        for i in pk6[0x40:0x58]:
            if i == '\xff': break
            if i != '\x00': nickname += i
    lv = p[0xec]
    nat = getNature(ord(pk6[0x1c]))
    spec = getSpecies((p[0x09] << 8) + p[0x08])
    abil = getAbility(p[0x14])
    if p[0x1d] & 4:
        gender = '(Genderless)'
    elif p[0x1d] & 2:
        gender = '(Female)'
    else: gender = '(Male)'
    otName = ''
    if p[0xb1] != 0:
        otName = 'TRAINER'
    else:
        for i in pk6[0xb0:0xc8]:
            if i == '\xff': break
            if i != '\x00': otName += i
    otID = (p[0x0d] << 8) + p[0x0c]
    secID = (p[0x0f] << 8) + p[0x0e]
    held = getItem((p[0x0b] << 8) + p[0x0a])
    ivs = checkIVs(p[0x74:0x78])
    evs = checkEVs(p[0x1e:0x24])
    atk = checkAttacks(p[0x5A:0x62])
    hidden = checkHiddenPower(ivs)
    happyOT = p[0xca]
    affectionOT = p[0xcb]
    if p[0xDD] & 128:
        genderOT = 'F'
    else:
        genderOT = 'M'
    shiny = checkShiny(pid, otID, secID)
    if shiny: shiny = 'SHINY'
    else: shiny = ''
    origin = getGame(p[0xdf])
    # Incomplete data dictionaries, so these will return None in some cases
    country = getCountry(p[0xe0])
    region = getRegion(p[0xe0], p[0xe1])
    threedsOrigin = getThreeds(p[0xe2])
    otLanguage = getLanguage(p[0xe3])
    
    if p[0x93] == 1:
        happyNotOT = p[0xa2]
        affectionNotOT = p[0xa3]
        if p[0x92]:
            genderNotOT = 'F'
        else:
            genderNotOT = 'M'
        currentT = ''
        if p[0x79] != 0:
            currentT = 'TRAINER'
        else:
            for i in pk6[0x78:0x90]:
                if i == '\xff': break
                if i != '\x00': currentT += i
                
    timetaken = str(datetime.now())[:-7]
    
    s = '"%s" (%s from %s)\n    ' % (nickname, timetaken, filePath)
    s += 'Lv %d %s %s %s\n    ' % (lv, shiny, spec, gender)
    s += 'Nature: %s,  Ability: %s\n    ' % (nat, abil)
    s += 'Holding: %s, Hidden Power: %s-type\n\n    ' % (held, hidden)
    
    s += 'Game of origin: %7s, PID: %d\n    ' % (origin, pid)
    if region != None: s += 'Country: %13s, Region: %s\n    ' % (country, region)
    else: s += 'Country: %13s\n    ' % country
    s += '3DS Region: %s, OT Language: %8s\n    ' % (threedsOrigin, otLanguage)
    s += 'OT: %7s (%s), ID: %05d, SecID: %05d\n    ' % (otName, genderOT, otID, secID)
    s += 'Happiness: %3d, Affection: %3d\n\n    ' % (happyOT, affectionOT)
    if p[0x93] == 1: # In the case that the current trainer is not the OT
        s += 'Current Trainer: %7s (%s)\n    ' % (currentT, genderNotOT)
        s += 'Happiness: %3d, Affection: %3d\n\n    ' % (happyNotOT, affectionNotOT)
    
    s += 'Attacks: %-12s %-12s\n             %-12s %-12s\n\n    ' % atk
    
    s += 'IVs: HP %3d, Atk %3d, Def %3d, SpA %3d, SpD %3d, Spe %3d\n    ' % ivs
    s += 'EVs: HP %3d, Atk %3d, Def %3d, SpA %3d, SpD %3d, Spe %3d, Total %d\n' % evs
    return s
    
def errorReadout(errorMessage):
    errorBar = '!' * (len(errorMessage) + 8)
    return "\n    %s\n    !!! %s !!!\n    %s\n" % (errorBar, errorMessage, errorBar)

def statAnalyze(p, filePath):
    # For interpreting hex values to determine legitimacy
    a = ''
    
    csum = struct.unpack('<6s1H', open(filePath, 'rb').read(8))[1]
    fcsum = struct.unpack(">I", struct.pack("<I", csum))[0]
    fcsum = ("%02x" % fcsum)[:-4]
    csum = struct.unpack(">I", struct.pack(">I", csum))[0]

    words = struct.unpack('<8s112H', open(filePath, 'rb').read(232))[1:]
    lilesum = sum(words) & 65535
    bigesum = struct.unpack(">I", struct.pack("<I", lilesum))[0]
    calcsum = ("%02x" % bigesum)[:-4]
    
    displaycalcsum = calcsum[:2] + ' ' + calcsum[2:]
    displayfcsum = fcsum[:2] + ' ' + fcsum[2:]
    
    if lilesum != csum:
    	a += errorReadout("File's checksum is incorrect (%s), should be %s." % (displayfcsum, displaycalcsum))
    
    ivs = checkIVs(p[0x74:0x78])
    evs = checkEVs(p[0x1e:0x24])
    
    if ivs[0] + ivs[1] + ivs[2]+ ivs[3]+ ivs[4]+ ivs[5] == (6 * 31):
        a += "\n    ! IVs are perfect, could be RNG abused or hacked. !"
    elif ivs[0] + ivs[1] + ivs[2]+ ivs[3]+ ivs[4]+ ivs[5] > (6 * 31):
        a += errorReadout("IVs are too high, none can exceed 31.")
    
    if evs[0] + evs[1] + evs[2]+ evs[3]+ evs[4]+ evs[5] == 508:
        a += "\n    ! Total EVs exactly 508. !"
    elif evs[0] + evs[1] + evs[2]+ evs[3]+ evs[4]+ evs[5] == 510:
        a += "\n    ! Total EVs exactly 510. !"
    elif evs[0] + evs[1] + evs[2]+ evs[3]+ evs[4]+ evs[5] >= 511:
        a += errorReadout("\nTotal EVs over 510, too high.")
        
    if (p[0x0f] << 8) + p[0x0e] == 0:
        a += "\n    ! Secret ID is zero, could be an event Pokemon. !"
    
    if p[0xdf] == 0:
        a += errorReadout('\n    ! Game of origin not set. !')
        
    return a

def statLog(s):
    # For logging the printout to a log file
    print 'Writing stats to statlog.txt... '
    s += '\n'
    s += ('=' * 80) + '\n\n'
    with open('statlog.txt', 'a') as f:
        f.write(s)
    print '    Done.'
