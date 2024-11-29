from cmu_graphics import *
import time
import string
import random
import sqlite3
from PIL import Image
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import SHA256
import base64
import pyperclip

# global styling constants
fontSize = 0.025
steelGray = gradient(rgb(153, 158, 152), rgb(203, 205, 205), start='top-left')

# global background and button icons
steelImage = CMUImage(Image.open('assets/steel.jpeg'))
pencilImages = (CMUImage(Image.open('assets/pencil.png')),
                CMUImage(Image.open('assets/steel-pencil.png')))
trashImages = (CMUImage(Image.open('assets/trash.png')),
               CMUImage(Image.open('assets/steel-trash.png')))
plusImages = (CMUImage(Image.open('assets/plus.png')),
              CMUImage(Image.open('assets/steel-plus.png')))
generateImages = (CMUImage(Image.open('assets/generate.png')),
                  CMUImage(Image.open('assets/steel-generate.png')))
hideImages = (CMUImage(Image.open('assets/hide.png')),
              CMUImage(Image.open('assets/steel-hide.png')))
copyImages = (CMUImage(Image.open('assets/copy.png')),
              CMUImage(Image.open('assets/steel-copy.png')))

def encrypt(key, data):
    # hash the key to get a fixed length of 32 bytes for AES
    key = SHA256.new(key.encode('utf-8')).digest()
    # generate a random 16-byte IV
    iv = get_random_bytes(16)
    # create the cipher object
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # pad the message to be a multiple of AES block size (16 bytes)
    paddedData = pad(data.encode('utf-8'), AES.block_size)
    # encrypt the padded message
    ciphertext = cipher.encrypt(paddedData)
    # combine the IV and ciphertext and encode them in base64
    encryptedData = base64.b64encode(iv + ciphertext).decode('utf-8')

    return encryptedData

def decrypt(key, data):
    try:
        # decode base64 encoding
        encryptedData = base64.b64decode(data)
        # get IV (first 16 bytes) and ciphertext (remaining bytes)
        iv = encryptedData[:16]
        ciphertext = encryptedData[16:]
        # hash the key to get a fixed length of 32 bytes for AES
        key = SHA256.new(key.encode('utf-8')).digest()
        # create the cipher object
        cipher = AES.new(key, AES.MODE_CBC, iv)
        # decrypt the ciphertext and remove padding
        decryptedData = unpad(cipher.decrypt(ciphertext), AES.block_size)

        return decryptedData.decode('utf-8')
    except:
        # either the key is invalid or the data is corrupt
        return False

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
def getEntries(masterKey):
    conn = sqlite3.connect('entries.db')
    c = conn.cursor()
    c.execute('SELECT * FROM entries')
    entries = c.fetchall()
    conn.close()
    if not entries:
        return None
    if decrypt(masterKey, entries[0][1]) == False:
        return False
    for i in range(len(entries)):
        entries[i] = (
            entries[i][0],
            decrypt(masterKey, entries[i][1]),
            decrypt(masterKey, entries[i][2]),
            decrypt(masterKey, entries[i][3])
        )
    return entries

# add entry to table
def addEntry(title, username, password, masterKey):
    title = encrypt(masterKey, title)
    username = encrypt(masterKey, username)
    password = encrypt(masterKey, password)
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
def updateEntry(entryID, title, username, password, masterKey):
    title = encrypt(masterKey, title)
    username = encrypt(masterKey, username)
    password = encrypt(masterKey, password)
    conn = sqlite3.connect('entries.db')
    c = conn.cursor()
    c.execute('''
    UPDATE entries
    SET title = ?, username = ?, password = ?
    WHERE id = ?
    ''', (title, username, password, entryID))
    conn.commit()
    conn.close()

def deleteEntry(entryID):
    conn = sqlite3.connect('entries.db')
    c = conn.cursor()
    c.execute('''
    DELETE FROM entries WHERE id = ?
    ''', (entryID,))
    conn.commit()
    conn.close()

