from PIL import Image
from PIL import ImageFilter, ImageDraw, ImageFont
from random import randint,choice,random
from sys import stdout
from tweepy import *
import os
import time
class Painter(object):
    def __init__(self):
        self.val = 5
        self.lowThreshold = 100
        self.imageWidth = 1940
        self.imageHeight = 1080
        self.last_image = None
        self.monochrome = False
        self.buffer = 20
        self.speed = 0
        self.max_speed = 0
        self.last_start = (0,0,0)
        self.last_suit = "fool.PNG"
        self.api = None
        f = open("number.txt","r")
        fileNumber = f.read()
        f.close()
        self.file_number = int(fileNumber) - 1
        self.tarot_symbols = os.listdir("symbology");
    def set_monochrome(self, boolean):
            self.monochrome = boolean
    def set_speed(self, speed):
        self.max_speed = speed
        self.speed = speed
    def get_last_image(self):
            return self.last_image
    def delete_last_image(self):
        filename = "Painting " + str(self.file_number) + ".jpg"
        try:
            os.remove(filename)
        except OSError:
            pass
        f = open("number.txt","r")
        fileNumber = f.read()
        f.close()
        f = open("number.txt","w")
        f.write(str(int(fileNumber) - 1))
        self.file_number += 1
        f.close()
    def randomise(self, lst):
        # adds/subtracts a value within the range val to each channel
        # also check that this does not exceed the extrema (0,255)
        if self.speed > 0:
            self.speed -= 1
            return lst
        self.speed = self.max_speed
        for c in [0,1,2]:
            randVal = int(random()*(self.val+1))
            if lst[c] + randVal > 255:
                lst[c] -= randVal
            elif lst[c] - randVal < 0:
                lst[c] += randVal
            else:
                lst[c] += [-randVal,randVal][int(random()*2)]
        return lst
    def set_val(self, integer):
        self.val = integer

    def set_low_threshold(self, integer):
        self.lowThreshold = integer

    def set_dimensions(self, width,height):
        self.set_width(width)
        self.set_height(height)

    def set_width(self, width):
        self.imageWidth = width+self.buffer

    def set_height(self, height):
        self.imageHeight = height

    def generate_image_and_show(self, starting_colour = None, randomiseStart = False):
        self.generate_image(starting_colour, randomiseStart)
        self.get_last_image().show()
        
    def generate_image(self, starting_colour = None, randomiseStart = False):
        image = Image.new("RGB", (self.imageWidth,self.imageHeight))
        print("Painting...\n")
        pixdata = image.getdata()
        pixdata_a = pixdata.pixel_access()
        tick = (image.size[0] * image.size[1]) // 50
        iteration = 0
        print("0% |" + (49 * " ") + "| 100%")
        stdout.write("   |")
        newColours = []
        startingColour = (randint(0,255),randint(0,255),randint(0,255))
        if starting_colour is None:
            while sum(startingColour) < self.lowThreshold:
                startingColour = (randint(0,255),randint(0,255),randint(0,255))
        else:
            startingColour = starting_colour
            if randomiseStart:
                startingColour = self.randomise(startingColour)
        self.last_start = startingColour
        choices = [(-1,-1),(-1,1),(-1,0), (-1,2), (-1,-2)]
        for x in range(image.size[0]):
            for y in range(image.size[1]):
                other = []
                above = []
                left = []
                
                iteration += 1
                if iteration % tick == 0:
                    stdout.write("|")
                    
                co = (x,y)
                if co == (0,0):
                    
                    pixdata_a[x,y]=startingColour
                    continue
                start = time.clock()
                if y != 0:
                    above = list(pixdata_a[x,y-1])
                    above = self.randomise(above)

                if x != 0:
                    left = list(pixdata_a[x-1,y])
                    left = self.randomise(left)
                    
                if x > 2 and y > 2 and y + 2 < image.size[1]:
                    ch = choices[int(random() * 5)]
                    other = list(pixdata_a[x+ch[0],y+ch[1]])
                    other = self.randomise(other)
                if other:
                    newPixel = other
                    while sum(newPixel) < self.lowThreshold:
                        if self.monochrome:
                            newPixel = self.randomise(list(startingColour))
                        else:
                            newPixel = [randint(0,255),randint(0,255),randint(0,255)]
                    pixdata_a[x,y]=tuple(newPixel)
                elif left and above:
                    newPixel = []
                    for i in range(3):
                        newPixel.append((above[i] + left[i]) // 2)
                    while sum(newPixel) < self.lowThreshold:
                        if self.monochrome:
                            newPixel = self.randomise(list(startingColour))
                        else:
                            newPixel = [randint(0,255),randint(0,255),randint(0,255)]
                    pixdata_a[x,y]=tuple(newPixel)
                elif above:
                    pixdata_a[x,y]=tuple(above)
                else:
                    pixdata_a[x,y]=tuple(left)
                start = time.clock()
        image.putdata(pixdata)
        image = image.filter(ImageFilter.GaussianBlur(1))
        image = image.filter(ImageFilter.SHARPEN)
        image = image.crop((self.buffer,0, self.imageWidth,self.imageHeight))
        f = open("number.txt","r")
        fileNumber = f.read()
        f.close()
        f = open("number.txt","w")
        f.write(str(int(fileNumber) + 1))
        self.file_number += 1
        f.close()

        image.save("Painting " + fileNumber + ".jpg")
        print("\n\nDone")
        self.last_image = image
    def tarot_card(self, number = 1,suit=None,start_colour=None):
        painter.set_dimensions(900,1500)
        painter.set_speed(10)
        painter.set_val(1)
        painter.set_monochrome(True)
        if suit is None or suit not in self.tarot_symbols:
            suit = choice(self.tarot_symbols)
        image = Image.open(os.path.join("symbology", suit))
        self.last_suit = suit
        painter.generate_image(start_colour)
        self.color_tarot_symbol(image)
        card = painter.get_last_image()
        marginx = card.width*0.1
        marginy = card.height*0.1
        if number > 1 and number < 11:
            ratio = min((card.width/6)/image.width, (card.height/6)/image.height)
        else:
            ratio = min((card.width/3)/image.width, (card.height/3)/image.height)
        image = image.resize((round(image.width*ratio),round(image.height*ratio)))
        for i in range(number):
            n = i+1
            location = self.get_symbol_location(number,n,card,image)
            card.paste(image,location,image)
            if number > 10:
                break
        card = self.add_suit_text(card, number, suit)
        
        self.delete_last_image()
        return card
    def add_suit_text(self, card, number, suit):
        txt = Image.new('RGBA', card.size, (255,255,255,0))
        fnt = ImageFont.truetype('fonts/Crushed/Crushed-Regular.ttf', 80)
        d = ImageDraw.Draw(txt)
        numberStr = str(number)
        if number == 1:
            numberStr = "Ace"
        elif number == 11:
            numberStr = "Page"
        elif number == 12:
            numberStr = "Knight"
        elif number == 13:
            numberStr = "Queen"
        elif number == 14:
            numberStr = "King"
        message = "The " + numberStr + " of " + suit.split(".")[0]
        w,h = d.textsize(message,font=fnt)
        cr,cg,cb = self.last_start
        d.text(((card.width-w)//2,card.height-(h*2)), message, font=fnt, fill=(255-cr,255-cg,255-cb,255))
        return Image.alpha_composite(card.convert("RGBA"), txt)
    def tarot_suit(self):
        suit_cards = [self.tarot_card()]
        suit = self.last_suit
        suit_name = suit.split(".")[0]
        suit_colour = self.last_start
        for i in range(2,15):
            suit_cards.append(self.tarot_card(i, suit,suit_colour))
        return suit_name,suit_cards
    def save_tarot_suit(self, suit_name,cards):
        for i,c in enumerate(cards):
            c.save(suit_name+"_"+str(i)+".png")
    def generate_and_save_suit(self):
        self.save_tarot_suit(*self.tarot_suit())
    def get_symbol_location(self,number,n,card,image):
        if number == 1:
            return (card.width-image.width)//2,(card.height-image.height)//2
        if number == 2:
            return (card.width-image.width)//2, abs(((-(n//2)*(card.height-image.height)) + (card.height//3)-(image.height//2)))
        if number == 3:
            return (card.width-image.width)//2,(image.height) +(((card.height//3)-(image.height//2))*(n-1))
        if number == 4:
            return abs(((card.width//6) - (image.width//2)) - ((n-1)//2)*(card.width-(image.width))),abs(((-(n%2)*(card.height-image.height)) + (card.height//6)-(image.height//2)))
        if number == 5:
            if n%5 == 0:
                return (card.width-image.width)//2,(card.height-image.height)//2
            else:
                return abs(((card.width//6) - (image.width//2)) - ((n-1)//2)*(card.width-(image.width))),abs(((-(n%2)*(card.height-image.height)) + (card.height//6)-(image.height//2)))
        if number == 6:
            return [(card.width//6 - image.width//2,(card.height//6)-(image.height//2)),
                    (card.width//6 - image.width//2,(card.height//2)-(image.height//2)),
                    (card.width//6 - image.width//2,((5*card.height)//6)-(image.height//2)),
                    ((card.width-image.width)-(card.width//6 - image.width//2),(card.height//6)-(image.height//2)),
                    ((card.width-image.width)-(card.width//6 - image.width//2),(card.height//2)-(image.height//2)),
                    ((card.width-image.width)-(card.width//6 - image.width//2),((5*card.height)//6)-(image.height//2))][n-1]
        if number == 7:
            return [(card.width//6 - image.width//2,(card.height//6)-(image.height//2)),
                    (card.width//6 - image.width//2,(card.height//2)-(image.height//2)),
                    (card.width//6 - image.width//2,((5*card.height)//6)-(image.height//2)),
                    ((card.width-image.width)-(card.width//6 - image.width//2),(card.height//6)-(image.height//2)),
                    ((card.width-image.width)-(card.width//6 - image.width//2),(card.height//2)-(image.height//2)),
                    ((card.width-image.width)-(card.width//6 - image.width//2),((5*card.height)//6)-(image.height//2)),
                    ((card.width-image.width)//2,(card.height//3)-(image.height//2))][n-1]
        if number == 8:
            return [(card.width//6 - image.width//2,(card.height//6)-(image.height//2)),
                    (card.width//6 - image.width//2,(card.height//2)-(image.height//2)),
                    (card.width//6 - image.width//2,((5*card.height)//6)-(image.height//2)),
                    ((card.width-image.width)-(card.width//6 - image.width//2),(card.height//6)-(image.height//2)),
                    ((card.width-image.width)-(card.width//6 - image.width//2),(card.height//2)-(image.height//2)),
                    ((card.width-image.width)-(card.width//6 - image.width//2),((5*card.height)//6)-(image.height//2)),
                    ((card.width-image.width)//2,(card.height//3)-(image.height//2)),
                    ((card.width-image.width)//2,(card.height-image.height)-((card.height//3)-(image.height//2)))][n-1]
        if number == 9:
            return [(card.width//6 - image.width//2,(card.height//8)-(image.height//2)),
                    (card.width//6 - image.width//2,(3*card.height//8)-(image.height//2)),
                    (card.width//6 - image.width//2,((5*card.height)//8)-(image.height//2)),
                    (card.width//6 - image.width//2,((7*card.height)//8)-(image.height//2)),
                    ((card.width-image.width)-(card.width//6 - image.width//2),(card.height//8)-(image.height//2)),
                    ((card.width-image.width)-(card.width//6 - image.width//2),(3*card.height//8)-(image.height//2)),
                    ((card.width-image.width)-(card.width//6 - image.width//2),((5*card.height)//8)-(image.height//2)),
                    ((card.width-image.width)-(card.width//6 - image.width//2),((7*card.height)//8)-(image.height//2)),
                    ((card.width-image.width)//2,(card.height//3)-(image.height//2))][n-1]
        if number == 10:
            return [(card.width//6 - image.width//2,(card.height//8)-(image.height//2)),
                    (card.width//6 - image.width//2,(3*card.height//8)-(image.height//2)),
                    (card.width//6 - image.width//2,((5*card.height)//8)-(image.height//2)),
                    (card.width//6 - image.width//2,((7*card.height)//8)-(image.height//2)),
                    ((card.width-image.width)-(card.width//6 - image.width//2),(card.height//8)-(image.height//2)),
                    ((card.width-image.width)-(card.width//6 - image.width//2),(3*card.height//8)-(image.height//2)),
                    ((card.width-image.width)-(card.width//6 - image.width//2),((5*card.height)//8)-(image.height//2)),
                    ((card.width-image.width)-(card.width//6 - image.width//2),((7*card.height)//8)-(image.height//2)),
                    ((card.width-image.width)//2,(card.height//3)-(image.height//2)),
                    ((card.width-image.width)//2,(card.height-image.height)-((card.height//3)-(image.height//2)))][n-1]
        if number == 11:
            imageM = Image.open(os.path.join("symbology","moons.PNG"))
            ratio = min((card.width/6)/imageM.width, (card.height/6)/imageM.height)
            imageM = imageM.resize((round(imageM.width*ratio),round(imageM.height*ratio)))
            self.color_tarot_symbol(imageM)
            card.paste(imageM,((card.width-imageM.width)//2,(card.height//6)-(imageM.height//2)),imageM)
            return (card.width-image.width)//2,(card.height-image.height)//2
        if number == 12:
            imageM = Image.open(os.path.join("symbology","swords.PNG"))
            ratio = min((card.width/6)/imageM.width, (card.height/6)/imageM.height)
            imageM = imageM.resize((round(imageM.width*ratio),round(imageM.height*ratio)))
            self.color_tarot_symbol(imageM)
            card.paste(imageM,((card.width-imageM.width)//2,(card.height//6)-(imageM.height//2)),imageM)
            return (card.width-image.width)//2,(card.height-image.height)//2
        if number == 13:
            imageM = Image.open(os.path.join("symbology","suns.PNG"))
            ratio = min((card.width/6)/imageM.width, (card.height/6)/imageM.height)
            imageM = imageM.resize((round(imageM.width*ratio),round(imageM.height*ratio)))
            self.color_tarot_symbol(imageM)
            card.paste(imageM,((card.width-imageM.width)//2,(card.height//6)-(imageM.height//2)),imageM)
            return (card.width-image.width)//2,(card.height-image.height)//2
        if number == 14:
            imageM = Image.open(os.path.join("symbology","divinity.PNG"))
            ratio = min((card.width/6)/imageM.width, (card.height/6)/imageM.height)
            imageM = imageM.resize((round(imageM.width*ratio),round(imageM.height*ratio)))
            self.color_tarot_symbol(imageM)
            card.paste(imageM,((card.width-imageM.width)//2,(card.height//6)-(imageM.height//2)),imageM)
            return (card.width-image.width)//2,(card.height-image.height)//2
        
    def color_tarot_symbol(self, image):
        pixdata = image.load()
        cr,cg,cb = self.last_start
        for i in range(image.width):
            for j in range(image.height):
                if pixdata[i, j][3] != 0:
                    pixdata[i, j] = (255-cr, 255-cg, 255-cb, 255)

    def twitter_image(self):
        self.set_dimensions(800,600)
        self.set_monochrome(choice([True,False,False,False]))
        self.set_val(choice([1,5,5,5,5,5,10,15,20]))
        self.set_low_threshold(choice([25,50,75,100,100,100,100,100,150,200,250,300]))
        self.generate_image()
    def setup_twitter(self):
		print("For twitter to work, you'll need to replace the api details in the setup_twitter function")
		access_token = "blah"
		access_token_secret = "blah"
		consumer_key = "blah"
		consumer_secret = "blah"
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = API(auth)
    def tweet_image(self):
        filename = "Painting " + str(self.file_number) + ".jpg"
        self.api.update_with_media(filename)

    def full_twitter_experience(self):
        self.twitter_image()
        self.setup_twitter()
        self.tweet_image()
        self.delete_last_image()
        
painter = Painter()
