#Import Modules
try:
    import android
except ImportError:
    indroid = None
    print "none"
import random, operator, eztext
import os, pygame
from pygame.locals import *
from pygame.compat import geterror


if not pygame.font: print ('Warning, fonts disabled')
if not pygame.mixer: print ('Warning, sound disabled')

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')


#initialize UI
WIDTH = 1600
HEIGHT = 900
coloured_mode = True
place = 0
game_state = 0
score = 0
age = 0
boxes = [True, False, False ,False , True]
scrolling  = 0    
clicked_mouse_1 = False
clicked_mouse_2 = False
name = 0
name_entered = False
writing  = False
#build dictionary
"""
no gaps

. separator
- subject
= action
~ object
? question word
! other
"""
all_sentences = {"Present Simple" : ['who?.are=.you1-.you2-.??', 
                                'Alex-.visits=.his grandparents~.every Friday!',
                                'does=.Amy-.like=.football~.??',
                                'Dominic-.is=.often!.late~.for school!',
                                'does=.Paul\'s mum-.work=.in a shop!.??',
                                'Susie-.is=.very quiet~',
                                'Where?.is=.your brother-.??',
                                'how?.are=.you-.??',
                                'it-.is=.three o\'clock!',
                                'are=.there!.any cars-.in the street!.??'
                                ],
         "Present Continuous" : ['who-.is=.shouting=.on the street!.??',
                                'is=.he-.laughing=.??',
                                'kids-.are=.playing=.in the garden!',
                                'my mum-.is=.cooking=.dinner~.in the kitchen!',
                                'where?.are=.you-.going=.??',
                                'it-.is=.raining=.outside!',
                                'John-.is=.listening=.to!.music!',
                                'I-.am=.going to=.visit=.my aunt~.next weekend!',
                                'when?.are=.they-.moving=.to Italy!.??',
                                'Peter-.isn\'t=.doing=.anything~.now!'
                                ],
    
                "Past Simple" : ['She-.went=.to Beijing~.two weeks ago!'
                                ],
    
                "Past Continuous" : ['We-.were=.watching=.stars~.in the garden!.yesterday!']} 

#functions to create our resources
def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print ('Cannot load image:', fullname)
        raise SystemExit(str(geterror()))
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_file(name):
    fullname = os.path.join(data_dir, name)
    try:
        text = open(name, 'r')
    except pygame.error:
        print ('Cannot load file:', fullname)
        raise SystemExit(str(geterror()))
    
    return text

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print ('Cannot load sound: %s' % fullname)
        raise SystemExit(str(geterror()))
    return sound


class Dictionary:
    
    def __init__(self, tenses):
        
        self.sentence = []
        self.sentences = []
        self.text_pos = [0,0]
        
        self.text_size = 50
        self.tenses = set(tenses)
        self.widths = []
        self.is_clicked = []
        self.control = []
        self.age = [0,0]
        self.start_button_pos = []
        self.gameover_age = 0
        self.congratulations = ["Correct!", "Well Done!", "Good Job!", "That's Right!", "Nice!"]
        self.phrase = self.congratulations[random.randrange(len(self.congratulations))]
        self.sentence_order = 0
        self.word_centers = []
        
        self.wire_cut_rect = 0
        
        self.green, self.wire_rect = load_image("green.png")
        self.green_cut = load_image("green_cut.png")[0]
        self.red = load_image("red.png")[0]
        self.red_cut = load_image("red_cut.png")[0]
        self.blue = load_image("blue.png")[0]
        self.blue_cut = load_image("blue_cut.png")[0]
        self.gray = load_image("gray.png")[0]
        self.gray_cut = load_image("gray_cut.png")[0]
        self.black = load_image("black.png")[0]
        self.black_cut = load_image("black_cut.png")[0]

        
        for a_tense in self.tenses:
            if a_tense != None:
                self.sentences.extend(all_sentences[a_tense])
                
        self.sentences = set(self.sentences)
        self.sentences = list(self.sentences)
        #print self.sentences
        
        #random sentence
        random.shuffle(self.sentences)
        
    def print_dict(self):
        print self.sentences
        
    def get_sentence(self):

        
        
        
        self.sentence = self.sentences[self.sentence_order].split(".")
        if self.sentence_order == (len(self.sentences)-1):
            self.sentence_order = 0
        else:
            self.sentence_order += 1
            
        self.word_center_dots = []
        
        self.widths = range(len(self.sentence))
        self.word_centers = range(len(self.sentence))
        self.polygons = []

        self.wires_list = []
        self.is_clicked = [False] * len(self.sentence)
        self.control = list(self.sentence)
        
        self.place = 0
        
        
        self.gameover_age = 0
        self.congratulations = ["Correct!", "Well Done!", "Good Job!", "That's Right!", "Nice!"]
        self.phrase = self.congratulations[random.randrange(len(self.congratulations))]
        return self.control
        
    def shuffle(self):
        random.shuffle(self.sentence)
        return self.sentence
    
    def clicked_word(self, tile):
        
        self.is_clicked[tile] = True
        
    def clicked_check(self):
        
        return self.is_clicked

    def congratulate(self):
        return self.phrase
    
    def defuse(self):
        self.text_pos = [100, 560]
        self.space = 0
        # draw words in separate tiles
        font = pygame.font.SysFont("a_FuturaRound", WIDTH/25)
        
        k = ''
        for i in self.sentence:
            k +=str(i[:-1])
        sent_size = font.size(str(k))
        self.text_pos = [(WIDTH/2 - sent_size[0]/2) - (len(self.sentence)-1) * WIDTH * 25/1000, HEIGHT * 75/100]
        
