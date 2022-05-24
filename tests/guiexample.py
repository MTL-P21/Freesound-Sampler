import pygame

window_width = 800
window_height = 600
scene = 0

# Globals to store
Query = ""
selected_license = ""
License = ""
Brightness = 0
Warmth = 0
Hardness = 0
SlidersResults = [Brightness, Warmth, Hardness]


class Slider:
    def __init__(self, x, y, w, h, pos):
        self.circle_x = x
        self.volume = 0
        self.sliderRect = pg.Rect(x, y, w, h)
        self.selected = False;
        self.pos = pos;

    def draw(self, screen):
        pg.draw.rect(screen, (COLOR_4), self.sliderRect)
        pg.draw.circle(screen, (COLOR_6), (self.circle_x, (self.sliderRect.h / 2 + self.sliderRect.y)),
                       self.sliderRect.h * 0.5)

    def get_pos(self):
        return self.pos

    def get_volume(self):
        return self.volume

    def get_selected(self):
        return self.selected

    def select(self):
        self.selected = True

    def unselect(self):
        self.selected = False

    def set_volume(self, num):
        self.volume = num

    def update_volume(self, x):
        if x < self.sliderRect.x:
            self.volume = 0
        elif x > self.sliderRect.x + self.sliderRect.w:
            self.volume = 100
        else:
            self.volume = int((x - self.sliderRect.x) / float(self.sliderRect.w) * 100)

    def on_slider(self, x, y):
        if self.on_slider_hold(x,
                               y) or self.sliderRect.x <= x <= self.sliderRect.x + self.sliderRect.w and self.sliderRect.y <= y <= self.sliderRect.y + self.sliderRect.h:
            return True
        else:
            return False

    def on_slider_hold(self, x, y):
        if ((x - self.circle_x) * (x - self.circle_x) + (y - (self.sliderRect.y + self.sliderRect.h / 2)) * (
                y - (self.sliderRect.y + self.sliderRect.h / 2))) \
                <= (self.sliderRect.h * 1.5) * (self.sliderRect.h * 1.5):
            return True
        else:
            return False

    def handle_event(self, screen, x):
        if x < self.sliderRect.x:
            self.circle_x = self.sliderRect.x
        elif x > self.sliderRect.x + self.sliderRect.w:
            self.circle_x = self.sliderRect.x + self.sliderRect.w
        else:
            self.circle_x = x
        self.draw(screen)
        self.update_volume(x)
        # print(self.volume)


class OptionBox:
    def __init__(self, x, y, w, h, color, highlight_color, font, option_list, selected=0):
        self.color = color
        self.highlight_color = highlight_color
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.option_list = option_list
        self.selected = selected
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(self, surf):
        pygame.draw.rect(surf, self.highlight_color if self.menu_active else self.color, self.rect)
        pygame.draw.rect(surf, (0, 0, 0), self.rect, 2)
        msg = self.font.render(self.option_list[self.selected], 1, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center=self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.option_list):
                rect = self.rect.copy()
                rect.y += (i + 1) * self.rect.height
                pygame.draw.rect(surf, self.highlight_color if i == self.active_option else self.color, rect)
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center=rect.center))
            outer_rect = (
                self.rect.x, self.rect.y + self.rect.height, self.rect.width, self.rect.height * len(self.option_list))
            pygame.draw.rect(surf, (0, 0, 0), outer_rect, 2)

    def update(self, event_list):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)

        self.active_option = -1
        for i in range(len(self.option_list)):
            rect = self.rect.copy()
            rect.y += (i + 1) * self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.selected = self.active_option
                    self.draw_menu = False
                    return self.active_option
        return -1


import pygame as pg


