from cmu_graphics import *
import time
import string
import os
import random
import sqlite3
from PIL import Image

# global constants
fontSize = 20
characterWidth = (fontSize*3)//5
ironGray = rgb(52,52,50)
steelGray = gradient(rgb(153,158,152), rgb(203,205,205), start='top-left')
steelImage = CMUImage(Image.open('steel.jpeg'))

# create a new database and table if they do not already exist
def createDB():
    conn = sqlite3.connect('entries.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            username TEXT,
            password TEXT
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
def addEntry(title, username, password):
    conn = sqlite3.connect('entries.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO entries (title, username, password)
        VALUES (?, ?, ?)
    ''', (title, username, password))
    conn.commit()
    conn.close()
    return c.lastrowid

# update an entry if it has the same title
def updateEntry(entryID, title, username, password):
    conn = sqlite3.connect('entries.db')
    c = conn.cursor()
    c.execute('''
    UPDATE entries
    SET title = ?, username = ?, password = ?
    WHERE id = ?
    ''', (title, username, password, entryID))
    conn.commit()
    conn.close()

class Textbox:
    def __init__(self, x, y, w, h, text='', placeholder=''):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.placeholder = placeholder
        # To shift the view as the textbox gets filled, we define the following
        # three variables:
        # max viewable characters given the width of the textbox
        # the -1 is there to keep distance between the last character
        # in the view and the right rectangle edge
        self.maxChars = self.w//characterWidth - 1
        # index of first character of the viewable part of the entered text
        self.viewIndex = 0
        # index of the blinking cursor that controls the view
        self.cursorIndex = len(text)

    def draw(self):
        drawRect(self.x, self.y, self.w, self.h, fill=None,
                    border=steelGray, borderWidth=2)
        text = self.text[self.viewIndex:self.viewIndex+self.maxChars]
        if hasattr(self, 'hide') and self.hide:
            text = '*' * len(text)
        # start characterWidth pixels to the right after the rectangle left edge
        drawLabel(text, self.x+characterWidth, self.y+self.h/2, align='left',
        fill=steelGray, size=fontSize, font='monospace')
        if not self.text:
            drawLabel(self.placeholder, self.x+characterWidth, self.y+self.h/2,
                      align='left', fill='dimGray', size=fontSize,
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
        if self.cursorIndex > 0:
            self.text = self.text[:self.cursorIndex-1] + \
                        self.text[self.cursorIndex:]
        self.shiftCursor(-1)

    def copyToClipboard(self):
        os.system(f'echo -n {self.text} | xsel --clipboard')

# special textbox that generates passwords
class PasswordField(Textbox):
    def __init__(self, x, y, w, h, text='', placeholder='', hide=True):
        super().__init__(x, y, w, h, text, placeholder)
        self.hide = hide

    def generatePassword(self, length, uppers, lowers, nums, specials):
        if not length.isdigit():
            return
        length = int(length)
        password = ''
        characters = ''
        characters += string.ascii_uppercase if uppers else ''
        characters += string.ascii_lowercase if lowers else ''
        characters += string.digits if nums else ''
        characters += string.punctuation if specials else ''
        if characters:
            for i in range(length):
                password += random.choice(characters)
        self.text = password
        self.viewIndex = 0
        self.cursorIndex = len(self.text)

class Button:
    def __init__(self, x, y, w, h, content, action, hover=False):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.content = content
        # callback function that the button will run on click
        self.action = action
        #self.fill = steelGray if active else None
        #self.fontColor = 'black' if active else steelGray
        self.hover = hover

    def draw(self):
        fill = steelGray if self.hover else None
        fontColor = 'black' if self.hover else steelGray

        drawRect(self.x, self.y, self.w, self.h, fill=fill,
                 border=steelGray)
        if self.content:
            drawLabel(self.content, self.x+self.w/2, self.y+self.h/2,
                      fill=fontColor, size=fontSize, font='monospace')

    def checkBounds(self, x, y):
        if self.x < x < self.x + self.w and \
        self.y < y < self.y + self.h:
            return True

    def checkMouseClick(self, mouseX, mouseY):
        if self.checkBounds(mouseX, mouseY):
            self.action()

    def unhover(self):
        self.hover = False

class ActivateButton(Button):
    def __init__(self, *args):
        super().__init__(*args)
        self.fill = steelGray
        self.fontColor = 'black'

    def activate(self):
        if self.fill == None:
            self.fill = steelGray
            self.fontColor = 'black'
        else:
            self.fill = None
            self.fontColor = steelGray

    def draw(self):
        drawRect(self.x, self.y, self.w, self.h, fill=self.fill,
                 border=steelGray)
        if self.content:
            drawLabel(self.content, self.x+self.w/2, self.y+self.h/2,
                      fill=self.fontColor, size=fontSize, font='monospace')

# a form is a view or window that houses specific elements
class Form:
    def __init__(self, app, w, h):
        self.w = w
        self.h = h
        # center all forms
        self.x = app.width/2-self.w/2
        self.y = app.height/2-self.h/2

    def draw(self, opacity=10, border=None):
        drawRect(self.x, self.y, self.w, self.h, fill='black')
        drawImage(steelImage, self.x, self.y, width=self.w, height=self.h, opacity=opacity, border=border)

class FloatingForm(Form):
    def __init__(self, app, w, h):
        super().__init__(app, w, h)

        self.textboxes = [
            Textbox(20, 20, 200, 40, '', 'Search...')
        ]
        self.inFocusTB = 0

        self.buttons = [
            Button(app.width-60, 20, 40, 40, 'N', lambda: (self.buttons[0].unhover(), NewEntryForm(app, 0.9*app.width, 0.9*app.height))),
            Button(app.width-120, 20, 40, 40, 'E', lambda: (self.buttons[0].unhover(), NewEntryForm(app, 0.9*app.width, 0.9*app.height, app.forms[app.inFocusForm].entry))),
            Button(20, app.height/2, 40, 40, '<', lambda: EntryView.changeFormView(app, -1)),
            Button(app.width-60, app.height/2, 40, 40, '>', lambda: EntryView.changeFormView(app, +1))
        ]

    def draw(self, app):
        drawLabel(f'{app.inFocusForm+1}/{len(app.forms)}', self.w/2, 40, size=24, fill=steelGray, font='monospace')
        for textbox in self.textboxes:
            textbox.draw()
        for button in self.buttons:
            button.draw()

class EntryView(Form):
    def __init__(self, app, w, h, entry):
        super().__init__(app, w, h)
        self.entry = entry
        self.textboxes = [
            Textbox(150, 380, 500, 50, entry[2]),
            PasswordField(150, 450, 430, 50, entry[3])
        ]
        # the index of the textbox currently in focus
        self.inFocusTB = 0

        self.buttons = [
            ActivateButton(600, 450, 50, 50, 'H', lambda: (self.hidePassword(), self.buttons[0].activate()))
        ]

    def hidePassword(self):
        self.textboxes[1].hide = not self.textboxes[1].hide

    @classmethod
    def changeFormView(self, app, steps):
        app.inFocusForm = (app.inFocusForm+steps) % (len(app.forms))

    def draw(self):
        super().draw()
        drawLabel(self.entry[1], self.w/2, self.h/3, size=64, fill=steelGray, font='monospace')
        for textbox in self.textboxes:
            textbox.draw()
        for button in self.buttons:
            button.draw()

class NewEntryForm(Form):
    def __init__(self, app, w, h, prevEntry=None):
        super().__init__(app, w, h)

        if prevEntry:
            title, username, password = prevEntry[1], prevEntry[2], prevEntry[3]
        else:
            title, username, password = '', '', ''

        self.textboxes = [
            Textbox(app.width/2-500/2-50, 150, 500, 50, title, 'Title'), # Title box
            Textbox(app.width/2-500/2-50, 230, 500, 50, username, 'Username'), # Username box
            PasswordField(app.width/2-500/2-50, 310, 430, 50, password, 'Password', False), # Password box
            Textbox(620, 310, 50, 50, '16')
        ]
        # the index of the textbox currently in focus
        self.inFocusTB = 0

        self.updatePasswordGen(True, True, True, True)

        self.buttons = [
            Button(app.width/2+150, 310, 50, 50, 'G',
                   lambda: self.textboxes[2].generatePassword(self.textboxes[3].text, self.uppers, self.lowers, self.nums, self.specials)),
            ActivateButton(100, 395, 100, 50, 'A-Z', lambda: (self.updatePasswordGen(uppers=not self.uppers), self.buttons[1].activate())),
            ActivateButton(230, 395, 100, 50, 'a-z', lambda: (self.updatePasswordGen(lowers=not self.lowers), self.buttons[2].activate())),
            ActivateButton(360, 395, 100, 50, '0-9', lambda: (self.updatePasswordGen(nums=not self.nums), self.buttons[3].activate())),
            ActivateButton(490, 395, 100, 50, '/*+&...', lambda: (self.updatePasswordGen(specials=not self.specials), self.buttons[4].activate())),
            Button(440, 480, 120, 40, 'Cancel', lambda: self.kill(app)),
            Button(580, 480, 120, 40, 'Save',
                   lambda: self.saveEntry(app))
        ]

        #self.prevFormIndex = prevFormIndex
        #app.forms.insert(prevFormIndex+1, self)
        #app.inFocusForm = prevFormIndex+1
        app.forms.insert(app.inFocusForm, self)
        self.prevEntry = prevEntry

    def updatePasswordGen(self, uppers=None, lowers=None, nums=None, specials=None):
        self.uppers = uppers if uppers != None else self.uppers
        self.lowers = lowers if lowers != None else self.lowers
        self.nums = nums if nums != None else self.nums
        self.specials = specials if specials != None else self.specials

    def draw(self):
        super().draw(30, 'white')
        for textbox in self.textboxes:
            textbox.draw()
        for button in self.buttons:
            button.draw()

    def saveEntry(self, app):
        title = self.textboxes[0].text
        username = self.textboxes[1].text
        password = self.textboxes[2].text

        if self.prevEntry:
            prevEntryID = self.prevEntry[0]
            updateEntry(prevEntryID, title, username, password)
            loadEntries(app, prevEntryID)
        else:
            entryID = addEntry(title, username, password)
            loadEntries(app, entryID)

    def kill(self, app):
        #app.inFocusForm = self.prevFormIndex
        app.forms.remove(self)

def loadEntries(app, focusEntryID=0):
    app.forms = []
    entries = getEntries()
    for entry in entries:
        app.forms.append(EntryView(app, app.width, app.height, entry))
    app.forms.sort(key=lambda form: form.entry[1].lower())
    app.inFocusForm = len(app.forms)//2
    for i in range(len(app.forms)):
        if app.forms[i].entry[0] == focusEntryID:
            app.inFocusForm = i
            break
    if not app.forms:
        app.forms.append(
            EntryView(app, app.width, app.height, (-1, 'Welcome!', 'Click the + to add your first entry...', 'Enjoy :)'))
        )

def reset(app):
    app.stepsPerSecond = 60
    app.steps = 0
    app.keyHoldSpeed = app.stepsPerSecond//8 # 8 presses a second
    app.keyHoldCounter = 0

    loadEntries(app)

    app.floatingForm = FloatingForm(app, app.width, app.height)

def onAppStart(app):
    reset(app)

def redrawAll(app):
    form = app.forms[app.inFocusForm]
    if type(form) == NewEntryForm:
        app.forms[app.inFocusForm+1].draw()
        app.floatingForm.draw(app)
        form.draw()
    else:
        form.draw()
        app.floatingForm.draw(app)
    if 0 < app.steps % app.stepsPerSecond < app.stepsPerSecond//2:
        if type(form) == NewEntryForm:
            form.textboxes[form.inFocusTB].blinkCursor()
        else:
            app.floatingForm.textboxes[0].blinkCursor()

def onStep(app):
    app.steps += 1
    if app.keyHoldCounter:
        app.keyHoldCounter -= 1

def onKeyHold(app, keys):
    form = app.forms[app.inFocusForm]
    if type(form) == EntryView:
        form = app.floatingForm
    if app.keyHoldCounter == 0:
        if 'backspace' in keys:
            form.textboxes[form.inFocusTB].erase()
        elif 'right' in keys:
            form.textboxes[form.inFocusTB].shiftCursor(1)
        elif 'left' in keys:
            form.textboxes[form.inFocusTB].shiftCursor(-1)
        app.keyHoldCounter = app.keyHoldSpeed

def onKeyPress(app, key, modifiers):
    form = app.forms[app.inFocusForm]
    if type(form) == EntryView:
        if key == 'right':
            EntryView.changeFormView(app, 1)
        if key == 'left':
            EntryView.changeFormView(app, -1)
        form = app.floatingForm
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
    for button in form.buttons:
        button.checkMouseClick(mouseX, mouseY)
    if type(form) == NewEntryForm:
        for i in range(len(form.textboxes)):
            if form.textboxes[i].checkMouseClick(mouseX, mouseY):
                form.inFocusTB = i
    else:
        for button in app.floatingForm.buttons:
            button.checkMouseClick(mouseX, mouseY)
        for textbox in app.floatingForm.textboxes:
            textbox.checkMouseClick(mouseX, mouseY)

def onMouseMove(app, mouseX, mouseY):
    form = app.forms[app.inFocusForm]
    for button in form.buttons:
        button.hover = button.checkBounds(mouseX, mouseY)
    if type(form) != NewEntryForm:
        for button in app.floatingForm.buttons:
            button.hover = button.checkBounds(mouseX, mouseY)

createDB()
runApp(width=800, height=600)