##        if sent_size[0] < 1100:        
##            self.text_pos = [(WIDTH - sent_size[0])/2 + 50, 600]
##        else:
##            self.text_pos = [100, 570]
##        print sent_size, self.text_pos
        
        
        for i in self.sentence:
            
            
            
            
            colour = (0, 0, 0)
            current_image = self.black
            
            
           
            if boxes[4] == True:
                
                if i.endswith('-'):
                    colour = (0, 128, 0)
                    if self.is_clicked[self.sentence.index(i)]: 
                        current_image = self.green_cut
                    else:
                        current_image = self.green

                elif i.endswith('='):
                    colour = (255, 0, 0)
                    
                    if self.is_clicked[self.sentence.index(i)]: 
                        current_image = self.red_cut
                    else:
                        current_image = self.red

                elif i.endswith('~'):
                    colour = (0, 0, 255)
                    if self.is_clicked[self.sentence.index(i)]: 
                        current_image = self.blue_cut
                    else:
                        current_image = self.blue

                elif i.endswith('?'):
                    colour = (128, 128, 128)
                    if self.is_clicked[self.sentence.index(i)]: 
                        current_image = self.gray_cut
                    else:
                        current_image = self.gray

                else:
                    colour = (0, 0, 0)
                    if self.is_clicked[self.sentence.index(i)]: 
                        current_image = self.black_cut
                    else:
                        current_image = self.black
            else:
                    colour = (0, 0, 0)
                    if self.is_clicked[self.sentence.index(i)]: 
                        current_image = self.black_cut
                    else:
                        current_image = self.black

            current_image = pygame.transform.scale(current_image, (WIDTH * 35/100, HEIGHT * 58/100))
            self.wire_rect = current_image.get_rect()                    
            
            
            i = i[:-1]
            i = same_words_order(i)
                
            #text
            text = font.render(i, 1, colour)
            text_rect = text.get_rect(top=self.text_pos[1], left=self.text_pos[0])
            size = font.size(i)

            #words background
            word_poly = pygame.Surface((size[0]+ WIDTH * 25/1000, size[1]+WIDTH * 20/1000),SRCALPHA)
            word_poly.fill((255,255,255,125))

            #wire bent
            if text_rect[0] + size[0]/2 + self.space > WIDTH/2:
                bent = 0
                bent_tab = -self.wire_rect[2]/2 + WIDTH*1/100
            else:
                bent = self.wire_rect[2]/2
                bent_tab = - WIDTH*1/100
                
            

            #detect wires positions
            
            wire_cut_rect = pygame.Rect(text_rect[0] + size[0]/2 + self.space -5,
                                        text_rect[1] - 390, 8, 375)

            self.wires_list.append(wire_cut_rect)
            
            #draw words
           
            screen.blit(word_poly, (text_rect[0]-(WIDTH * 25/1000)/2 + self.space, text_rect[1]-(WIDTH * 20/1000)/2))
            screen.blit(text, (text_rect[0] + self.space, text_rect[1]))
            screen.blit(current_image, (text_rect[0] + bent_tab + size[0]/2 + self.space,
                                        text_rect[1] - self.wire_rect[3]-WIDTH*1/100),
                                        (bent, 0, self.wire_rect[2]/2, self.wire_rect[3]))

            
            self.space += size[0] + WIDTH * 5/100

            
