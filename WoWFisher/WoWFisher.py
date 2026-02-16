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
import pytesseract
import re
from scipy import ndimage
import math
import cProfile
# Shared bot functionality
dirPath = os.path.dirname(os.path.realpath(__file__))
sys.path.append("{}\\..".format(dirPath))
from Config import *


# globals
screenshotPath = "{}\\Output\\Screenshot.png".format(dirPath)
#x, y = pyautogui.size()
#x2, y2 = pyautogui.size()
#x2, y2 = int(str(x2)), int(str(y2))
x3 = 1280
y3 = 720


programStateIndeterminate = -1
programStateIdle = 0
programStateLookingForSchool = 1
programStateMovingToSchool = 2
programStateFishing = 3
ProgramState = programStateIdle


def GetPyautoguiScreenshot(coords = (0, 0, x3, y3)):
    p = pyautogui.screenshot()
    return p.crop(coords)


def UpdateScreenshot():
    p = GetPyautoguiScreenshot()
    p.save(screenshotPath, quality=100)


def GetScreenshotGrayscale(coords = (0, 0, x3, y3)):
    p = GetPyautoguiScreenshot(coords)
    p = cv2.cvtColor(np.array(p), cv2.COLOR_BGR2GRAY)
    return p


def GetScreenshotColor(coords = (0, 0, x3, y3)):
    p = GetPyautoguiScreenshot(coords)
    p = cv2.cvtColor(np.array(p), cv2.COLOR_RGB2BGR)
    return p


pressedFromKeyCode = {}


def IsKeyCodePressed(keyCode):
    if keyCode in pressedFromKeyCode:
        return pressedFromKeyCode[keyCode]
    else:
        return False


def SetKeyCodePressed(keyCode, pressed):
    pressedFromKeyCode[keyCode] = pressed


def IsPressed(keys):
    parseResult = keyboard.parse_hotkey(keys)
    if not parseResult:
        return False

    allKeysPressed = True
    for keyCodes in parseResult[0]:
        anyCodePressed = False
        for keyCode in keyCodes:
            if IsKeyCodePressed(keyCode):
                anyCodePressed = True
                break

        if not anyCodePressed:
            allKeysPressed = False
            break

    return allKeysPressed

def Press(keys):
    parseResult = keyboard.parse_hotkey(keys)
    if parseResult:
        for keyCodes in parseResult[0]:
            anyCodePressed = False
            for keyCode in keyCodes:
                if (IsKeyCodePressed(keyCode)):
                    anyCodePressed = True

            if len(keyCodes) > 0 and not anyCodePressed:
                keyboard.press(keyCodes[0])
                SetKeyCodePressed(keyCodes[0], True)


def Release(keys):
    parseResult = keyboard.parse_hotkey(keys)
    if parseResult:
        for keyCodes in parseResult[0]:
            for keyCode in keyCodes:
                if (IsKeyCodePressed(keyCode)):
                    keyboard.release(keyCode)
                    SetKeyCodePressed(keyCode, False)


def PressKeysForRandomTime(keys):
    Press(keys)
    time.sleep(random.uniform(0.1, 0.11))
    Release(keys)


def PressKeysAfterRandomTime(keys):
    #time.sleep(random.uniform(0.05, 0.15))
    Press(keys)


def ReleaseKeysAfterRandomTime(keys):
    #time.sleep(random.uniform(0.01, 0.05))
    Release(keys)


def GetCharacterTransform():
    frame = GetScreenshotGrayscale()
    coordImage = frame[694: 694 + 26, 1141: 1141 + 139]
    coordText = pytesseract.image_to_string(coordImage)
    coordText = re.sub('\\s+', "", coordText)

    search = re.search('([0-9\\.]*),([0-9\\.]*),([0-9\\.]*)', coordText)
    if (search):
        xCoord = float(search.group(1))
        yCoord = float(search.group(2))
        degrees = float(search.group(3))
    else:
        xCoord = -1
        yCoord = -1
        degrees = -1

    if (degrees > -1):
        degrees = (630 - degrees) % 360

    return (xCoord, yCoord), degrees


def RotateVector(vector, angleDeg):
    angleRad = math.radians(angleDeg)
    x2 = vector[0] * math.cos(angleRad) - vector[1] * math.sin(angleRad)
    y2 = vector[0] * math.sin(angleRad) + vector[1] * math.cos(angleRad)
    return x2, y2


# ----------------------------------------------------------------------------------------