class Textbox:
    def __init__(self, app, x, y, w, h, text='', placeholder=''):
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
        adjFontSize = fontSize*app.width
        characterWidth = 3*adjFontSize/5
        self.maxChars = int((self.w*app.width // characterWidth - 1))
        # index of first character of the viewable part of the entered text
        self.viewIndex = 0
        # index of the blinking cursor that controls the view
        self.cursorIndex = len(text)

    def draw(self, app):
        x = self.x * app.width
        y = self.y * app.height
        w = self.w * app.width
        h = self.h * app.height
        adjFontSize = fontSize*app.width
        characterWidth = 3*adjFontSize/5
        drawRect(x, y, w, h, fill=None,
                    border=steelGray, borderWidth=2)
        text = self.text[self.viewIndex:self.viewIndex+self.maxChars]
        if hasattr(self, 'hide') and self.hide:
            text = '*' * len(text)
        # start characterWidth pixels to the right after the rectangle left edge
        drawLabel(text, x+characterWidth, y+h/2, align='left',
        fill=steelGray, size=adjFontSize, font='monospace')
        if not self.text:
            drawLabel(self.placeholder, x+characterWidth, y+h/2,
                      align='left', fill='dimGray', size=adjFontSize*app.width,
                      font='monospace')

    def blinkCursor(self, app):
        x = self.x * app.width
        y = self.y * app.height
        h = self.h * app.height
        adjFontSize = fontSize*app.width
        characterWidth = 3*adjFontSize/5
        # offset the cursor to the right (+1) of last character
        offset = (len(
                    self.text[self.viewIndex:self.cursorIndex]
                    ) + 1) * characterWidth
        drawLine(x + offset, y+characterWidth,
                x + offset, y+h-characterWidth,
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

    def checkMouseClick(self, app, mouseX, mouseY):
        x = self.x * app.width
        y = self.y * app.height
        w = self.w * app.width
        h = self.h * app.height
        adjFontSize = fontSize*app.width
        characterWidth = 3*adjFontSize/5
        # do nothing if click is out of the rectangle
        if not (x < mouseX < x + w \
            and y < mouseY < y + h):
            return
        self.shiftCursor(
            # calculate press location before and after exactly half the width
            # of each character for precision
            int((mouseX-x-characterWidth/2)/characterWidth)
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

    def copyToClipboard(self, app):
        pyperclip.copy(self.text)
        app.clipboardCounter = app.clipboardTime

# special textbox that generates passwords
class PasswordField(Textbox):
    def __init__(self, app, x, y, w, h, text='', placeholder='', hide=True):
        super().__init__(app, x, y, w, h, text, placeholder)
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
        self.hover = hover

    def draw(self, app):
        x = self.x * app.width
        y = self.y * app.height
        w = self.w * app.width
        h = self.h * app.height
        adjFontSize = fontSize*app.width
        fill = steelGray if self.hover else None
        fontColor = 'black' if self.hover else steelGray
        drawRect(x, y, w, h, fill=fill, border=steelGray)
        if type(self.content) == tuple:
            image = self.content[0] if self.hover else self.content[1]
            drawImage(image, x+w/8, y+w/8, width=0.75*w, height=0.75*h)
        else:
            drawLabel(self.content, x+w/2, y+h/2, fill=fontColor,
            size=adjFontSize, font='monospace')

    def checkBounds(self, app, px, py):
        x = self.x * app.width
        y = self.y * app.height
        w = self.w * app.width
        h = self.h * app.height
        if x < px < x + w and y < py < y + h:
            return True

    def checkMouseClick(self, app, mouseX, mouseY):
        if self.checkBounds(app, mouseX, mouseY):
            self.action()

    def unhover(self):
        self.hover = False

class ActivateButton(Button):
    def __init__(self, *args):
        super().__init__(*args)
        self.active = True

    def activate(self):
        self.active = not self.active

    def draw(self, app):
        x = self.x * app.width
        y = self.y * app.height
        w = self.w * app.width
        h = self.h * app.height
        adjFontSize = fontSize*app.width
        fill = steelGray if self.active else None
        fontColor = 'black' if self.active else steelGray
        drawRect(x, y, w, h, fill=fill, border=steelGray)
        if type(self.content) == tuple:
            image = self.content[0] if self.active else self.content[1]
            drawImage(image, x+w/8, y+w/8,
                      width=0.75*w, height=0.75*h)
        else:
            fontColor = 'black' if self.active else steelGray
            drawLabel(self.content, x+w/2, y+h/2, fill=fontColor,
            size=adjFontSize, font='monospace')

# a form is a view or window that houses specific elements
class Form:
    def __init__(self, app, w, h):
        self.w = w
        self.h = h
        # center all forms
        self.x = 1/2 - self.w/2
        self.y = 1/2 - self.h/2

    def draw(self, app, opacity=10, border=None):
        x = self.x * app.width
        y = self.y * app.height
        w = self.w * app.width
        h = self.h * app.height
        drawRect(x, y, w, h, fill='black')
        drawImage(steelImage, x, y, width=w, height=h,
                  opacity=opacity, border=border)

class FloatingForm(Form):
    def __init__(self, app, w, h):
        super().__init__(app, w, h)

        self.textboxes = [
            Textbox(app, 0.025, 0.0333, 0.25, 0.0666, '', 'Search...')
        ]
        self.inFocusTB = 0

        self.buttons = [
            Button(0.925, 0.0333, 0.05, 0.0666, plusImages,
                lambda: (
                    self.buttons[0].unhover(),
                    NewEntryForm(app, 0.9, 0.9)
                )),
            Button(0.85, 0.0333, 0.05, 0.0666, pencilImages,
                lambda: (
                    self.buttons[1].unhover(),
                    NewEntryForm(app, 0.9, 0.9,
                                app.forms[app.inFocusForm].entry)
                )),
            Button(0.775, 0.0333, 0.05, 0.0666, trashImages,
                lambda: (
                    self.buttons[2].unhover(),
                    ConfirmationDialogue(app, 0.5, 0.3333,
                        lambda: app.forms[app.inFocusForm].deleteEntry(app))
                )),
            Button(0.025, 0.5, 0.05, 0.0666, '<',
                   lambda: EntryView.changeFormView(app, -1)),
            Button(0.925, 0.5, 0.05, 0.0666, '>',
                   lambda: EntryView.changeFormView(app, +1))
        ]

    def draw(self, app):
        totalEntries = \
            len(app.forms) - int(type(app.forms[app.inFocusForm]) != EntryView)
        drawLabel(f'{app.inFocusForm+1}/{totalEntries}',
                  app.width*(self.x+self.w/2), app.height*(self.y+self.h*0.0666)
                  , size=0.03*app.width, fill=steelGray, font='monospace')
        for textbox in self.textboxes:
            textbox.draw(app)
        for button in self.buttons:
            button.draw(app)

class EntryView(Form):
    def __init__(self, app, w, h, entry):
        super().__init__(app, w, h)
        self.entry = entry
        self.textboxes = [
            Textbox(app, 0.1875, 0.6333, 0.5375, 0.0833, entry[2]),
            PasswordField(app, 0.1875, 0.75, 0.45, 0.0833, entry[3])
        ]
        # the index of the textbox currently in focus
        self.inFocusTB = 0

        self.buttons = [
            ActivateButton(0.6625, 0.75, 0.0625, 0.0833, hideImages,
                lambda: (
                    self.hidePassword(),
                    self.buttons[0].activate()
                )),
            Button(0.75, 0.6333, 0.0625, 0.0833, copyImages,
                   lambda: self.textboxes[0].copyToClipboard(app)),
            Button(0.75, 0.75, 0.0625, 0.0833, copyImages,
                   lambda: self.textboxes[1].copyToClipboard(app))
        ]

        app.forms.append(self)

    def hidePassword(self):
        self.textboxes[1].hide = not self.textboxes[1].hide

    @classmethod
    def changeFormView(self, app, steps):
        app.inFocusForm = (app.inFocusForm+steps) % len(app.forms)

    @classmethod
    def searchEntries(self, app, match):
        for i in range(len(app.forms)):
            if app.forms[i].entry[1].lower().startswith(match.lower()):
                app.inFocusForm = i

    def deleteEntry(self, app):
        deleteEntry(self.entry[0])
        loadEntries(app)

    def draw(self, app):
        super().draw(app)
        drawLabel(self.entry[1], app.width*(self.x+self.w/2),
                  app.height*(self.y+self.h/3), size=0.08*app.width,
                  fill=steelGray, font='monospace')
        for textbox in self.textboxes:
            textbox.draw(app)
        for button in self.buttons:
            button.draw(app)

class NewEntryForm(Form):
    def __init__(self, app, w, h, prevEntry=None):
        super().__init__(app, w, h)

        if prevEntry:
            title, username, password = prevEntry[1], prevEntry[2], prevEntry[3]
        else:
            title, username, password = '', '', ''

        self.textboxes = [
            Textbox(app, 0.125, 0.25, 0.625, 0.0833, title, 'Title'),
            Textbox(app, 0.125, 0.3833, 0.625, 0.0833, username, 'Username'),
            PasswordField(app, 0.125, 0.5166, 0.5375, 0.0833, password,
                          'Password', False),
            Textbox(app, 0.775, 0.5166, 0.0625, 0.0833, '16') # password length textbox
        ]
        # the index of the textbox currently in focus
        self.inFocusTB = 0

        self.updatePasswordGen(True, True, True, True)

        self.buttons = [
            Button(0.6875, 0.5166, 0.0625, 0.0833, generateImages,
                   lambda: self.textboxes[2].generatePassword(
                    self.textboxes[3].text, self.uppers, self.lowers, self.nums,
                    self.specials)),
            ActivateButton(0.125, 0.6583, 0.125, 0.0833, 'A-Z',
                lambda: (
                    self.updatePasswordGen(uppers=not self.uppers),
                    self.buttons[1].activate()
                )),
            ActivateButton(0.2875, 0.6583, 0.125, 0.0833, 'a-z',
                lambda: (
                    self.updatePasswordGen(lowers=not self.lowers),
                    self.buttons[2].activate()
                )),
            ActivateButton(0.45, 0.6583, 0.125, 0.0833, '0-9',
                lambda: (
                    self.updatePasswordGen(nums=not self.nums),
                    self.buttons[3].activate()
                )),
            ActivateButton(0.6125, 0.6583, 0.125, 0.0833, '/*+&...',
                lambda: (
                    self.updatePasswordGen(specials=not self.specials),
                    self.buttons[4].activate()
                )),
            Button(0.55, 0.8, 0.15, 0.0666, 'Cancel',
                   lambda: app.forms.pop(app.inFocusForm)),
            Button(0.725, 0.8, 0.15, 0.0666, 'Save',
                   lambda: self.saveEntry(app))
        ]

        app.forms.insert(app.inFocusForm, self)
        self.prevEntry = prevEntry

    def updatePasswordGen(self, uppers=None, lowers=None, nums=None,
                          specials=None):
        self.uppers = uppers if uppers != None else self.uppers
        self.lowers = lowers if lowers != None else self.lowers
        self.nums = nums if nums != None else self.nums
        self.specials = specials if specials != None else self.specials

    def draw(self, app):
        super().draw(app, 30, 'white')
        for textbox in self.textboxes:
            textbox.draw(app)
        for button in self.buttons:
            button.draw(app)

    def saveEntry(self, app):
        title = self.textboxes[0].text
        username = self.textboxes[1].text
        password = self.textboxes[2].text

        if self.prevEntry:
            prevEntryID = self.prevEntry[0]
            updateEntry(prevEntryID, title, username, password, app.masterKey)
            loadEntries(app, prevEntryID)
        else:
            entryID = addEntry(title, username, password, app.masterKey)
            loadEntries(app, entryID)

class ConfirmationDialogue(Form):
    def __init__(self, app, w, h, action):
        super().__init__(app, w, h)

        self.buttons = [
            Button(0.3625, 0.5333, 0.125, 0.0666, 'No',
                   lambda: app.forms.pop(app.inFocusForm)),
            Button(0.5125, 0.5333, 0.125, 0.0666, 'Yes',
                lambda: (
                    app.forms.pop(app.inFocusForm),
                    action()
                ))
        ]

        app.forms.insert(app.inFocusForm, self)

    def draw(self, app):
        super().draw(app, 30, 'white')
        drawLabel('Are you sure?', app.width*(self.x+self.w/2),
                  app.height*(self.y+self.h/3), fill=steelGray,
                  size=0.0325*app.width, font='monospace')
        for button in self.buttons:
            button.draw(app)

class UnlockForm(Form):
    def __init__(self, app, w, h):
        super().__init__(app, w, h)

        self.firstUse = True if getEntries('') == None else False
        buttonContent = 'Start' if self.firstUse else 'Unlock'

        self.buttons = [
            Button(self.w/2-0.125/2, 0.5916, 0.125, 0.0666, buttonContent,
                   lambda: self.unlock(app)),
            ActivateButton(self.w*0.75, self.h*0.4583, 0.0625*self.w,
                0.0833*self.h, hideImages,
                lambda: (
                    self.hidePassword(),
                    self.buttons[1].activate()
                ))
        ]

        self.textboxes = [
            PasswordField(app, 0.1875, 0.4583, 0.5375, 0.0833)
        ]
        self.inFocusTB = 0

    def unlock(self, app):
        app.masterKey = self.textboxes[0].text
        loadEntries(app)

    def hidePassword(self):
        self.textboxes[0].hide = not self.textboxes[0].hide

    def draw(self, app):
        super().draw(app)
        adjFontSize = fontSize*app.width
        if self.firstUse:
            message = 'Create a secure master password'
        else:
            message = 'Enter your master password'
        drawLabel(message, app.width*(self.x+self.w/2),
                  app.height*(self.y+self.h*0.375), fill=steelGray,
                  size=0.0325*app.width, font='monospace')
        for button in self.buttons:
            button.draw(app)
        for textbox in self.textboxes:
            textbox.draw(app)
        if hasattr(app, 'incorrectKeyCounter') and app.incorrectKeyCounter:
            drawLabel(f'Incorrect master key. Please try again.',
                      app.width*(self.x+self.w/2),
                      app.height*(self.y+self.h*0.93), fill=steelGray,
                      size=adjFontSize, font='monospace')

def loadEntries(app, focusEntryID=0):
    app.forms = []
    entries = getEntries(app.masterKey)
    if entries == False:
        reset(app)
        app.incorrectKeyCounter = 5 # 5-second decryption failure message
        return
    elif entries == None:
        EntryView(app, 1, 1, (-1, 'Welcome!',
                  'Click the + to add your first entry...', 'Enjoy :)'))
    else:
        for entry in entries:
            EntryView(app, 1, 1, entry)
        app.forms.sort(key=lambda form: form.entry[1].lower())
        app.inFocusForm = len(app.forms)//2
        for i in range(len(app.forms)):
            if app.forms[i].entry[0] == focusEntryID:
                app.inFocusForm = i
                break
    app.floatingForm = FloatingForm(app, 1, 1)

def reset(app):
    app.stepsPerSecond = 60
    app.steps = 0
    app.keyHoldSpeed = app.stepsPerSecond//8 # 8 presses a second
    app.keyHoldCounter = 0
    app.clipboardTime = 10 # 10 seconds
    app.clipboardCounter = 0
    app.idleTime = 60 # 1 minute (annoying but good for demonstration)
    app.idleCounter = app.idleTime

    app.masterKey = ''
    app.forms = [UnlockForm(app, 1, 1)]
    app.inFocusForm = 0

def onAppStart(app):
    reset(app)

def redrawAll(app):
    form = app.forms[app.inFocusForm]
    adjFontSize = fontSize*app.width
    if type(form) == EntryView:
        form.draw(app)
        app.floatingForm.draw(app)
    elif type(form) == UnlockForm:
        form.draw(app)
    else:
        app.forms[app.inFocusForm+1].draw(app)
        app.floatingForm.draw(app)
        form.draw(app)
    if 0 < app.steps % app.stepsPerSecond < app.stepsPerSecond//2:
        if type(form) in [NewEntryForm, UnlockForm]:
            form.textboxes[form.inFocusTB].blinkCursor(app)
        else:
            app.floatingForm.textboxes[0].blinkCursor(app)
    if app.clipboardCounter:
        drawLabel(f'Clearing the clipboard in {app.clipboardCounter} seconds...'
                  , app.width/2, app.height*0.93, fill=steelGray,
                  size=adjFontSize, font='monospace')

def onStep(app):
    app.steps += 1
    if app.keyHoldCounter:
        app.keyHoldCounter -= 1
    if app.steps % 60 == 0:
        if app.clipboardCounter:
            app.clipboardCounter -= 1
            if app.clipboardCounter == 0:
                pyperclip.copy('')
        app.idleCounter -= 1
        if app.idleCounter == 0:
            reset(app)
        if hasattr(app, 'incorrectKeyCounter') and app.incorrectKeyCounter:
            app.incorrectKeyCounter -= 1

def onKeyHold(app, keys):
    form = app.forms[app.inFocusForm]
    if type(form) == ConfirmationDialogue:
        return
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
    app.idleCounter = app.idleTime
    form = app.forms[app.inFocusForm]
    if type(form) == ConfirmationDialogue:
        return
    if type(form) == EntryView:
        if key == 'right':
            EntryView.changeFormView(app, 1)
        if key == 'left':
            EntryView.changeFormView(app, -1)
        form = app.floatingForm
    if type(form) == UnlockForm:
        if key == 'enter':
            form.unlock(app)
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
        if type(form) == FloatingForm:
            EntryView.searchEntries(app, form.textboxes[form.inFocusTB].text)

def onMousePress(app, mouseX, mouseY):
    app.idleCounter = app.idleTime
    form = app.forms[app.inFocusForm]
    for button in form.buttons:
        button.checkMouseClick(app, mouseX, mouseY)
    if type(form) in [NewEntryForm, UnlockForm]:
        for i in range(len(form.textboxes)):
            if form.textboxes[i].checkMouseClick(app, mouseX, mouseY):
                form.inFocusTB = i
    elif type(form) == EntryView:
        for button in app.floatingForm.buttons:
            button.checkMouseClick(app, mouseX, mouseY)
        for textbox in app.floatingForm.textboxes:
            textbox.checkMouseClick(app, mouseX, mouseY)

def onMouseMove(app, mouseX, mouseY):
    form = app.forms[app.inFocusForm]
    for button in form.buttons:
        button.hover = button.checkBounds(app, mouseX, mouseY)
    if type(form) == EntryView:
        for button in app.floatingForm.buttons:
            button.hover = button.checkBounds(app, mouseX, mouseY)

createDB()
runApp(width=800, height=600)