class DropDown():

    def __init__(self, color_menu, color_option, x, y, w, h, font, main, options):
        self.color_menu = color_menu
        self.color_option = color_option
        self.rect = pg.Rect(x, y, w, h)
        self.font = font
        self.main = main
        self.options = options
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(self, surf):
        pg.draw.rect(surf, self.color_menu[self.menu_active], self.rect, 0)
        msg = self.font.render(self.main, 1, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center=self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.options):
                rect = self.rect.copy()
                rect.y += (i + 1) * self.rect.height
                pg.draw.rect(surf, self.color_option[1 if i == self.active_option else 0], rect, 0)
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center=rect.center))

    def update(self, event_list):
        mpos = pg.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)

        self.active_option = -1
        for i in range(len(self.options)):
            rect = self.rect.copy()
            rect.y += (i + 1) * self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.draw_menu = False
                    return self.active_option
        return -1


class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_6
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False
        self.initialTxt = text

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.text == self.initialTxt:
                self.text = ''
                self.txt_surface = FONT.render(self.text, True, self.color)
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_1 if self.active else COLOR_6
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    print(self.text)
                    #self.text = ''
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pg.draw.rect(screen, self.color, self.rect, 2)

    def getText(self):
        return self.text


class button:
    def __init__(self, position, size, clr=[100, 100, 100], cngclr=None, func=None, text='', font="Segoe Print",
                 font_size=16, font_clr=[0, 0, 0]):
        self.clr = clr
        self.size = size
        self.func = func
        self.surf = pygame.Surface(size)
        self.rect = self.surf.get_rect(center=position)

        if cngclr:
            self.cngclr = cngclr
        else:
            self.cngclr = clr

        if len(clr) == 4:
            self.surf.set_alpha(clr[3])

        self.font = pygame.font.SysFont(font, font_size)
        self.txt = text
        self.font_clr = font_clr
        self.txt_surf = self.font.render(self.txt, 1, self.font_clr)
        self.txt_rect = self.txt_surf.get_rect(center=[wh // 2 for wh in self.size])

    def draw(self, screen):
        self.mouseover()

        self.surf.fill(self.curclr)
        self.surf.blit(self.txt_surf, self.txt_rect)
        screen.blit(self.surf, self.rect)

    def mouseover(self):
        self.curclr = self.clr
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.curclr = self.cngclr

    def call_back(self, *args):
        if self.func:
            return self.func(*args)


class text:
    def __init__(self, msg, position, clr=[100, 100, 100], font="Segoe Print", font_size=15, mid=False):
        self.position = position
        self.font = pygame.font.SysFont(font, font_size)
        self.txt_surf = self.font.render(msg, 1, clr)

        if len(clr) == 4:
            self.txt_surf.set_alpha(clr[3])

        if mid:
            self.position = self.txt_surf.get_rect(center=position)

    def draw(self, screen):
        screen.blit(self.txt_surf, self.position)

    def update(self, val):
        self.txt_surf = self.font.render(val, 1, [100, 100, 100])


# call back functions
def fn1():
    print('button1')


def fn2():
    print('button2')


def fn3():
    global Query
    global selected_license
    global SlidersResults

    print("\n")
    print("Text query: ", Query, "\n")
    print("License option: ", selected_license, "\n")
    print("Brightness: ", SlidersResults[0], "\n")
    print("Warmth: ", SlidersResults[1], "\n")
    print("Hardness: ", SlidersResults[2], "\n")


pg.init()
COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')
FONT = pg.font.Font(None, 32)

pygame.init()
pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode((window_width, window_height))

# COLORS
COLOR_INACTIVE = (151, 186, 169)
COLOR_ACTIVE = (183, 219, 201)
COLOR_LIST_INACTIVE = (151, 186, 169)
COLOR_LIST_ACTIVE = (183, 219, 201)

COLOR_1 = [54, 96, 88]
COLOR_2 = [151, 186, 169]
COLOR_3 = [190, 204, 204]
COLOR_4 = [238, 223, 206]
COLOR_5 = [241, 176, 143]
COLOR_6 = [216, 134, 91]

list1 = DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    (window_width / 2) - 100, window_height / 3, 190, 50,
    pg.font.SysFont(None, 30),
    "Chnnels", ["Single Channel", "Dual Channel"])

typeList1 = DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    (window_width / 2) - 300, window_height / 3, 190, 50,
    pg.font.SysFont(None, 30),
    "Format", ["wav", "aiff", "ogg", "mp3", "m4a", "flac"])

