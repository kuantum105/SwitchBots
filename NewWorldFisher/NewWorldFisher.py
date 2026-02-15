import datetime
import cv2
import os
import sys
import time
import pygetwindow
import time
import os
import pyautogui
import PIL
import keyboard
import random
import numpy as np
# Shared bot functionality
dirPath = os.path.dirname(os.path.realpath(__file__))
sys.path.append("{}\\..".format(dirPath))
import BotCore as Bot
from Config import *


# globals
screenshotPath = "{}\\Output\\Screenshot.png".format(dirPath)
x, y = pyautogui.size()
x2, y2 = pyautogui.size()
x2, y2 = int(str(x2)), int(str(y2))
x3 = x2 // 2
y3 = y2 // 2

stateIndeterminate = -1
stateWaitingForBite = 0
stateReelingIn = 1
stateReelingOut = 2
currentState = stateIndeterminate

timeoutFishCaptured = 8
timeoutState = 60
timeoutLogout = 120
timeOfLastReelingAction = time.time()


def GetPyautoguiScreenshot():
    p = pyautogui.screenshot()
    return p.crop((0, 0, x3, y3))


def UpdateScreenshot():
    p = GetPyautoguiScreenshot()
    p.save(screenshotPath, quality=100)


def GetScreenshotGrayscale():
    p = GetPyautoguiScreenshot()
    p = cv2.cvtColor(np.array(p), cv2.COLOR_BGR2GRAY)
    return p


def GetScreenshotColor():
    p = GetPyautoguiScreenshot()
    p = cv2.cvtColor(np.array(p), cv2.COLOR_RGB2BGR)
    return p


def PressKeysForRandomTime(keys):
    keyboard.press(keys)
    time.sleep(random.uniform(0.1, 0.11))
    keyboard.release(keys)


def PressKeysAfterRandomTime(keys):
    #time.sleep(random.uniform(0.05, 0.15))
    keyboard.press(keys)


def ReleaseKeysAfterRandomTime(keys):
    #time.sleep(random.uniform(0.01, 0.05))
    #time.sleep(0.05)
    keyboard.release(keys)


# ----------------------------------------------------------------------------------------


def HoldCastCrop(frame):
    return frame[507: 507 + 14, 697: 697 + 18]


holdCastPrompt = cv2.imread(
    'Resources\\HoldCastScreenshot.png', cv2.IMREAD_GRAYSCALE)
holdCastPrompt = HoldCastCrop(holdCastPrompt)
cv2.imwrite('Resources\\HoldCastScreenshot_Cropped.png', holdCastPrompt)
holdCastPromptThreshold = 0.99
castKey = 'F5'


def ShouldCastReel():
    if (currentState == stateIndeterminate or currentState == stateWaitingForBite):
        frame = GetScreenshotGrayscale()
        Score = Bot.GetMatchScore(frame, holdCastPrompt)
        return Score > holdCastPromptThreshold
    else:
        return False


def CastReel():
    #PressKeysForRandomTime(castKey)
    PressKeysAfterRandomTime(castKey)
    time.sleep(2.0)
    #time.sleep(1.0)
    ReleaseKeysAfterRandomTime(castKey)


def HookCrop(frame):
    return frame[174: 174 + 21, 608: 608 + 29]


hookPrompt = cv2.imread(
    'Resources\\HookScreenshot.png', cv2.IMREAD_GRAYSCALE)
hookPrompt = HookCrop(hookPrompt)
cv2.imwrite('Resources\\HookScreenshot_Cropped.png', hookPrompt)
hookPromptThreshold = 0.9
hookKey = 'F5'


def ShouldHook():
    if (currentState == stateIndeterminate or currentState == stateWaitingForBite):
        frame = GetScreenshotGrayscale()
        Score = Bot.GetMatchScore(frame, hookPrompt)
        return Score > hookPromptThreshold
    else:
        return False


def Hook():
    PressKeysForRandomTime(hookKey)


def StartReelCrop(frame):
    return frame[196: 196 + 25, 581: 581 + 20]


startReelPrompt = cv2.imread(
    'Resources\\StartReelingScreenshot.png', cv2.IMREAD_COLOR)
startReelPrompt = StartReelCrop(startReelPrompt)
cv2.imwrite('Resources\\StartReelingScreenshot_Cropped.png', startReelPrompt)
startReelThreshold = 0.7
startReelKey = 'F5'