positionTolerance = 0.05
targetPosition = (52.25, 73.47)
def TickMovement(currentPosition, currentAngle):
    positionError = np.subtract(currentPosition, targetPosition)
    if (abs(positionError[0]) < positionTolerance):
        positionError[0] = 0
    if (abs(positionError[1]) < positionTolerance):
        positionError[1] = 0

    localPositionError = RotateVector(positionError, -currentAngle)
    if (localPositionError[0] < -positionTolerance):
        if (not IsPressed('w')):
            PressKeysAfterRandomTime('w')
            print ('Pressed w')
    elif (IsPressed('w')):
        ReleaseKeysAfterRandomTime('w')
        print ('Released w')
    if (localPositionError[0] > positionTolerance):
        if (not IsPressed('s')):
            PressKeysAfterRandomTime('s')
            print ('Pressed s')
    elif (IsPressed('s')):
        ReleaseKeysAfterRandomTime('s')
        print ('Released s')

    if (localPositionError[1] < -positionTolerance):
        if (not IsPressed('d')):
            PressKeysAfterRandomTime('d')
            print ('Pressed d')
    elif (IsPressed('d')):
        ReleaseKeysAfterRandomTime('d')
        print ('Released d')
    if (localPositionError[1] > positionTolerance):
        if (not IsPressed('a')):
            PressKeysAfterRandomTime('a')
            print ('Pressed a')
    elif (IsPressed('a')):
        ReleaseKeysAfterRandomTime('a')
        print ('Released a')


angleTolerance = 60
def TickOrientation(currentPosition, currentAngle):
    directionToTarget = np.subtract(targetPosition, currentPosition)
    directionToTarget = directionToTarget / np.linalg.norm(directionToTarget)
    facingDirection = RotateVector([1, 0], currentAngle)

    cross = np.cross(facingDirection, directionToTarget)
    dot = np.dot(facingDirection, directionToTarget)
    angleToTarget = math.degrees(math.asin(np.linalg.norm(cross)))

    pressLeft = False
    pressRight = False

    if (dot < 0 or angleToTarget > angleTolerance):
        if (cross > 0):
            pressRight = True
        else:
            pressLeft = True

    if (pressLeft):
        if (not IsPressed('[')):
            PressKeysAfterRandomTime('[')
            print ('Pressed [')
    elif (IsPressed('[')):
        ReleaseKeysAfterRandomTime('[')
        print ('Released [')

    if (pressRight):
        if (not IsPressed(']')):
            PressKeysAfterRandomTime(']')
            print ('Pressed ]')
    elif (IsPressed(']')):
        ReleaseKeysAfterRandomTime(']')
        print ('Released ]')



# ----------------------------------------------------------------------------------------


lookingStateIndeterminate = -1
lookingStateIdle = 0
lookingStateSearching = 1


class DynamicLookingData:
    frame = None


LookingData = None


def TransitionToLookingState():
    global ProgramState
    global LookingData
    ProgramState = programStateLookingForSchool
    LookingData = DynamicLookingData()


def MapCrop(frame):
    return frame[47: 47 + 74, 1152: 1152 + 91]


# Returns the match score for the given template in the given frame. Ranges
# from 0 to 1, which larger numbers indicating a stronger match.
def GetMatchScore(frame, template):
    res = cv2.matchTemplate(frame, template, eval('cv2.TM_CCOEFF_NORMED'))
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    return max_val, min_loc, max_loc


SchoolNode = cv2.imread('Resources\\SchoolNode.png', cv2.IMREAD_COLOR)
SchoolScoreThreshold = 0.8
OriginLocation = (36, 47)


def GetSchoolLocation(data):
    mapFrame = MapCrop(data.frame)
    score, minLoc, maxLoc = GetMatchScore(mapFrame, SchoolNode)
    if (score > SchoolScoreThreshold):
        return np.subtract(maxLoc, OriginLocation)
    else:
        return None



def TickLookingForSchool(data):
    data.frame = GetScreenshotColor()
    schoolLocation = GetSchoolLocation(data)
    if (schoolLocation is not None):
        print (schoolLocation)



# ----------------------------------------------------------------------------------------


fishingStateIndeterminate = -1
fishingStateIdle = 0
fishingStateCalibrating = 1
fishingstateWaitingForBite = 2


class DynamicFishingData:
    fishingState = fishingStateIdle
    timeOfLastCast = time.time()
    timeOfLastHookAction = time.time()
    calibrationScores = []
    scoreAverage = 0
    scoreStdDev = 0


FishingData = None


def TransitionToFishingState():
    global ProgramState
    global FishingData
    ProgramState = programStateFishing
    FishingData = DynamicFishingData()


def ShouldCalibrate(data):
    if (data.fishingState == fishingStateCalibrating):
        return True
    else:
        return False

def ShouldCastReel(data):
    if (data.fishingState == fishingStateIdle):
        return True
    else:
        return False


okayPrompt = cv2.imread(
    'Resources\\OkayPrompt.png', cv2.IMREAD_COLOR)
okayPromptThreshold = 0.9


