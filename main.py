import pyglet

stack = []

def alpha_shift(string):
    new_string = ""
    for char in string:
        if char not in ["/", "-"]:
            new_string += chr(ord(char)+5)
        else:
            new_string += char
    return new_string

variable = "a"
def improve_alpha(string):
    global variable
    if string[0] == "/":
        head = string[:2]
        body = string[2:]
        own_variable = variable
        variable = chr(ord(variable)+1)
        body, string = improve_alpha(body)
        #print head[1], body, own_variable
        body = body.replace(head[1], own_variable)
        head = "/"+own_variable
        #print head, body
        return head+body, string
    elif string[0] == "-":
        head = string[0]
        operator = string[1:]
        operator, string = improve_alpha(operator)
        operand = string
        operand, string = improve_alpha(operand)
        return head+operator+operand, string
    else:
        return string[0], string[1:]

def lambdaeval(string, replace=None):
    if string == "":
        return string
    if string[0] == "/":
        head = string[:2]
        body = string[2:]
        body_processed, string = lambdaeval(body, replace=replace)
        #print "Abstraction: "+head+", "+body_processed
        return head+body_processed, string
    elif string[0] == "-":
        returnstring = string[0]
        operator, string = lambdaeval(string[1:], replace=replace)
        operand, string = lambdaeval(string, replace=replace)
        #print "Application: "+operator+", "+operand
        if replace == None:#Don't replace when there is already a replacement in progress
            if operator[0] == "/":#Check whether the operator is an abstraction and can thus be applied
                replacechar = operator[1]
                replacestring = operand
                result, a = lambdaeval(operator, replace=(replacechar, replacestring))
                result = result[2:]#Cap off the abstraction variable
                simplified_result, a = lambdaeval(result)#Check for newly created applications (and execute them)
                return simplified_result, string
        return returnstring+operator+operand, string
    else:
        if replace != None:
            if string[0] == replace[0]:
                return replace[1], string[1:]
            else:
                return string[0], string[1:]
        else:
            return string[0], string[1:]

def input_eval(string):
    global variable
    transformed_exp = "-"*(len(string)-1)
    for char in string:
        transformed_exp += symbols[char]
    string = transformed_exp
    result = lambdaeval(improve_alpha(string.upper())[0])[0]
    variable = "a"
    result = improve_alpha(result.upper())
    variable = "a"
    result = result[0].lower()
    if result in reverse_symbols.keys():
        return reverse_symbols[result]
    return None

a = "/f/xx"
b = "/f/x-"

symbols = { "a": "/a/bb", "b": "/a/ba", "c": "/a/b/c--cba", "d": "/a--a/b/cc/d/ed", "e": "/a/b--ba/c/dd", "f": "/ab", "g": "/aa" }
reverse_symbols = {v:k for k, v in symbols.items()}

class Symbol:

    def __init__(self, symbol_img, symbol_img_highlighted, x, y, char):
        self.x = x
        self.y = y
        self.sprite = pyglet.sprite.Sprite(symbol_img, x, y)
        self.sprite_highlighted = pyglet.sprite.Sprite(symbol_img_highlighted, x, y)
        self.highlighted = False
        self.char = char

    def draw(self):
        if self.highlighted:
            self.sprite_highlighted.draw()
        else:
            self.sprite.draw()

    def on_mouse_motion(self, x, y):
        if (x > self.x) and (y > self.y) and (x < self.x+self.sprite.width) and (y < self.y+self.sprite.height):
            self.highlighted = True
        else:
            self.highlighted = False

    def copy_symbol(self):
        return Symbol(self.sprite.image, self.sprite_highlighted.image, self.x, self.y, self.char)

    def on_mouse_press(self, x, y, button):
        self.on_mouse_motion(x, y)
        if self.highlighted:
            return self.copy_symbol()
        else:
            return None

    def update_coords(self):
        self.sprite.x, self.sprite.y = self.sprite_highlighted.x, self.sprite_highlighted.y = self.x, self.y

class Box:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 73
        self.height = 128
        self.vertexlist = pyglet.graphics.vertex_list_indexed(4, [0, 1, 2, 0, 2, 3],
                ('v2i', (self.x, self.y, self.x+self.width, self.y, self.x+self.width, self.y+self.height, self.x, self.y+self.height)),
                ('c4f', (0.2, 0.2, 0.2, 1.0)*4)
                )
        self.symbol = None

    def draw(self):
        self.vertexlist.draw(pyglet.gl.GL_TRIANGLES)
        if self.symbol:
            self.symbol.draw()

    def assign_symbol(self, symbol):
        self.symbol = symbol
        self.symbol.x = self.x
        self.symbol.y = self.y
        self.symbol.update_coords()

    def on_mouse_release(self, x, y):
        if (x > self.x) and (y > self.y) and (x < self.x+self.width) and (y < self.y+self.height):
            self.assign_symbol(drag_symbol)

    def on_mouse_motion(self, x, y):
        if self.symbol:
            self.symbol.on_mouse_motion(x, y)

    def on_mouse_press(self, x, y, button):
        if self.symbol:
            copy_symbol = self.symbol.on_mouse_press(x, y, button)
            if copy_symbol:
                self.symbol = None
                return copy_symbol