licenceList1 = DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    80, 175, 190, 50,
    pg.font.SysFont(None, 20),
    "License", ["Attribution ", " Attribution Noncommercial", "Creative Commons 0"])

input_box1 = InputBox(300, 100, 140, 32, "Query")
input_box2 = InputBox(100, 300, 140, 32, "Tags")

input_boxes = [input_box1]

button1 = button(position=(400, 400), size=(100, 50), clr=(220, 220, 220), cngclr=(255, 0, 0), func=fn3, text='Next')
button_list = [button1];

# Sliders
BrightnessSlider = Slider(600, 200, 150, 10, 0);
WarmthSlider = Slider(600, 250, 150, 10, 1);
HardnessSlider = Slider(600, 300, 150, 10, 2);
sliders = [BrightnessSlider, WarmthSlider, HardnessSlider]
# Sliders text
BrightnessTAG = text("Brightness", [510, 197], font_size=23)
WarmthTAG = text("Warmth", [510, 247], font_size=23)
HardnessTAG = text("Hardness", [510, 297], font_size=23)
SliderTAGs = [BrightnessTAG, WarmthTAG, HardnessTAG]
# Sliders Values
BrightnessValue = text("0", [760, 200], font_size=23)
WarmthValue = text("0", [760, 250], font_size=23)
HardnessValue = text("0", [760, 300], font_size=23)
SliderValues = [BrightnessValue, WarmthValue, HardnessValue];

selected_license = ""

# Main Loop
while scene == 0:
    screen.fill(COLOR_3)
    pygame.display.set_caption('Query and tags')

    event_list = pg.event.get()
    for event in event_list:
        if event.type == pg.QUIT:
            done = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for s in sliders:
                if s.on_slider_hold(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
                    s.select()
            if event.button == 1:
                pos = pygame.mouse.get_pos()
                for b in button_list:
                    if b.rect.collidepoint(pos):
                        b.call_back()
        for s in sliders:
            if s.get_selected():
                s.handle_event(screen, pygame.mouse.get_pos()[0])
                SlidersResults[s.get_pos()] = s.get_volume()
                SliderValues[s.get_pos()].update(str(s.get_volume()))
        if event.type == pygame.MOUSEBUTTONUP:
            for s in sliders:
                s.unselect()
        for box in input_boxes:
            box.handle_event(event)
            Query=box.getText()
    License = licenceList1.update(event_list)

    if License >= 0:
        licenceList1.main = licenceList1.options[License]
        selected_license = licenceList1.main

        # print(pygame.mouse.get_pos()[0]);

    for box in input_boxes:
        box.update()

    for box in input_boxes:
        box.draw(screen)
    for b in button_list:
        b.draw(screen)
    for s in sliders:
        s.draw(screen)
    licenceList1.draw(screen)
    for t in SliderTAGs:
        t.draw(screen)
    for v in SliderValues:
        v.draw(screen)

    pygame.display.update()
    pg.display.flip()
    clock.tick(30)

# run = false;

while scene == 1:
    pygame.display.set_caption('Filters')
    clock.tick(30)

    event_list = pg.event.get()
    for event in event_list:
        if event.type == pg.QUIT:
            run = False

    selected_option = list1.update(event_list)
    selected_type = typeList1.update(event_list)
    selected_licence = licenceList1.update(event_list)
    if selected_option >= 0:
        list1.main = list1.options[selected_option]
        print(list1.main)
    if selected_type >= 0:
        typeList1.main = typeList1.options[selected_type]
        print(typeList1.main)
    if selected_licence >= 0:
        licenceList1.main = licenceList1.options[selected_licence]
        print(licenceList1.main)

    screen.fill((255, 255, 255))
    list1.draw(screen)
    typeList1.draw(screen)
    licenceList1.draw(screen)
    pg.display.flip()

pg.quit()
exit()
