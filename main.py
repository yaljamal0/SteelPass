from cmu_graphics import *
import time
import string

class Element:
    def checkMouseClick(self, mouseX, mouseY):
        if self.x < mouseX < self.x + self.w and \
            self.y < mouseY < self.y + self.h:
            return True
        return False

class Textbox(Element):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = '  '

    def draw(self, app):
        drawRect(self.x, self.y, self.w, self.h, fill=None,
                    border=app.steelGray, borderWidth=2)
        drawLabel(self.text[::-1][:self.w//14][::-1], self.x+self.w/10,
                    self.y+self.h/2, align='left', fill=app.steelGray, size=24)

    def blinkCursor(self, clear=False):
        if self.text.endswith('| ') or clear:
            self.text = self.text[:-2] + '  '
        else:
            self.text = self.text[:-2] + '| '

    def write(self, data):
        self.text = self.text[:-2] + data + self.text[-2:]

    def erase(self):
        self.text = self.text[:-3] + self.text[-2:]

def onAppStart(app):
    app.ironGray = rgb(109, 110, 113)
    app.steelGray = rgb(224, 224, 224)

    app.steps = 0

    titleBox = Textbox(app.width/2-500/2, \
        200, 500, 50)
    usernameBox = Textbox(app.width/2-500/2, \
        280, 500, 50)
    passwordBox = Textbox(app.width/2-500/2, \
        360, 500, 50)
    app.textboxes = [titleBox, usernameBox, passwordBox]
    app.inFocusTB = 0

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill=app.ironGray)
    for textbox in app.textboxes:
        textbox.draw(app)

def onStep(app):
    app.steps += 1
    if app.steps % 30 == 0:
        app.textboxes[app.inFocusTB].blinkCursor()

def onKeyHold(app, keys):
    if 'backspace' in keys:
        app.textboxes[app.inFocusTB].erase()
        time.sleep(0.1)

def onKeyPress(app, key):
    if key == 'up':
        app.textboxes[app.inFocusTB].blinkCursor(clear=True)
        app.inFocusTB -= 1 if app.inFocusTB > 0 else 0
    elif key == 'down':
        app.textboxes[app.inFocusTB].blinkCursor(clear=True)
        app.inFocusTB += 1 if app.inFocusTB < len(app.textboxes)-1 else 0
    elif key == 'space':
        app.textboxes[app.inFocusTB].write(' ')
    elif key in string.printable:
        app.textboxes[app.inFocusTB].write(key)

def onMousePress(app, mouseX, mouseY):
    for i in range(len(app.textboxes)):
        if app.textboxes[i].checkMouseClick(mouseX, mouseY):
            app.textboxes[app.inFocusTB].blinkCursor(clear=True)
            app.inFocusTB = i

runApp(width=800, height=600)