class MenuItem:

    def __init__(self, img, img_highlighted, x, y, click_action):
        self.x = x
        self.y = y
        self.sprite = pyglet.sprite.Sprite(img, x, y)
        self.sprite_highlighted = pyglet.sprite.Sprite(img_highlighted, x, y)
        self.highlighted = False
        self.click_action = click_action

    def draw(self):
        if self.highlighted:
            self.sprite_highlighted.draw()
        else:
            self.sprite.draw()

    def on_mouse_motion(self, x, y):
        if (x > self.x) and (y > self.y) and (x < self.x+self.sprite.width) and (y < self.y+self.sprite.height):
            if self.highlighted == False:
                self.highlighted = True
                grab_sound.play()
        else:
            self.highlighted = False

    def on_mouse_press(self, x, y, button):
        if self.highlighted:
            self.click_action()
            drop_sound.play()

window = pyglet.window.Window(640, 480)
symbols_image = pyglet.image.load("symbols.png")
symbols_highlighted_image = pyglet.image.load("symbols_highlighted.png")
symbol_grid = pyglet.image.ImageGrid(symbols_image, 1, 7)
symbol_highlighted_grid = pyglet.image.ImageGrid(symbols_highlighted_image, 1, 7)
a = Symbol(symbol_grid[0], symbol_highlighted_grid[0], 0, 0, "a")
symbol_list = []
for i in range(7):
    symbol_list.append(Symbol(symbol_grid[i], symbol_highlighted_grid[i], 12+i*73, 12, chr(ord("a")+i)))

box_list = []
for i in range(4):
    box_list.append(Box(32+i*83, 256))

result_box = Box(530, 256)

drag_symbol = None

grab_sound = pyglet.media.load("grab.wav", streaming=False)
drop_sound = pyglet.media.load("drop.wav", streaming=False)

def play_action():
    global menu
    menu = False

menu = True
lang_image = pyglet.image.load("lang.png")
lang_item = MenuItem(lang_image, lang_image, window.width/2-lang_image.width/2, 353, lambda: 1)
play_item = MenuItem(pyglet.image.load("play.png"), pyglet.image.load("play_highlighted.png"), lang_item.x, 189, play_action)
exit_item = MenuItem(pyglet.image.load("exit.png"), pyglet.image.load("exit_highlighted.png"), lang_item.x, 0, pyglet.app.exit)
#menu_image = pyglet.image.load("menu.png")
#menu_image.anchor_x = menu_image.width/2
#menu_image.anchor_y = menu_image.height/2
#menu_sign = pyglet.sprite.Sprite(menu_image, window.width/2, window.height/2)
#menu_hover = None

@window.event
def on_draw():
    window.clear()
    if menu:
        lang_item.draw()
        play_item.draw()
        exit_item.draw()
    else:
        for box in box_list:
            box.draw()
        result_box.draw()
        for symbol in symbol_list:
            symbol.draw()
        if drag_symbol:
            drag_symbol.draw()

@window.event
def on_mouse_motion(x, y, dx, dy):
    global menu_hover
    if menu:
        play_item.on_mouse_motion(x, y)
        exit_item.on_mouse_motion(x, y)
    else:
        for obj in symbol_list+box_list:
            obj.on_mouse_motion(x, y)

@window.event
def on_mouse_press(x, y, button, modifiers):
    global drag_symbol
    global menu
    if menu:
        play_item.on_mouse_press(x, y, button)
        exit_item.on_mouse_press(x, y, button)
    else:
        for obj in symbol_list+box_list:
            drag_symbol = obj.on_mouse_press(x, y, button)
            if drag_symbol != None:
                grab_sound.play()
                break

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    if drag_symbol:
        drag_symbol.x += dx
        drag_symbol.y += dy
        drag_symbol.update_coords()

@window.event
def on_mouse_release(x, y, button, modifiers):
    global drag_symbol
    if drag_symbol:
        for box in box_list:
            box.on_mouse_release(x, y)
        drag_symbol = None
        drop_sound.play()
    update_result()

def update_result():
    exp = ""
    for box in box_list:
        if box.symbol != None:
            exp += box.symbol.char
    if exp == "":
        result_box.symbol = None
    else:
        result = input_eval(exp)
        #print result
        if result == None:
            result_box.symbol = None
        else:
            for symbol in symbol_list:
                if symbol.char == result:
                    break
            result_box.assign_symbol(symbol.copy_symbol())

#exp = raw_input("")
#length = len(exp)
#new_exp = "-"*(length-1)
#for char in exp:
#    new_exp += symbols[char]
#result = input_eval(exp)
#print result
pyglet.app.run()
