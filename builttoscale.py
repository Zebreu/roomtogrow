import math
import random    
import pyxel
distance = 11
#prompt_colors = [14, 8, 2, 2, 8]
prompt_colors = [1, 5, 6, 6, 5]

leaf = [(20,20), (15,21), (16,18), (14,16), (18,17), (20,12), (22,17), (26,16), (24,18), (25, 21), (20,20)]

def calculate_distance(point, other_point):
    x_change = point[0]-other_point[0]
    y_change = point[1]-other_point[1]
    norm = math.sqrt(y_change**2 + x_change**2)
    return norm, x_change, y_change    

def add_transform(points, x=-20, y=-20):
    new_points = []
    for p in points:
        new_points.append((p[0]+x, p[1]+y))
    return new_points

def rotate(points, amount=1.22):
    a = math.cos(amount)
    b = -math.sin(amount)
    c = math.sin(amount)
    d = math.cos(amount)
    new_points = []
    for p in points:
        new_points.append((p[0]*a + p[1]*b, p[0]*c + p[1]*d))
    return new_points
    
def scale(points, amount=2):
    new_points = []
    for p in points:
        new_points.append((p[0]*amount, p[1]*amount))
    return new_points

def draw_leaf(pos_x, pos_y, rotation, factor=1, two=True):
    new_leaf = add_transform(leaf)
    new_leaf = rotate(new_leaf, amount=rotation)
    if factor != 1:
        new_leaf = scale(new_leaf, factor)
    new_leaf = add_transform(new_leaf, x= pos_x, y=pos_y)
    for i in range(len(new_leaf)-1):
        a = new_leaf[i]
        b = new_leaf[i+1]
        pyxel.line(a[0], a[1], b[0], b[1], col=3)
    if two:
        new_leaf = add_transform(leaf)
        new_leaf = rotate(new_leaf, amount=rotation)
        new_leaf = scale(new_leaf, 0.7)
        new_leaf = add_transform(new_leaf, x= pos_x, y=pos_y)
        for i in range(len(new_leaf)-1):
            a = new_leaf[i]
            b = new_leaf[i+1]
            pyxel.line(a[0], a[1], b[0], b[1], col=11)
    if False:
        new_leaf = add_transform(leaf)
        new_leaf = rotate(new_leaf, amount=rotation)
        new_leaf = scale(new_leaf, 0.3)
        new_leaf = add_transform(new_leaf, x= pos_x, y=pos_y)
        for i in range(len(new_leaf)-1):
            a = new_leaf[i]
            b = new_leaf[i+1]
            pyxel.line(a[0], a[1], b[0], b[1], col=3)


