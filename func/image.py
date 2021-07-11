import json
import os
from clss.CharSheet import CharSheet
from PIL import Image, ImageDraw, ImageFont

def test():
    #relative file path for the assets folder
    assetsPath = os.path.abspath("assets")

    #load images needed for compositing
    emptyTemplate = Image.open(assetsPath + "\\empty.png")
    nula = Image.open(assetsPath + "\\nula.png")
    portraitMask = Image.open(assetsPath + "\\portraitMask.png").convert('L')
    
    #composite nula image into template
    composite = emptyTemplate.copy()
    composite.paste(nula, (72, 220), mask=portraitMask)

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