def TryLootBoP():
    frame = GetScreenshotColor()
    score, minLoc, maxLoc = GetMatchScore(frame, okayPrompt)
    if (score > okayPromptThreshold):
        h, w, d = okayPrompt.shape
        matchLocMin = (maxLoc[0], maxLoc[1])
        matchLocMax = (matchLocMin[0] + w, matchLocMin[1] + h)
        moveToX = 0.5 * (matchLocMin[0] + matchLocMax[0])
        moveToY = 0.5 * (matchLocMin[1] + matchLocMax[1])
        pyautogui.moveTo(moveToX, moveToY, 0.15)
        time.sleep(1)
        pyautogui.leftClick()
        time.sleep(1)

hookPrompt = cv2.imread(
    'Resources\\HookScreenshot_ThunderBluff.png', cv2.IMREAD_COLOR)
hookPromptThreshold = 0.08
hookAlpha = 4


frameMin = x3/4, 0
frameMax = 3 * x3 / 4, y3/2


def GetHookFrameData():
    frame = GetScreenshotColor((frameMin[0], frameMin[1], frameMax[0], frameMax[1]))
    score, minLoc, maxLoc = GetMatchScore(frame, hookPrompt)
    return frame, score, maxLoc


def TryHook(data):
    if (data.fishingState == fishingstateWaitingForBite):
        frame, score, maxLoc = GetHookFrameData()
        scoreDelta = abs(score - data.scoreAverage)
        if (scoreDelta > hookAlpha * data.scoreStdDev):
            print(scoreDelta, data.scoreAverage, data.scoreStdDev)
            print('Hooking!')
            h, w, d = hookPrompt.shape
            matchLocMin = (frameMin[0] + maxLoc[0], frameMin[1] + maxLoc[1])
            matchLocMax = (matchLocMin[0] + w, matchLocMin[1] + h)
            moveToX = 0.5 * (matchLocMin[0] + matchLocMax[0])
            moveToY = 0.5 * (matchLocMin[1] + matchLocMax[1])
            pyautogui.moveTo(moveToX, moveToY, 0.15)
            time.sleep(0.4)

            PressKeysAfterRandomTime('shift')
            pyautogui.rightClick()
            ReleaseKeysAfterRandomTime('shift')
            time.sleep(2)

            TryLootBoP()

            pyautogui.moveTo(moveToX + 2.0 * frame.shape[0], moveToY, 0.3)
            return True
    return False


MaxFishingTime = 25
TimeoutLogout = 360
CalibrationTime = 2


def TickFishing(data):
    if (ShouldCastReel(data)):
        print('Casting reel')
        PressKeysForRandomTime('F1')
        time.sleep(3)
        data.fishingState = fishingStateCalibrating
        data.timeOfLastCast = time.time()

    data.timeSinceLastCast = time.time() - data.timeOfLastCast
    if (ShouldCalibrate(data)):
        if (data.timeSinceLastCast < CalibrationTime):
            frame, score, maxLoc = GetHookFrameData()
            data.calibrationScores.append(score)
        else:
            data.scoreAverage = np.mean(data.calibrationScores)
            data.scoreStdDev = np.std(data.calibrationScores)
            data.fishingState = fishingstateWaitingForBite

    if (TryHook(data)):
        data.calibrationScores = []
        data.fishingState = fishingStateIdle
        data.timeOfLastHookAction = time.time()

    if (data.timeSinceLastCast > MaxFishingTime):
        print('Fish missed')
        data.fishingState = fishingStateIdle

    data.timeSinceLastHook = time.time() - data.timeOfLastHookAction
    if (data.timeSinceLastHook > TimeoutLogout):
        print('Nothing happened for a long time. Quitting out')
        PressKeysForRandomTime('alt+F4')
        exit()


# ----------------------------------------------------------------------------------------


z1 = pygetwindow.getAllTitles()
my = pygetwindow.getWindowsWithTitle("World of Warcraft")[0]
my.resizeTo(x3, y3)
# top-left
my.moveTo(0, 0)
my.activate()
time.sleep(3)

screenshotNum = 0


TransitionToFishingState()


while(True):
    # time.sleep(0.033)
    # screenshotNum += 1
    # screenshotPath = "{}\\Output\\Screenshot{}.png".format(dirPath, screenshotNum)
    # p = GetPyautoguiScreenshot()
    # p.save(screenshotPath, quality=100)

    # currentPosition, currentAngle = GetCharacterTransform()
    # TickMovement(currentPosition, currentAngle)
    # TickOrientation(currentPosition, currentAngle)

    if (ProgramState == programStateFishing):
        TickFishing(FishingData)
        continue
    elif (ProgramState == programStateLookingForSchool):
        TickLookingForSchool(LookingData)
        continue