def ShouldStartReel():
    if (currentState == stateIndeterminate or currentState == stateReelingOut):
        frame = GetScreenshotColor()
        Score = Bot.GetMatchScore(frame, startReelPrompt)
        return Score > startReelThreshold
    else:
        return False


def StartReel():
    PressKeysAfterRandomTime(startReelKey)


def StopReel1Crop(frame):
    return frame[230: 230 + 25, 580: 580 + 18]


stopReel1Prompt = cv2.imread(
    'Resources\\StopReelingScreenshot.png', cv2.IMREAD_COLOR)
stopReel1Prompt = StopReel1Crop(stopReel1Prompt)
cv2.imwrite('Resources\\StopReelingScreenshot_Cropped.png', stopReel1Prompt)
stopReel1Threshold = 0.75


def StopReel2Crop(frame):
    return frame[222: 222 + 25, 582: 582 + 18]


stopReel2Prompt = cv2.imread(
    'Resources\\StopReelingScreenshot2.png', cv2.IMREAD_COLOR)
stopReel2Prompt = StopReel2Crop(stopReel2Prompt)
cv2.imwrite('Resources\\StopReelingScreenshot2_Cropped.png', stopReel2Prompt)
stopReel2Threshold = 0.75

def ShouldStopReel():
    if (currentState == stateIndeterminate or currentState == stateReelingIn):
        frame = GetScreenshotColor()
        Score1 = Bot.GetMatchScore(frame, stopReel1Prompt)
        Score2 = Bot.GetMatchScore(frame, stopReel2Prompt)
        return Score1 > stopReel1Threshold or Score2 > stopReel2Threshold
    else:
        return False


def StopReel():
    ReleaseKeysAfterRandomTime(startReelKey)


# ----------------------------------------------------------------------------------------


# z1 = pygetwindow.getAllTitles()
# my = pygetwindow.getWindowsWithTitle("New World")[0]
# my.resizeTo(x3, y3)
# # top-left
# my.moveTo(0, 0)
# my.activate()

# walkDuration = 2
# walkingRight = True
# numFishUntilLagReset = 0

# while(True):
#     if (ShouldCastReel()):
#         print('Casting reel')
#         ReleaseKeysAfterRandomTime('alt')
#         time.sleep(1)
        
#         if (numFishUntilLagReset == 0):
#             numFishUntilLagReset = random.randrange(9, 12)

#             if walkingRight:
#                 walkKey = 'd'
#             else:
#                 walkKey = 'a'

#             PressKeysAfterRandomTime(walkKey)
#             time.sleep(walkDuration)
#             ReleaseKeysAfterRandomTime(walkKey)
#             time.sleep(1)
#             walkingRight = not walkingRight

#         CastReel()
#         PressKeysAfterRandomTime('alt')
#         time.sleep(1)
#         currentState = stateWaitingForBite

#     if (ShouldHook()):
#         print('Hooking')
#         Hook()
#         currentState = stateReelingOut
#         timeOfLastReelingAction = time.time()

#     if (ShouldStartReel()):
#         print('Starting reel')
#         timeOfLastStartReel = time.time()
#         StartReel()
#         currentState = stateReelingIn
#         timeOfLastReelingAction = time.time()

#     if (ShouldStopReel()):
#         print('Stopping reel')
#         StopReel()
#         currentState = stateReelingOut
#         timeOfLastReelingAction = time.time()

#     timeSinceLastReelingAction = time.time() - timeOfLastReelingAction
#     if ((currentState == stateReelingIn or currentState == stateReelingOut) and timeSinceLastReelingAction > timeoutFishCaptured):
#         currentState = stateWaitingForBite
#         numFishUntilLagReset -= 1
#     elif (currentState != stateIndeterminate and timeSinceLastReelingAction > timeoutState):
#         currentState = stateIndeterminate
#         PressKeysForRandomTime('F6')
#     elif (timeSinceLastReelingAction > timeoutLogout):
#         print('Nothing happened for a long time. Quitting out')
#         Bot.SendEmail(EmailTo, EmailFrom, 'New World fisher bot got stuck', "Time: {}".format(datetime.datetime.now()))
#         PressKeysForRandomTime('alt+F4')
#         break
