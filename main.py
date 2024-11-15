from cmu_graphics import *
import time

class Window:
    def __init__(self, w, h):
        self.w = w
        self.h = h
    def draw(self, app):
        drawRect(app.width/2-self.w/2, app.height/2-self.h/2, self.w, self.h,
        fill=app.ironGray, border='black', borderWidth=5)

class Textbox:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = '| '
    def draw(self, app):
        drawRect(self.x, self.y, self.w, self.h, fill=None,
                    border=app.steelGray, borderWidth=5)
        drawLabel(self.text[::-1][:25][::-1], self.x+100, self.y+self.h/2, align='left',
                    fill=app.steelGray, size=30)

def onAppStart(app):
    app.ironGray = rgb(109, 110, 113)
    app.steelGray = rgb(224, 224, 224)

    app.steps = 0

    app.window = Window(200, 200)

    mainTextBoxW = 500
    mainTextBoxH = 80
    mainTextBox = Textbox(app.width/2-mainTextBoxW/2, \
        app.height/2-mainTextBoxH/2, mainTextBoxW, mainTextBoxH)
    app.textboxes = [mainTextBox]

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill=app.ironGray)
    for textbox in app.textboxes:
        textbox.draw(app)
    app.window.draw(app)

def onStep(app):
    app.steps += 1
    if app.steps % 30 == 0:
        if app.textboxes[0].text.endswith('| '):
            app.textboxes[0].text = app.textboxes[0].text[:-2] + '  '
        else:
            app.textboxes[0].text = app.textboxes[0].text[:-2] + '| '

def onKeyHold(app, keys):
    if 'backspace' in keys:
        app.textboxes[0].text = app.textboxes[0].text[:-3] + \
                                                    app.textboxes[0].text[-2:]
        time.sleep(0.1)

def onKeyPress(app, key):
    if key == 'space':
        app.textboxes[0].text = app.textboxes[0].text[:-2] + ' ' + \
                                                    app.textboxes[0].text[-2:]
    elif key != 'backspace':
        app.textboxes[0].text = app.textboxes[0].text[:-2] + key + \
                                                    app.textboxes[0].text[-2:]

runApp(width=800, height=600)