##
    def wire_rectlist(self):
        
        return self.wires_list
         
#classes for our game objects
class Bomb(pygame.sprite.Sprite):
    """draws a bomb on the screen and explodes it when detonated"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.bomb, self.rect = load_image('Sticky_Bomb.png', (255, 255, 255))
        self.bomb = pygame.transform.smoothscale(self.bomb, (WIDTH * 60/100, HEIGHT* 60/100 ))
        self.rect = self.bomb.get_rect()
        self.explosion_sound = load_sound('boom.wav')
        self.explosion, self.exp_rect = load_image('explosion.png', -1)
        self.explosion = pygame.transform.scale(self.explosion, (WIDTH * 320/100, HEIGHT* 426/100 ))
        self.exp_rect = self.explosion.get_rect()
        self.age = [0,0]
        self.game_over_age = 0
        #print self.exp_rect
        self.expl_rect = pygame.Rect(0, 0, self.exp_rect[2]/8, self.exp_rect[3]/6)
        #print self.exp_rect
        self.explode = False

    def draw(self):
        if self.explode == False:
            screen.blit(self.bomb, ((WIDTH - self.rect.width)/2, 0))
        "draws an explosion depending on time"
        
        if self.explode == True:
            screen.blit(self.explosion, ((WIDTH - self.expl_rect.width)/2, 0), self.expl_rect)
            if self.age[1] < 6:
                if self.age[0] < 5:
                    self.age[0] += 1
                
                else:
                    self.age[0] = 0
                    self.age[1] += 1
                self.expl_rect = pygame.Rect(self.age[0] * self.expl_rect[2],
                                             self.age[1] * self.expl_rect[2], self.expl_rect[2], self.expl_rect[2])
         
    def update(self):
        
        pass 
            

    def detonator(self):
        "detonates the bomb"
        self.explode = True
        self.explosion_sound.play()
        
    def game_over(self):
        global txtbx, writing
        if self.game_over_age > 60:

              
            
            font = pygame.font.SysFont("a_FuturaRound", WIDTH/10)
            font_score = pygame.font.SysFont("a_FuturaRound", WIDTH/15)
            
            text = font.render("GAME OVER", 1, (58,110,131))
            text_score = font_score.render("score: "+ str(score), 1, (90,150,120))
            
            size = font.size("GAME OVER")
            size_score = font_score.size("score: "+ str(score))
            
            text_rect = text.get_rect(top=HEIGHT * 20/100, left=WIDTH / 2 - size[0]/2)
            pos = (WIDTH / 2 - size_score[0]/2, HEIGHT * 45/100)
        
            word_poly = pygame.Surface((size_score[0]+30, size_score[1]+6),SRCALPHA)
            word_poly.fill((255,255,255,80))

            
            input_size = txtbx.get_size()
            input_size = list(input_size)
##            print input_size, size_score
##            print
            
            if input_size[0] < size_score[0]:
                input_size[0] = size_score[0]

##            print input_size, size_score
##            print "----"
            input_pos = (WIDTH / 2 - input_size[0]/2, HEIGHT * 65/100)

            
            input_poly = pygame.Surface((input_size[0]+30, input_size[1]+6),SRCALPHA)
            input_poly.fill((255,255,255,80))
            input_rect = input_poly.get_rect(left=input_pos[0] - 15, top=input_pos[1] - 3)
            
            mouse_pos = pygame.mouse.get_pos()
            screen.blit(input_poly, (input_pos[0] - 15, input_pos[1] - 3))  
            
            if clicked_mouse_1 == True:
                if name_entered == False:
                    if input_rect.collidepoint(mouse_pos):
                            txtbx = eztext.Input(maxlength=20, color=(100,160,130), prompt='')
                            writing = True
            if clicked_mouse_2 == True:
                    
                if len(txtbx.get_value()) == 0:
                    writing = True
                value = ""    
                if writing == True:
                    #if self.game_over_age
                    self.game_over_age += 1
                    if self.game_over_age % 80 == 0:
                        value = txtbx.get_value() + "I"
                        txtbx.set_value(value)
                    if self.game_over_age % 80 == 40:
                        value = txtbx.get_value()[:-1]
                        txtbx.set_value(value)
                    print txtbx.get_value()
            
                            
            input_size = txtbx.get_size()    
            input_pos = (WIDTH / 2 - input_size[0]/2, HEIGHT * 65/100)

            txtbx.set_font(pygame.font.SysFont("a_FuturaRound", WIDTH/20))
            txtbx.set_pos(input_pos[0], input_pos[1])
            txtbx.draw(screen)
            
            screen.blit(text, text_rect)
            screen.blit(word_poly, (pos[0] - 15, pos[1] - 3))          
            screen.blit(text_score, pos)
        else:
            self.game_over_age += 1
        
            
    def get_age(self):
        return self.game_over_age 
        
    def renew(self):
        self.game_over_age = 0
        self.age = [0,0]
        self.explode = False
            
class Cutters(pygame.sprite.Sprite):
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.image, self.rect = load_image('cutters.png', -1)
        #self.image = pygame.transform.scale(self.image, (WIDTH * 102/100, HEIGHT* 35/100 ))
        #self.image = pygame.transform.smoothscale(self.image, (WIDTH * 102/100, HEIGHT* 35/100 ))
        self.rect = self.image.get_rect()
        self.cutters_size = 1
        if WIDTH < 1000:
            self.cutters_size = 0.5
            self.image, self.rect = load_image('cutters_small.png', -1)
            
        self.cut_rect = pygame.Rect(0, 0, 260 * self.cutters_size, 256 * self.cutters_size)
        self.pos = [WIDTH, HEIGHT]
        self.age = 0
        
        self.cutting = 0
        self.cut_space = 0 
        
    def draw(self):
        
        
        self.pos = pygame.mouse.get_pos()
        screen.blit(self.image, self.rect, self.cut_rect)
        self.rect.left = self.pos[0]
        self.rect.top = self.pos[1]

        if self.cutting == 1:
           if self.age < 4:
                self.age += 1
        elif self.age == 4:
            self.age = 4
        self.cut_rect = pygame.Rect(self.age * 260 * self.cutters_size, 0, 260 * self.cutters_size, 256 * self.cutters_size) 
        
    def cut(self):
        "draws cutters"
        self.cutting = 1
        
        
            
    def uncut(self):
        self.age = 0
        self.cutting = 0
        self.cut_rect = pygame.Rect(0, 0, 260 * self.cutters_size, 256 * self.cutters_size)

    def cutters_rect(self):
        self.cut_space = pygame.Rect(self.pos[0] + 8, self.pos[1] + 5, 8, 22)
        
        return self.cut_space
    
class Cursor(pygame.sprite.Sprite):
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.image, self.rect = load_image('cursor.png', -1)
        self.image = pygame.transform.smoothscale(self.image, (WIDTH/15, HEIGHT/15))
        self.pos = [WIDTH, HEIGHT]
        
        
        
    def draw(self):
        
        self.pos = pygame.mouse.get_pos()
        screen.blit(self.image, self.rect)
        self.rect.left = self.pos[0]
        self.rect.top = self.pos[1]

class Back_button(pygame.sprite.Sprite):
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.image, self.rect = load_image('back.png', -1)
        self.image = pygame.transform.scale(self.image, (WIDTH/15, HEIGHT/8))
        self.rect = self.image.get_rect(left=WIDTH/100, top=HEIGHT - HEIGHT/7)
        
        
    def draw(self):
        
        screen.blit(self.image, self.rect)
        
    def clicked(self):
        global game_state, scrolling
        self.mouse_pos = pygame.mouse.get_pos()
        
        if self.rect.collidepoint(self.mouse_pos):
            game_state = 0
            scrolling  = 0    

            return True
    
def cutting(rect, rect_list, original_sentence, shuffled_sentence, bomb):
    global place, game_state, score
    cut_sound = load_sound('cut.wav')
    point_sound = load_sound('coin.wav')
    rect_index = rect.collidelist(rect_list)
    original_sentence_copy = list(original_sentence)
    shuffled_sentence_copy = list(shuffled_sentence)

##    print
##    print original_sentence[place]
##    print shuffled_sentence[rect_index]
##    print place
    if rect_index != -1:
        if dictionary.clicked_check()[rect_index] == False:
##            print
##            
##            print
            if original_sentence_copy[place][-2] in ['1','2','3','4']:
                original_sentence_copy[place] =  original_sentence_copy[place].replace(str(original_sentence_copy[place][-2]), "")
            if shuffled_sentence_copy[rect_index][-2] in ['1','2','3','4']:
                shuffled_sentence_copy[rect_index] = shuffled_sentence_copy[rect_index].replace(str(shuffled_sentence_copy[rect_index][-2]), "")
                
##            print original_sentence_copy[place]
##            print shuffled_sentence_copy[rect_index]
                
            if original_sentence_copy[place] == shuffled_sentence_copy[rect_index]:

                
                
                cut_sound.play()
                place +=1
                dictionary.clicked_word(rect_index)
                #print dictionary.clicked_check()
            else:
                bomb.detonator()
                game_state = 3
                

            if place == len(original_sentence_copy):
                point_sound.play()
                score += 1
                game_state = 2
                
def same_words_order(i):
    if i.endswith('1'):
        i = i[:-1]
    elif i.endswith('2'):
        i = i[:-1]
    elif i.endswith('3'):
        i = i[:-1]
    elif i.endswith('4'):
        i = i[:-1]
    return i

def start_screen():
    
    font = pygame.font.SysFont("a_FuturaRound", WIDTH/10)
    text = font.render("START", 1, (58,110,131))
    size = font.size("START")
    
    

    font_set = pygame.font.SysFont("a_FuturaRound", WIDTH/25)
    
    text_high = font_set.render("high score", 1, (58,110,131))
    text_set = font_set.render("settings", 1, (58,110,131))

    size_high = font_set.size("high score")
    size_set = font_set.size("settings")
    
    set_rect = text_set.get_rect(top=HEIGHT * 70/100, left=WIDTH / 2 - size_set[0]/2)
    high_rect = text_high.get_rect(top=HEIGHT * 80/100, left=WIDTH / 2 - size_high[0]/2)
    start_rect = text.get_rect(top=HEIGHT * 50/100, left=WIDTH / 2 - size[0]/2)
    
    screen.blit(text_set, set_rect)
    screen.blit(text_high, high_rect)
    screen.blit(text, start_rect)
    
    return start_rect, set_rect, high_rect

def settings_screen():
    
    font = pygame.font.SysFont("a_FuturaRound", WIDTH/25)
    text_list = ["Tenses:",
                 "      Present Simple", "      Present Continuous", "      Past Simple", "      Past Continuous",
                 "", "Coloured Mode"]
    print_text("SETTINGS", 10, (58,110,131), (WIDTH / 2, HEIGHT * 1/100), "Center")
    space = 20
    poly_list = []
    for i in text_list:
        text = font.render(i, 1, (75,145,115))
        size = font.size(i)
        
        rect = text.get_rect(top=HEIGHT * space/100, left=WIDTH / 10)
        
        screen.blit(text, rect)
        if i.startswith( ' ' ) | i.startswith( 'C' ):
            word_poly = pygame.Surface((size[1], size[1]),SRCALPHA)
            word_poly.fill((255,255,255,80))
            poly_rect = word_poly.get_rect(top=HEIGHT * space/100, left=WIDTH - WIDTH * 12/100)
            
            screen.blit(word_poly, poly_rect)
            poly_list.append(poly_rect)   
        space += 10

    
    
    for poly in poly_list:
        i = boxes[poly_list.index(poly)]
        if i == True:
            
            word_poly = pygame.Surface((poly[2] * 6/10 , poly[3] * 6/10), SRCALPHA)
            word_poly.fill((0,0,0,200))
            poly_rect = word_poly.get_rect(top=poly[1] + poly[2]* 2/10, left=poly[0] + poly[3]* 2/10)
        
            screen.blit(word_poly, poly_rect)
            
    return poly_list
def high_score_screen(scroll):
    global players_list, score_list, scrolling
    space = 22
    
    a_file = os.path.join(data_dir, "score.txt")
    files = open(a_file, 'r')
    players = files.readline()
    scores = files.readline()
    players_list = players.split(',')
    players_list[-1] = players_list[-1][:-1]
    score_list = scores.split(',')
    play_score = dict(zip(players_list, score_list))
    sorted_x = sorted(play_score.items(), key=operator.itemgetter(1), reverse=True)
    
    
    if scroll == "up":
        if scrolling < 0:
            scrolling  += WIDTH * 20/1000
    if scroll == "down":
        scrolling  += - WIDTH * 20/1000
    
    files.close()
    

    for i, k in sorted_x:
        print_text(i, 5, (75,145,115), (WIDTH / 9, HEIGHT * space/100 + scrolling), "Left")
        print_text(str(k), 5, (75,145,115), (WIDTH - WIDTH * 12/100, HEIGHT * space/100 + scrolling), "Right")
        space += 12
    
##    for i in players_list:
##        print_text(i, 22, (75,145,115), (WIDTH / 9, HEIGHT * space1/100), "Left")
##        space1 += 12
##    for k in score_list:
##        print_text(str(k), 22, (75,145,115), (WIDTH - 150, HEIGHT * space2/100), "Right")
##        space2 += 12
    screen.blit(not_tranparent_oak, oak_rect)
    
    print_text("HIGH SCORE", 10, (58,110,131), (WIDTH / 2, HEIGHT * 1/100), "Center")

def add_name():
    a_file = os.path.join(data_dir, "score.txt")
    files = open(a_file, 'r')
    players = files.readline()
    players = players[:-1]
    scores = files.readline()
    files.close()
    files = open(a_file, 'w')
    print players, name
    players += ","+name
    scores += ","+str(score)
##    print players
##    print
##    print scores
    files.truncate()
    files.write(players)
    files.write('\n')
    files.write(scores)
    #print files
    files.close()
    
def congratulations_screen():
    phrase = dictionary.congratulate()
    print_text(phrase, 10, (58,110,131), (WIDTH/2, HEIGHT *2/5), "Center")
   
def settings_screen_controls(poly_list):
    global boxes
    
    pos = pygame.mouse.get_pos()
    for i in poly_list:
        if i.collidepoint(pos):
            boxes[poly_list.index(i)] = not boxes[poly_list.index(i)]
    
    
    
        
def start_menu(buttons):
    global game_state, name_entered, txtbx, clicked_mouse_2, score
    start, settings, high_score = buttons
    pos = pygame.mouse.get_pos()
    if start.collidepoint(pos):
        game_state = 1
        name_entered = False
        clicked_mouse_2 = False
        txtbx = eztext.Input(maxlength=20, color=(100,160,130), prompt='Player Name')
        new_game()
        score = 0
    if settings.collidepoint(pos):
        game_state = 4
    if high_score.collidepoint(pos):
        game_state = 5
 
def score_text():
        
    font = pygame.font.SysFont("a_FuturaRound", WIDTH/20)
    text = font.render("score: "+ str(score), 1, (90,150,120))
    size = font.size("score: "+ str(score))
    pos = (WIDTH - size[0] - WIDTH/40, HEIGHT/30)
            
    word_poly = pygame.Surface((size[0]+WIDTH * 25/1000, size[1]+6),SRCALPHA)
    word_poly.fill((255,255,255,80))
            
    screen.blit(word_poly, (pos[0] - (WIDTH * 25/1000)/2, pos[1] - 3))          
    screen.blit(text, pos)
    
def print_text(text, size, colour, pos, centered = "Left", poly_colour = None):
    font = pygame.font.SysFont("a_FuturaRound", WIDTH * size/100)
    a_text = font.render(str(text), 1, colour)
    a_size = font.size(str(text))
    if centered == "Center":
        tilt = - a_size[0]/2
    elif centered == "Right":
        tilt = - a_size[0]
    elif centered == "Left":
        tilt = 0
       
    a_poly = pygame.Surface((a_size[0]+20, a_size[1]+6),SRCALPHA)
    if poly_colour != None:
        a_poly.fill(colour)
            
    screen.blit(a_poly, (int(pos[0]) + tilt - 10, int(pos[1])))          
    screen.blit(a_text, (int(pos[0]) + tilt, int(pos[1])))
      
def new_sentence():
    global place
    original_sentence = dictionary.get_sentence()
    shuffled_sentence = dictionary.shuffle()
    place = 0
    
    return original_sentence, shuffled_sentence

def new_game():
    global dictionary
    tenses = []
    if boxes[0] == True:
        tenses.append("Present Simple")    
    if boxes[1] == True:
        tenses.append("Present Continuous")    
    if boxes[2] == True:
        tenses.append("Past Simple")    
    if boxes[3] == True:
        tenses.append("Past Continuous")    
    dictionary = Dictionary(tenses)
    #print tenses, dictionary.print_dict()



#Initialize Everything
pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('Bomb Defuse')
pygame.mouse.set_visible(0)
background = pygame.image.load("white-oak.jpg").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        
not_tranparent_oak, oak_rect = load_image('white-oak.png', -1)
not_tranparent_oak = pygame.transform.scale(not_tranparent_oak, (WIDTH, HEIGHT))

txtbx = eztext.Input(maxlength=20, color=(100,160,130), prompt='Enter Name')

#Put Text On The Background, Centered
##    if pygame.font:
##        font = pygame.font.Font(None, 36)
##        text = font.render("Pummel The Chimp, And Win $$$", 1, (10, 10, 10))
##        textpos = text.get_rect(centerx=background.get_width()/2)
##        background.blit(text, textpos)

#Display The Background
screen.blit(background, (0, 0))
pygame.display.flip()

#Prepare Game Objects
clock = pygame.time.Clock()
whiff_sound = load_sound('whiff.wav')
dictionary = Dictionary(["Present Simple"])
bomb = Bomb()
cutters = Cutters()
cursor = Cursor()
back_button = Back_button()
#allsprites = pygame.sprite.RenderPlain(cutters)

def main():
    global game_state, place, clock, score, clicked_mouse_1, clicked_mouse_2, name, name_entered, writing, txtbx
#Main Loop
    going = True
##    original_sentence = dictionary.get_sentence()
##    shuffled_sentence = dictionary.shuffle()
##    place = 0
    original_sentence, shuffled_sentence = new_sentence()
    
    dictionary.defuse()
    while going:
        clock.tick(60)
        
        screen.blit(background, (0, 0))
        
        #Handle Input Events
        events = pygame.event.get()
        for event in events:
            
            if event.type == QUIT:
                going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                going = False
            elif event.type == KEYDOWN and event.key in (K_RETURN, K_KP_ENTER):
                name = txtbx.update(events)
                name_entered = True
                add_name()
                game_state = 0
                bomb.renew()
            elif event.type == KEYDOWN and game_state == 3:
                if writing == True:
                    writing = False
                    value = ""
                    txtbx.set_value(value)
                
                
            elif event.type == MOUSEBUTTONDOWN:
                
                
                if game_state == 5:
                    if event.button == 4:
                        high_score_screen("up")
                    if event.button == 5:
                        high_score_screen("down")   
                if event.button == 1:
                    clicked_mouse_1 = True 
                    if game_state == 0:
                        start_menu(start_screen())
                        original_sentence, shuffled_sentence = new_sentence()
                        break
                    if game_state == 1:
                        cutters.cut()
                        cutting(cutters.cutters_rect(), dictionary.wire_rectlist(),
                                original_sentence, shuffled_sentence, bomb)
                        back_button.clicked()
                       # if back_button.clicked():
                        #    original_sentence, shuffled_sentence = new_sentence()
                        
                        break
                    if game_state == 2:
                        original_sentence, shuffled_sentence = new_sentence()
                        game_state = 1
                        break
                    if game_state == 3:
                        clicked_mouse_2 = True 
                        
                        if back_button.clicked():
                            game_state = 0
                            score = 0
                            original_sentence, shuffled_sentence = new_sentence()
                            bomb.renew()
                        break
                    if game_state == 4:
                        settings_screen_controls(settings_screen())
                        back_button.clicked()
                        break
                    if game_state == 5:
                        
                        back_button.clicked()
                        break
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    clicked_mouse_1 = False
                    
                    if game_state == 1:
                        cutters.uncut()
        
        
        #Draw Everything
        if game_state == 0:
            bomb.draw()
            start_screen()
            cursor.draw()
            
        if game_state == 1:
            dictionary.defuse()
            bomb.draw()
            score_text()
            back_button.draw()
            cutters.draw()
            
        if game_state == 2:
            congratulations_screen()
            score_text()
            
        if game_state == 3:
            if name_entered == False:
                if clicked_mouse_2 == True:
                    txtbx.update(events)
                
            bomb.draw()
            bomb.game_over()
            
            back_button.draw()
            cursor.draw()
            
        if game_state == 4:
            settings_screen()
            back_button.draw()
            cursor.draw()
            
        if game_state == 5:
            high_score_screen("no")
            back_button.draw()
            cursor.draw()
            
        pygame.display.flip()
        #allsprites.draw()
        
        
        
    pygame.quit()

#Game Over


#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()
