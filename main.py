from cmu_graphics import *
import time
import string
import os
import random
import sqlite3

# create a new database and table if they do not already exist
def createDB():
    conn = sqlite3.connect('entries.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            color TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# get all entries from table
def getEntries():
    conn = sqlite3.connect('entries.db')
    c = conn.cursor()
    c.execute('SELECT * FROM entries')
    entries = c.fetchall()
    conn.close()
    return entries

# add entry to table
def addEntry(title, username, password, color):
    conn = sqlite3.connect('entries.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO entries (title, username, password, color)
        VALUES (?, ?, ?, ?)
    ''', (title, username, password, color))
    conn.commit()
    conn.close()

# global font variables
fontSize = 20
characterWidth = (fontSize*3)//5

class Textbox:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = ''
        # To shift the view as the textbox gets filled, we define the following
        # three variables:
        # max viewable characters given the width of the textbox
        # the -1 is there to keep distance between the last character
        # in the view and the right rectangle edge
        self.maxChars = self.w//characterWidth - 1
        # index of first character of the viewable part of the entered text
        self.viewIndex = 0
        # index of the blinking cursor that controls the view
        self.cursorIndex = 0

    def draw(self, app):
        drawRect(self.x, self.y, self.w, self.h, fill=None,
                    border=app.steelGray, borderWidth=2)
        # start characterWidth pixels to the right after the rectangle left edge
        drawLabel(self.text[self.viewIndex:self.viewIndex+self.maxChars],
                    self.x+characterWidth, self.y+self.h/2,
                    align='left', fill=app.steelGray, size=fontSize,
                    font='monospace')

    def blinkCursor(self):
        # offset the cursor to the right (+1) of last character
        offset = (len(
                    self.text[self.viewIndex:self.cursorIndex]
                    ) + 1) * characterWidth
        drawLine(self.x + offset, self.y+characterWidth,
                self.x + offset, self.y+self.h-characterWidth,
                fill='white', lineWidth=1)

    def shiftCursor(self, steps):
        # if cursor shift is within text length, shift it by steps
        if 0 <= self.cursorIndex + steps <= len(self.text):
            self.cursorIndex += steps
            # if the cursor exceeds ends of the view, shift the view by steps
            if self.cursorIndex > self.viewIndex+self.maxChars \
            or self.cursorIndex < self.viewIndex:
                self.viewIndex += steps
        # potentially not useful anymore
        #elif self.cursorIndex + steps < 0:
        #    self.cursorIndex = self.viewIndex
        elif self.cursorIndex + steps > len(self.text):
            self.cursorIndex = len(self.text)

    def checkMouseClick(self, mouseX, mouseY):
        # do nothing if click is out of the rectangle
        if not (self.x < mouseX < self.x + self.w \
            and self.y < mouseY < self.y + self.h):
            return
        self.shiftCursor(
            # calculate press location before and after exactly half the width
            # of each character for precision
            int((mouseX-self.x-characterWidth/2)/characterWidth)
            # move by difference between press location index and cursorIndex
            + self.viewIndex - self.cursorIndex)
        return True

    def write(self, data):
        # insert at cursor location
        self.text = self.text[:self.cursorIndex] + data + \
                    self.text[self.cursorIndex:]
        self.shiftCursor(1)

    def erase(self):
        # erase behind cursor location
        self.text = self.text[:self.cursorIndex-1] + \
                    self.text[self.cursorIndex:]
        self.shiftCursor(-1)

    def copyToClipboard(self):
        os.system(f'echo -n {self.text} | xsel --clipboard')

# special textbox that generates passwords
class PasswordField(Textbox):
    def generatePassword(self, length):
        password = ''
        characters = string.ascii_letters + string.digits + string.punctuation
        for i in range(length):
            password += random.choice(characters)
        self.text = password

class Button:
    def __init__(self, x, y, w, h, label, action, *args):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.label = label
        # callback function that the button will run on click
        self.action = action
        # arguments to that function stored in a tuple as they might differ
        self.args = args

    def draw(self, app):
        drawRect(self.x, self.y, self.w, self.h, fill=None,
                    border=app.steelGray)
        if self.label:
            drawLabel(self.label, self.x+self.w/2, self.y+self.h/2,
                      fill=app.steelGray, size=fontSize)

    def checkMouseClick(self, mouseX, mouseY, app):
        if self.x < mouseX < self.x + self.w and \
        self.y < mouseY < self.y + self.h:
            # we use * to parse the args in a tuple
            self.action(*self.args)

# a form is a view or window that houses specific elements
class Form:
    def __init__(self, app, w, h):
        self.w = w
        self.h = h
        # center all forms
        self.x = app.width/2-self.w/2
        self.y = app.height/2-self.h/2
    def draw(self, app, border=None):
        drawRect(self.x, self.y, self.w, self.h, fill=app.ironGray,
                 border=border)

class EntryView(Form):
    def __init__(self, app, w, h, entry):
        super().__init__(app, w, h)
        self.entry = entry
        self.buttons = [
            Button(app.width-60, 20, 40, 40, 'N', lambda: app.forms.append(NewEntryForm(app, 0.8*app.width, 0.8*app.height)))
        ]
    def draw(self, app):
        super().draw(app)
        drawLabel(self.entry[1], self.x + self.w/2, self.y + self.h/2,
                  size=40)
        for button in self.buttons:
            button.draw(app)

class NewEntryForm(Form):
    def __init__(self, app, w, h):
        print('initiating')
        super().__init__(app, w, h)
        self.textboxes = [
            Textbox(app.width/2-500/2-50, 150, 500, 50), # Title box
            Textbox(app.width/2-500/2-50, 230, 500, 50), # Username box
            PasswordField(app.width/2-500/2-50, 310, 500, 50) # Password box
        ]
        # the index of the textbox currently in focus
        self.inFocusTB = 0
        self.buttons = [
            Button(app.width/2+220, 310, 50, 50, '',
                   self.textboxes[2].generatePassword, 16),
            Button(app.width/2-500/2-50, 480, 120, 40, 'Cancel', lambda: self.kill(app)),
            Button(app.width/2-500/2+90, 480, 120, 40, 'Save Entry',
                   self.saveEntry)
        ]
        app.inFocusForm = len(app.forms)
    def draw(self, app):
        super().draw(app, 'white')
        for textbox in self.textboxes:
            textbox.draw(app)
        for button in self.buttons:
            button.draw(app)
    def saveEntry(self):
        title = self.textboxes[0].text
        username = self.textboxes[1].text
        password = self.textboxes[2].text
        addEntry(title, username, password)

def reset(app):
    app.stepsPerSecond = 60
    app.steps = 0
    app.keyHoldSpeed = app.stepsPerSecond//8 # 8 presses a second
    app.keyHoldCounter = 0

    app.ironGray = rgb(52,52,50)
    app.steelGray = gradient(rgb(153,158,152), rgb(203,205,205),
                            start='top-left')

    app.forms = []
    app.forms.append(NewEntryForm(app, 0.8*app.width, 0.8*app.height))
    entries = getEntries()
    for entry in entries:
        app.forms.append(EntryView(app, app.width, app.height, entry))
    app.inFocusForm = 0

def onAppStart(app):
    reset(app)

def redrawAll(app):
    # draw all forms except the focused one
    for i in range(len(app.forms)):
        if i == app.inFocusForm:
            continue
        app.forms[i].draw(app)
    # draw the focused form
    form = app.forms[app.inFocusForm]
    form.draw(app)
    if type(form) == NewEntryForm and \
    0 < app.steps % app.stepsPerSecond < app.stepsPerSecond//2:
        form.textboxes[form.inFocusTB].blinkCursor()

def onStep(app):
    app.steps += 1
    if app.keyHoldCounter:
        app.keyHoldCounter -= 1

def onKeyHold(app, keys):
    if app.keyHoldCounter == 0:
        form = app.forms[app.inFocusForm]
        if 'backspace' in keys:
            form.textboxes[form.inFocusTB].erase()
        elif 'right' in keys:
            form.textboxes[form.inFocusTB].shiftCursor(1)
        elif 'left' in keys:
            form.textboxes[form.inFocusTB].shiftCursor(-1)
        app.keyHoldCounter = app.keyHoldSpeed

def onKeyPress(app, key, modifiers):
    form = app.forms[app.inFocusForm]
    if key == 'backspace':
        app.keyHoldCounter = 0
    elif key == 'tab':
        if 'shift' in modifiers:
            form.inFocusTB -= 1 if form.inFocusTB > 0 else 0
        else:
            form.inFocusTB += 1 if form.inFocusTB < len(form.textboxes)-1 else 0
    elif key == 'space':
        form.textboxes[form.inFocusTB].write(' ')
    elif key in string.printable:
        form.textboxes[form.inFocusTB].write(key)

def onMousePress(app, mouseX, mouseY):
    form = app.forms[app.inFocusForm]
    for i in range(len(form.buttons)):
        form.buttons[i].checkMouseClick(mouseX, mouseY, app)
    #for i in range(len(form.textboxes)):
    #    if form.textboxes[i].checkMouseClick(mouseX, mouseY):
    #        form.inFocusTB = i

createDB()
runApp(width=800, height=600)