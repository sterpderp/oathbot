import json
import os
from clss.CharSheet import CharSheet
from PIL import Image, ImageDraw, ImageFont

def render(charSheet:CharSheet, coordsName:str, attachFP:str):
    assetsPath = os.path.abspath("assets")
    jsonPath = assetsPath + "\\" + coordsName + ".json"
    coords = json.load(open(jsonPath))

    #load assets
    blank               = Image.open(assetsPath + "\\blank.png")
    dash                = Image.open(assetsPath + "\\dash.png")
    dashMask            = Image.open(assetsPath + "\\dash mask.png").convert('L')
    dice                = Image.open(assetsPath + "\\dice.png")
    diceMask            = Image.open(assetsPath + "\\dice mask.png").convert('L')
    emptyLarge          = Image.open(assetsPath + "\\empty big.png")
    emptyLargeMask      = Image.open(assetsPath + "\\empty big mask.png").convert('L')
    emptyMedium         = Image.open(assetsPath + "\\empty medium.png")
    emptyMediumMask     = Image.open(assetsPath + "\\empty medium mask.png").convert('L')
    emptySmall          = Image.open(assetsPath + "\\empty small.png")
    emptySmallMask      = Image.open(assetsPath + "\\empty small mask.png").convert('L')
    pipLarge            = Image.open(assetsPath + "\\pip large.png")
    pipLargeRed         = Image.open(assetsPath + "\\pip large red.png")
    pipLargeMask        = Image.open(assetsPath + "\\pip large mask.png").convert('L')
    pipMedium           = Image.open(assetsPath + "\\pip medium.png")
    pipMediumRedLight   = Image.open(assetsPath + "\\pip medium red light.png")
    pipMediumRedDark    = Image.open(assetsPath + "\\pip medium red dark.png")
    pipMediumMask       = Image.open(assetsPath + "\\pip medium mask.png").convert('L')
    pipSmall            = Image.open(assetsPath + "\\pip small.png")
    pipSmallMask        = Image.open(assetsPath + "\\pip small mask.png").convert('L')
    portraitMask        = Image.open(assetsPath + "\\portrait mask.png").convert('L')

    if attachFP != "":
        portrait = Image.open(attachFP)
    else:
        portrait = Image.open(assetsPath + "\\portrait mask.png")

    if portrait.width != portraitMask.width or portrait.height != portraitMask.height:
        portrait = portrait.resize((portraitMask.width, portraitMask.height))

    composite = blank.copy()

    #name
    pasteText(composite, charSheet.char_name, coords["title"], coords["titlewidth"], coords["titlefontsize"], assetsPath)

    #portrait
    composite.paste(portrait, strToTuple(coords["portrait"]), mask=portraitMask)

    #skills
    skills = ["Hunt", "Study", "Survey", "Tinker", "Finesse", "Prowl", "Skirmish", "Wreck", "Aether", "Command", "Consort", "Sway"]
    for skill in skills:
        pastePipList(composite, charSheet.skills[skill], coords[skill.lower()], pipSmall, pipSmallMask, emptySmall, emptySmallMask)

    #stress
    pastePipList(composite, charSheet.stress, coords["stress"], pipMedium, pipMediumMask, emptyMedium, emptyMediumMask)

    #harm
    harms = charSheet.harm.keys()
    harmText = coords["harmtext"]
    harmDash = coords["harmdash"]
    harmWidth = coords["harmwidth"]
    harmFontSize = coords["harmfontsize"]
    slots = []
    for i in range(len(harmText)):
        slots.append(True)

    #try to fill the 2 slots one after the other
    for harm in harms:
        level = charSheet.harm[harm] - 1
        for i in range(2):
            index = (level*2) + i
            if index < len(slots) and slots[index]:
                slots[index] = False
                pasteText(composite, harm, harmText[index], harmWidth, harmFontSize, assetsPath)
                break

    #draw dash anywhere a harm was not drawn
    for i in range(len(slots)):
        if slots[i] == True:
            composite.paste(dash, strToTuple(harmDash[i]), mask=dashMask)

    #trauma
    trauma = charSheet.trauma
    traumaPips = coords["trauma"]
    traumaText = coords["traumatext"]
    traumaDash = coords["traumadash"]
    traumaWidth = coords["traumawidth"]
    traumaFontSize = coords["traumafontsize"]
    counter = 0
    traumaPip = [pipSmall, pipMediumRedLight, pipMediumRedDark, pipLargeRed]
    traumaPipMasks = [pipSmallMask, pipMediumMask, pipMediumMask, pipLargeMask]
    traumaEmpty = [emptySmall, emptyMedium, emptyMedium, emptyLarge]
    traumaEmptyMasks = [emptySmallMask, emptyMediumMask, emptyMediumMask, emptyLargeMask]

    #for every listed trauma, paste the text and the full pip
    for t in trauma:
        pasteText(composite, t, traumaText[counter], traumaWidth, traumaFontSize, assetsPath)
        composite.paste(traumaPip[counter], strToTuple(traumaPips[counter]), mask=traumaPipMasks[counter])
        counter += 1

    #for every empty slot, draw a dash and an empty pip
    while counter < 4:
        composite.paste(dash, strToTuple(traumaDash[counter]), mask=dashMask)
        composite.paste(traumaEmpty[counter], strToTuple(traumaPips[counter]), mask=traumaEmptyMasks[counter])
        counter += 1

    #rerolls
    rerolls = charSheet.rerolls
    categories = ["Insight", "Prowess", "Resolve"]
    anyValue = 0

    #Any represents a crit on reroll, and will show up in all 3 skill categories
    if "Any" in rerolls and rerolls["Any"] > 0:
        anyValue = rerolls["Any"]

    #for each skill category, render the dice one by one
    for category in categories:
        if anyValue > 0:
            rerollCoords = coords[category.lower()]
            counter = 0
            for coord in rerollCoords:
                if counter < anyValue:
                    composite.paste(dice, strToTuple(coord), mask=diceMask)
                    counter += 1
        elif category in rerolls and rerolls[category] > 0:
            rerollCoords = coords[category.lower()]
            rerollValue = rerolls[category]
            counter=0
            for coord in rerollCoords:
                if counter < rerollValue:
                    composite.paste(dice, strToTuple(coord), mask=diceMask)
                    counter+=1
        
    
    

    imagePath = assetsPath + "\\composite.png"
    composite.save(imagePath, format='png')

    return imagePath