class App:
    def __init__(self):
        pyxel.init(256, 256)
        pyxel.load("builttoscale.pyxres")
        self.start()
        pyxel.run(self.update, self.draw)

    def start(self):
        self.ticker = 0
        self.tip_x = 256/2-4
        self.tip_y = 256-8
        self.maximum_height = 256
        self.score = 0
        self.prompts = [['S', None], ['T', None], ['N', None], ['E', None]]
        self.segments = []
        self.lines = []
        self.segments.append((self.tip_x, self.tip_y))
        self.prompt_loop = 0
        self.roots = []
        self.prompt_color = 1
        self.roots.append((self.tip_x, self.tip_y))
        self.chloro = 0
        self.regenturn = 1
        self.energy = 30
        self.sun = [45,100]
        self.terminal = []
        
        pyxel.sounds[50].set(notes="d1d2d3d4", tones='s', volumes='3', effects='vvvvf', speed=5)

        pyxel.sounds[51].set(notes="C2D2E2F2G2A2B2", tones='s', volumes='1', effects='v', speed=5)

        pyxel.playm(0, loop=True)
        
        self.wall = self.draw_wall()
        self.wallnoise = self.noise(self.wall)

        self.windownoise = []
        for i in range(3000):
            x = random.randint(70,70+114)
            y = random.randint(30,30+110)
            c = random.choice([7,13, 12])
            self.windownoise.append((x,y,c))


        self.sun_noise = []

        for _ in range(8000):
            lightx = random.gauss(0, 8.0)
            lighty = random.gauss(0, 8.0)
            color = random.choices([9,10], weights=[0.8,0.2], k=1)[0]
            self.sun_noise.append((lightx, lighty, color))

        
        
    #'CDEFGAB'+'#-'+'01234' or 'R'
    #TSPN
    #01234567
    #NSVFHQ
    def draw_wall(self):
        #brick_colors = [4, 14, 15, 13]
        #brick_colors = [1, 5]
        brick_colors = [1, 2, 5]
        y = 240
        bricks = []
        for j in range(30):
            x = -10
            for i in range(15):
                width = random.randint(20,30)
                bricks.append((x, y, width, 8, random.choices(brick_colors, weights=[0.8,0.1,0.1], k=1)[0]))
                x += width
            y += -8
        return bricks
    
    def noise(self, locations):
        noises = []
        for location in locations:
            for i in range(140):
                new_x = random.gauss(location[0]+12, sigma=7)
                new_y = random.gauss(location[1]+4, sigma=7)
                noises.append((new_x, new_y, 0))
        return noises
            

    def find_source(self, destination):
        distances = []
        for segment in self.segments:
            if segment not in self.terminal[:-1]:
                distances.append(calculate_distance(segment, destination)[0])
            else:
                distances.append(1000)
        
        source = sorted(zip(distances, self.segments))[0]
        if source[1] in self.terminal:
            self.terminal.remove(source[1])
        return source[1]

    def add_segment(self, destination):
        rate = max(0,len(self.terminal)-1)
        if rate > 0:
            self.chloro += max(1,math.log(rate, 5))#/self.regenturn
        
        source = self.find_source(destination)
        norm, x_change, y_change = calculate_distance(destination, source)

        try:
            x_change = x_change/norm*distance
            y_change = y_change/norm*distance
        except ZeroDivisionError:
            x_change = distance
            y_change = distance
        self.segments.append((int(source[0]+x_change), int(source[1]+y_change)))
        self.maximum_height = min(self.segments[-1][1], self.maximum_height)
        self.lines.append((source, self.segments[-1]))
        self.energy += -1
        self.terminal.append(self.segments[-1])
        

    def reset_prompts(self):
        to_eventually_sort = []
        for prompt in self.prompts:
            x = random.randint(5,250)
            y = random.randint(5,250)
            to_eventually_sort.append((x,y))
        sorted_prompts = sorted(to_eventually_sort)
        for prompt, (x,y) in zip(self.prompts, sorted_prompts):
            prompt[1] = (x,y)

    def update(self):
        self.ticker += 1
        
        if pyxel.btnp(pyxel.KEY_R):
            self.start()

        if pyxel.btnp(pyxel.KEY_M):
            pyxel.stop()
            
        if self.chloro > 30:
            self.regenturn += 1
            self.energy += 13
            self.energy = min(self.energy, 30)
            self.chloro = 0
            
        if self.energy < 1:
            return
        self.prompt_color = prompt_colors[int(self.prompt_loop)]
        self.prompt_loop += 0.2
        self.prompt_loop = self.prompt_loop % 5

        original = len(self.segments)
        
        if pyxel.btnp(pyxel.KEY_S):
            for prompt in self.prompts:
                if prompt[0] == 'S':
                    destination = prompt[1]
                    self.reset_prompts()
                    break            
            self.add_segment(destination)

        if pyxel.btnp(pyxel.KEY_T):
            for prompt in self.prompts:
                if prompt[0] == 'T':
                    destination = prompt[1]
                    self.reset_prompts()
                    break            
            self.add_segment(destination)        

        if pyxel.btnp(pyxel.KEY_N):
            for prompt in self.prompts:
                if prompt[0] == 'N':
                    destination = prompt[1]
                    self.reset_prompts()
                    break            
            self.add_segment(destination)        

        if pyxel.btnp(pyxel.KEY_E):
            for prompt in self.prompts:
                if prompt[0] == 'E':
                    destination = prompt[1]
                    self.reset_prompts()
                    break            
            self.add_segment(destination)      

    
        if pyxel.btnp(pyxel.KEY_I):
            self.roots.append((self.roots[-1][0]+distance, self.roots[-1][1]))

        if len(self.segments) > original:
            pyxel.play(2, 50)
            
        self.score = int(256-self.maximum_height)
        
        for prompt in self.prompts:
            if prompt[1] is None:
                x = random.randint(5,250)
                y = random.randint(5,250)
                prompt[1] = (x,y)
        if (self.ticker % 3) == 0:
            indices = [random.randint(0,2999) for _ in range(random.randint(20,300))]
            for i in indices:
                x = random.randint(70,70+114)
                y = random.randint(30,30+110)
                c = random.choice([7,13, 12])
                self.windownoise[i] = (x,y,c)

    def draw_window(self):
        
        #glass
        #pyxel.rect(70, 30, 114, 110, 7)
        pyxel.rect(70, 30, 114, 110, 6)
        for x,y,c in self.windownoise:
            pyxel.pset(x, y, c)
        
        # sun
        pyxel.clip(70,30,110,100)
        self.sun[0] += 1/20
        if self.ticker < 1600:
            self.sun[1] += -1/40
        elif self.ticker < 1700:
            self.sun[1] += 0
        else:
            self.sun[1] += 1/40
        x = self.sun[0]
        y = self.sun[1]
        for lightx, lighty, color in self.sun_noise:
             pyxel.pset(lightx+x, lighty+y, color)
        pyxel.clip()

        #left ledge
        pyxel.rect(70, 30, 8, 100, 4)
        pyxel.rectb(70+1, 30+1, 8-1, 100-1, 15)
        pyxel.rectb(70, 30, 8, 100, 0)
        
        pyxel.rect(70+54, 30, 8, 100, 4)
        pyxel.rectb(70+1+54, 30+1, 8-1, 100-1, 15)
        pyxel.rectb(70+54, 30, 8, 100, 0)
        

        #right ledge
        pyxel.rect(184-6, 30, 8, 100, 4)
        pyxel.rectb(184-6+1, 30+1, 8-1, 100-1, 15)
        pyxel.rectb(184-6, 30, 8, 100, 0)

        #bottom ledge
        pyxel.rect(64, 128, 128, 8, 4)
        pyxel.rectb(64+1, 128+1, 128-1, 8-1, 15)
        pyxel.rectb(64, 128, 128, 8, 0)
        pyxel.line(70, 133, 81, 133, 0)
        pyxel.line(110, 131, 123, 131, 0)
        pyxel.line(140, 132, 163, 133, 0)
        
        #pyxel.dither(0.3)
        pyxel.rect(65, 136, 128, 1, 0)
        pyxel.rect(66, 137, 128, 1, 0)
        pyxel.rect(67, 138, 128, 1, 0)
        pyxel.rect(68, 139, 128, 1, 0)
        pyxel.rect(69, 140, 128, 1, 0)
        
        pyxel.rect(64, 30, 128, 8, 4)
        pyxel.rectb(64+1, 30+1, 128-1, 8-1, 15)
        pyxel.rectb(64, 30, 128, 8, 0)

        

    def draw(self):
        pyxel.cls(0)
        for brick in self.wall:
            pyxel.rect(brick[0], brick[1], brick[2], brick[3], brick[4])
            pyxel.rectb(brick[0]+1, brick[1]+1, brick[2]-1, brick[3]-1, 6)
            pyxel.rectb(brick[0], brick[1], brick[2], brick[3], 0)
        
        for noise in self.wallnoise:
            pyxel.pset(*noise)
        
        self.draw_window()
        

        pyxel.rect(5, 20, self.energy, 4, col=12)
        #pyxel.blt(0,0,0,0,0,256,256)
        
        for _ in range(20):
            new_x = random.gauss(self.segments[-1][0], sigma=5)
            new_y = random.gauss(self.segments[-1][1], sigma=5)
            new_color = random.choice([3, 11, 1, 5, 6, 13, 11, 3, 10])
            pyxel.pset(new_x, new_y, new_color)

        previous = (self.tip_x, self.tip_y)
        for x,y in self.roots:
            pyxel.line(previous[0], previous[1], x, y, col=15)
            pyxel.trib(x, y+2, x-2, y, x+2, y, col=10)
            #pyxel.line(previous[0], previous[1], x, y, col=15)
            previous = (x,y)
        
        for x,y in self.segments:
            #pyxel.circb(x, y, r=2, col=3)
            draw_leaf(x, y, x+y, factor=0.5, two=False)
        for line in self.lines:   
            pyxel.line(line[1][0], line[1][1], line[0][0], line[0][1], col=11)
            
        #pyxel.dither(1.0)
        
        for prompt in self.prompts:
            pyxel.circ(prompt[1][0], prompt[1][1], r=5, col=0)
            pyxel.circb(prompt[1][0], prompt[1][1], r=5, col=self.prompt_color)
            pyxel.text(prompt[1][0]-1,prompt[1][1]-2, prompt[0], 15)

        
        
        if False:
            pyxel.circb(26,245, r=5, col=9)
            pyxel.text(25,243, 'R', 9)
            

            pyxel.circb(226,245, r=5, col=9)
            pyxel.text(225,243, 'E', 9)

        if len(self.terminal) > 1:
            for terminal in self.terminal[:-1]:
                draw_leaf(terminal[0], terminal[1], sum(terminal))

        pyxel.rect(0, 5, 40, 23, 0)
        pyxel.rect(5, 13, self.chloro, 4, col=11)
        pyxel.rect(5, 20, self.energy, 4, col=12)
        pyxel.text(5,5, f'{self.score}', 15)
        



App()