from cmu_graphics import *
import time
import string
import os
import random

fontSize = 20
characterWidth = (fontSize*3)//5

class Textbox:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = ''
        self.maxChars = self.w//characterWidth - 1
        self.viewIndex = 0
        self.cursorIndex = 0

    def draw(self, app):
        drawRect(self.x, self.y, self.w, self.h, fill=None,
                    border=app.steelGray, borderWidth=2)
        drawLabel(self.text[self.viewIndex:self.viewIndex+self.maxChars],
                    self.x+characterWidth, self.y+self.h/2,
                    align='left', fill=app.steelGray, size=fontSize,
                    font='monospace')

    def blinkCursor(self):
        offset = len(
                    self.text[self.viewIndex:self.cursorIndex]
                    ) * characterWidth + characterWidth
        drawLine(self.x + offset, self.y+characterWidth,
                self.x + offset, self.y+self.h-characterWidth,
                fill='white', lineWidth=1)

    def shiftCursor(self, steps):
        if 0 <= self.cursorIndex + steps <= len(self.text):
            self.cursorIndex += steps
            if self.cursorIndex > self.viewIndex+self.maxChars \
            or self.cursorIndex < self.viewIndex:
                self.viewIndex += steps
        elif self.cursorIndex + steps < 0:
            self.cursorIndex = self.viewIndex
        elif self.cursorIndex + steps > len(self.text):
            self.cursorIndex = len(self.text)

    def checkMouseClick(self, mouseX, mouseY):
        if not (self.x+characterWidth < mouseX < self.x + self.w \
            - characterWidth and self.y < mouseY < self.y + self.h):
            return
        self.shiftCursor(
            int((mouseX-self.x-characterWidth/2)/characterWidth)
            + self.viewIndex - self.cursorIndex)
        return True

    def write(self, data):
        self.text = self.text[:self.cursorIndex] + data + \
                    self.text[self.cursorIndex:]
        self.shiftCursor(1)

    def erase(self):
        self.text = self.text[:self.cursorIndex-1] + \
                    self.text[self.cursorIndex:]
        self.shiftCursor(-1)

    def copyToClipboard(self):
        os.system(f'echo -n {self.text} | xsel --clipboard')

class PasswordField(Textbox):
    def generatePassword(self, length):
        password = ''
        characters = string.ascii_letters + string.digits + string.punctuation
        for i in range(length):
            password += random.choice(characters)
        self.text = password

class Button:
    def __init__(self, x, y, w, h, action, label=''):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.action = action
        self.label = label

    def draw(self, app):
        drawRect(self.x, self.y, self.w, self.h, fill=None,
                    border=app.steelGray)
        if self.label:
            drawLabel(self.label, self.x + characterWidth,
            self.y + characterWidth, align='top-left', fill=app.steelGray,
            size=fontSize)

    def checkMouseClick(self, mouseX, mouseY):
        if self.x < mouseX < self.x + self.w and \
        self.y < mouseY < self.y + self.h:
            self.action(16) # passing constant length for now

def reset(app):
    app.stepsPerSecond = 60
    app.steps = 0
    app.keyHoldSpeed = app.stepsPerSecond//8 # 8 presses a second
    app.keyHoldCounter = 0

    app.ironGray = rgb(52,52,50)
    app.steelGray = gradient(rgb(153,158,152), rgb(203,205,205),
                            start='top-left')

    app.textboxes = [
        Textbox(app.width/2-500/2-50, 200, 500, 50), # Title box
        Textbox(app.width/2-500/2-50, 280, 500, 50), # Username box
        PasswordField(app.width/2-500/2-50, 360, 500, 50) # Password box
    ]

    app.buttons = [
        Button(app.width/2+220, 365, 40, 40, app.textboxes[2].generatePassword),
        Button(app.width/2-500/2-50, 440, 120, 40, print, 'Save Entry')
    ]

    app.inFocusTB = 0

def onAppStart(app):
    reset(app)

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill=app.ironGray)
    for textbox in app.textboxes:
        textbox.draw(app)
    for button in app.buttons:
        button.draw(app)
    if 0 < app.steps % app.stepsPerSecond < app.stepsPerSecond//2:
        app.textboxes[app.inFocusTB].blinkCursor()

def onStep(app):
    app.steps += 1
    if app.keyHoldCounter:
        app.keyHoldCounter -= 1

def onKeyHold(app, keys):
    if app.keyHoldCounter == 0:
        if 'backspace' in keys:
            app.textboxes[app.inFocusTB].erase()
        elif 'right' in keys:
            app.textboxes[app.inFocusTB].shiftCursor(1)
        elif 'left' in keys:
            app.textboxes[app.inFocusTB].shiftCursor(-1)
        app.keyHoldCounter = app.keyHoldSpeed

def onKeyPress(app, key, modifiers):
    if key == 'backspace':
        app.keyHoldCounter = 0
    elif key == 'tab':
        if 'shift' in modifiers:
            app.inFocusTB -= 1 if app.inFocusTB > 0 else 0
        else:
            app.inFocusTB += 1 if app.inFocusTB < len(app.textboxes)-1 else 0
    elif key == 'space':
        app.textboxes[app.inFocusTB].write(' ')
    elif key in string.printable:
        app.textboxes[app.inFocusTB].write(key)

def onMousePress(app, mouseX, mouseY):
    for i in range(len(app.textboxes)):
        if app.textboxes[i].checkMouseClick(mouseX, mouseY):
            app.inFocusTB = i
    for i in range(len(app.buttons)):
        app.buttons[i].checkMouseClick(mouseX, mouseY)

runApp(width=800, height=600)