def pastePipList(image, stat, pipList, pipFull, pipFullMask, pipEmpty, pipEmptyMask):
    counter = 0
    for pip in pipList:
        if counter < stat:
            image.paste(pipFull, strToTuple(pip), mask=pipFullMask)
        else:
            image.paste(pipEmpty, strToTuple(pip), mask=pipEmptyMask)
        counter += 1

def pasteText(image, text, point, width, fontsize, assetsPath):
    fontSize, originalH = generateFontSize(text, width, fontsize, assetsPath)
    minFont = ImageFont.truetype(assetsPath + "\\minion.otf", fontSize)
    W, H = strToTuple(point)
    draw = ImageDraw.Draw(image)
    w, h = minFont.getsize(text)
    #offset draw point start by half of the text's width (center justify) and down a small factor for its height, if the font size was lowered
    draw.text((W - w/2, H + (originalH - h)/2), text, fill='black', font=minFont)

def generateFontSize(text, maxWidth, baseFontSize, assetsPath) -> (int, int):
    minionFont = ImageFont.truetype(assetsPath + "\\minion.otf", baseFontSize)
    w, h = minionFont.getsize(text)
    fontSize = baseFontSize
    originalH = h

    while w > maxWidth and fontSize > 1:
        fontSize -= 1
        minionFont = ImageFont.truetype(assetsPath + "\\minion.otf", fontSize)
        w, h = minionFont.getsize(text)

    return (fontSize, originalH)

def test():
    #relative file path for the assets folder
    assetsPath = os.path.abspath("assets")

    #load images needed for compositing
    emptyTemplate = Image.open(assetsPath + "\\empty.png")
    nula = Image.open(assetsPath + "\\towernula.png")
    portraitMask = Image.open(assetsPath + "\\mask.png").convert('L')
    
    #composite nula image into template
    composite = emptyTemplate.copy()
    composite.paste(nula, (114, 204), mask=portraitMask)

    #text generation
    name = "Nula Pepper"
    maxWidth = 550
    fontSize = 62
    minionFont = ImageFont.truetype(assetsPath + "\\minion.otf", fontSize)
    w, h = minionFont.getsize(name)
    originalH = h

    #if name entered is too big, scale down the font size until it is not! 
    while w > maxWidth and fontSize > 1:
        fontSize -= 1
        minionFont = ImageFont.truetype(assetsPath + "\\minion.otf", fontSize)
        w, h = minionFont.getsize(name)

    W, H = (578, 35) #default centerpoint for the text
    draw = ImageDraw.Draw(composite)
    #offset draw point start by half of the text's width (center justify) and down a small factor for its height, if the font size was lowered
    draw.text((W - w/2, H + (originalH - h)/2), name, fill='black', font=minionFont)

    #save composite and return path to it
    imagePath = assetsPath + "\\composite.png"
    composite.save(imagePath, format='png')

    return imagePath

def strToTuple(s : str) -> (int, int):
    split = s.split(",")
    return (int(split[0]), int(split[1]))
