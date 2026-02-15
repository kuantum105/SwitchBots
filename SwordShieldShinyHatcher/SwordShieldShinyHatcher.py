from datetime import datetime
import cv2
import os
import sys
import time
# Shared bot functionality
dirPath = os.path.dirname(os.path.realpath(__file__))
sys.path.append("{}\\..".format(dirPath))
import BotCore as Bot
from Config import *


# Move right for seconds.
def MoveRight(seconds):
    Bot.SendCommandForSeconds(Bot.Controller.LSTICK_U_R, seconds)


# Move left for seconds.
def MoveLeft(seconds):
    Bot.SendCommandForSeconds(Bot.Controller.LSTICK_U_L, seconds)


# Open the day care lady. Assumes standing next to her.
def OpenDayCareLadyPrompt():
    Bot.SendCommandOnce(Bot.Controller.BTN_A)
    Bot.ShowLive(1.5)


# Accept an egg from the day care lady. Assumes prompt open.
def AcceptEggFromDayCareLady():
    Bot.SendCommandOnce(Bot.Controller.BTN_A)
    Bot.ShowLive(3.0)
    Bot.SendCommandOnce(Bot.Controller.BTN_A)
    Bot.ShowLive(3.0)
    Bot.SendCommandOnce(Bot.Controller.BTN_A)
    Bot.ShowLive(3.0)
    Bot.SendCommandOnce(Bot.Controller.BTN_A)
    Bot.ShowLive(0.75)


# Close the day care lady prompt.
def CloseDayCareLadyPrompt():
    Bot.SendCommandOnce(Bot.Controller.BTN_A)
    Bot.ShowLive(0.75)
    Bot.SendCommandOnce(Bot.Controller.BTN_B)
    Bot.ShowLive(0.75)
    Bot.SendCommandOnce(Bot.Controller.BTN_B)
    Bot.ShowLive(0.75)
    Bot.SendCommandOnce(Bot.Controller.BTN_B)
    Bot.ShowLive(0.75)


# Hatches an egg. Assumes "Oh?" prompt has appeared.
def HatchEgg():
    Bot.SendCommandOnce(Bot.Controller.BTN_A)
    Bot.ShowLive(20.0)
    Bot.SendCommandOnce(Bot.Controller.BTN_A)
    Bot.ShowLive(8.0)
    Bot.SendCommandOnce(Bot.Controller.LSTICK_D)
    Bot.SendCommandOnce(Bot.Controller.BTN_A)
    Bot.ShowLive(3.0)


# Homes the Pokebox to the bottom left. Assumes Pokebox is already open.
def HomePokebox():
    Bot.Controller.send_cmd(Bot.Controller.LSTICK_D)
    Bot.ShowLive(2.0)
    Bot.Controller.send_cmd()
    Bot.Controller.send_cmd(Bot.Controller.LSTICK_L)
    Bot.ShowLive(1.0)
    Bot.Controller.send_cmd()


# Opens the team menu. Assumes in open-world.
def OpenTeamMenu():
    Bot.SendCommandOnce(Bot.Controller.BTN_X)
    Bot.ShowLive(2.0)
    Bot.SendCommandForSeconds(Bot.Controller.LSTICK_L, 2.0)
    Bot.SendCommandForSeconds(Bot.Controller.LSTICK_U, 2.0)
    Bot.SendCommandOnce(Bot.Controller.LSTICK_R)
    Bot.SendCommandOnce(Bot.Controller.BTN_A)
    Bot.ShowLive(2.0)


# Closes the team menu. Assumes team menu is open.
def CloseTeamMenu():
    Bot.SendCommandOnce(Bot.Controller.BTN_B)
    Bot.ShowLive(2.0)
    Bot.SendCommandOnce(Bot.Controller.BTN_B)
    Bot.ShowLive(2.0)


# Opens the Pokebox. Assumes open-world.
def OpenPokebox():
    OpenTeamMenu()
    Bot.SendCommandOnce(Bot.Controller.BTN_R)
    Bot.ShowLive(2.0)


# Grabs the i'th Pokemon from party. Assumes Pokebox is open.
def GrabPokemonFromParty(Index):
    HomePokebox()

    upSteps = min(max(0, 5 - Index), 5)
    for i in range(upSteps):
        Bot.SendCommandOnce(Bot.Controller.LSTICK_U)
        Bot.ShowLive(0.25)
    Bot.SendCommandOnce(Bot.Controller.BTN_A)
    Bot.ShowLive(1.0)
    Bot.SendCommandOnce(Bot.Controller.BTN_A)
    Bot.ShowLive(0.75)
    for i in range(upSteps):
        Bot.SendCommandOnce(Bot.Controller.LSTICK_D)
        Bot.ShowLive(0.25)


# Deposits a Pokemon into the X, Y slot in Pokebox. Assumes Pokemon is grabbed.
def DepositPokemonIntoBoxSlot(x, y):
    Bot.SendCommandOnce(Bot.Controller.LSTICK_R)
    Bot.ShowLive(0.25)
    Bot.SendCommandOnce(Bot.Controller.LSTICK_U)
    Bot.ShowLive(0.25)

    upSteps = min(max(0, 4 - y), 4)
    for i in range(upSteps):
        Bot.SendCommandOnce(Bot.Controller.LSTICK_U)
        Bot.ShowLive(0.2)

    rightSteps = min(max(0, x), 5)
    for i in range(rightSteps):
        Bot.SendCommandOnce(Bot.Controller.LSTICK_R)
        Bot.ShowLive(0.2)

    Bot.SendCommandOnce(Bot.Controller.BTN_A)
    Bot.ShowLive(0.75)


# ----------------------------------------------------------------------------------------


def DayCareLadyCrop(frame):
    return frame[589:589+85, 288:288+568]


dayCareLadyEggPrompt = cv2.imread(
    'Resources\\DayCareLadyEggPrompt.jpg', cv2.IMREAD_GRAYSCALE)
dayCareLadyEggPrompt = DayCareLadyCrop(dayCareLadyEggPrompt)
dayCareLadyEggPromptThreshold = 0.95


def DoesDaycareLadyHaveEgg():
    frame = Bot.GetFrameGrayscale()
    frame = frame[575:575+107, 271:271+610]
    score = Bot.GetMatchScore(frame, dayCareLadyEggPrompt)
    print("Day Care Lady Score: {0}".format(score))
    return score > dayCareLadyEggPromptThreshold


def EggHatchStartCrop(frame):
    return frame[570:570+116, 240:240+650]


eggHatchingPrompt = cv2.imread(
    'Resources\\EggHatchingPrompt.jpg', cv2.IMREAD_GRAYSCALE)
eggHatchingPrompt = EggHatchStartCrop(eggHatchingPrompt)
eggHatchingPromptThreshold = 0.95


def IsEggHatching():
    Bot.ShowLive(0.5)
    frame = Bot.GetFrameGrayscale()
    frame = frame[551:551+150, 214:214+700]
    score = Bot.GetMatchScore(frame, eggHatchingPrompt)
    return score > eggHatchingPromptThreshold


occupiedPokeboxSlotMinStdDev = 25


def GetEmptyPokeboxSlotXY():
    pokeboxGridTop = 138
    pokeboxGridBottom = 138 + 435
    pokeboxGridLeft = 331
    pokeboxGridRight = 331 + 522
    slotHeight = (pokeboxGridBottom - pokeboxGridTop) / 5
    slotWidth = (pokeboxGridRight - pokeboxGridLeft) / 6

    frame = Bot.GetFrameGrayscale()
    for x in range(6):
        for y in range(5):
            slotTop = pokeboxGridTop + slotHeight * y
            slotBottom = slotTop + slotHeight
            slotLeft = pokeboxGridLeft + slotWidth * x
            slotRight = slotLeft + slotWidth

            slotTop = round(slotTop) + 5
            slotBottom = round(slotBottom) - 5
            slotLeft = round(slotLeft) + 5
            slotRight = round(slotRight) - 5

            slot = frame[slotTop:slotBottom, slotLeft:slotRight]
            mean, stdDev = cv2.meanStdDev(slot)
            if (stdDev < occupiedPokeboxSlotMinStdDev):
                return x, y

    return -1, -1


def TeamCrop(Frame, TeamIndex):
    TeamLeft = 75
    TeamTop = 118
    TeamWidth = 387
    TeamHeight = 555
    TeamMemberHeight = TeamHeight / 6

    y0 = TeamTop + round(TeamMemberHeight * TeamIndex)
    y1 = y0 + round(TeamMemberHeight)
    x0 = TeamLeft
    x1 = TeamLeft + TeamWidth
    return Frame[y0:y1, x0:x1]


EggInTeam = cv2.imread('Resources\\TeamPageWithEgg.jpg', cv2.IMREAD_GRAYSCALE)
EggInTeam = EggInTeam[450:450+18, 114:114+18]
EggInTeamThreshold = 0.9


def IsEggInTeamSlot(TeamIndex):
    Frame = Bot.GetFrameGrayscale()
    TeamMember = TeamCrop(Frame, TeamIndex)
    Score = Bot.GetMatchScore(TeamMember, EggInTeam)
    print(Score)
    return Score >= EggInTeamThreshold


def IsTeamSlotEmpty(TeamIndex):
    Frame = Bot.GetFrame()
    TeamMember = TeamCrop(Frame, TeamIndex)
    MeanColor = TeamMember.mean(axis=0).mean(axis=0)
    return MeanColor[2] > 200 and MeanColor[1] < 70 and MeanColor[0] < 70


PokeboxPageShinyMarker = cv2.imread('Resources\\PokeboxPageShinyMarker.jpg',
                                    cv2.IMREAD_GRAYSCALE)
PokeboxPageShinyMarker = PokeboxPageShinyMarker[116:116+26, 1218:1218+26]
PokeboxPageShinyMarkerThreshold = 0.9


def IsPokeboxPageShiny():
    Frame = Bot.GetFrameGrayscale()
    Frame = Frame[110:110+37, 1210:1210+42]
    Score = Bot.GetMatchScore(Frame, PokeboxPageShinyMarker)
    return Score > PokeboxPageShinyMarkerThreshold


# ----------------------------------------------------------------------------------------


def DepositAllHatchlingsIntoPokebox():
    OpenPokebox()

    for partyIndex in range(5, 0, -1):
        GrabPokemonFromParty(partyIndex)

        if (IsPokeboxPageShiny()):
            Bot.SendEmail(EmailTo, EmailFrom, 'Shiny pokemon hatched!',
                          "Time: {}".format(datetime.now()))

        numPagesChecked = 0
        slotX = -1
        slotY = -1
        while slotX < 0 and slotY < 0:
            slotX, slotY = GetEmptyPokeboxSlotXY()
            if (slotX < 0 and slotY < 0):
                if (numPagesChecked >= 32):
                    print("Pokebox full")
                    Bot.SendEmail(EmailTo, EmailFrom, 'Pokebox full',
                                  "Time: {}".format(datetime.now()))
                    sys.exit(0)
                HomePokebox()
                numPagesChecked += 1
                Bot.SendCommandOnce(Bot.Controller.LSTICK_R)
                Bot.SendCommandOnce(Bot.Controller.BTN_R)
                Bot.ShowLive(0.75)
                Bot.SendCommandOnce(Bot.Controller.LSTICK_L)

        print("Depositing into {0}, {1}".format(slotX, slotY))
        DepositPokemonIntoBoxSlot(slotX, slotY)

    Bot.SendCommandOnce(Bot.Controller.BTN_B)
    Bot.ShowLive(2.0)
    Bot.SendCommandOnce(Bot.Controller.BTN_B)
    Bot.ShowLive(2.0)
    Bot.SendCommandOnce(Bot.Controller.BTN_B)
    Bot.ShowLive(1.0)


def GetTeamState():
    OpenTeamMenu()
    NumEggs = 0
    NumHatchlings = 0
    for i in range(1, 6):
        if IsEggInTeamSlot(i):
            NumEggs += 1
        elif not IsTeamSlotEmpty(i):
            NumHatchlings += 1
    CloseTeamMenu()
    return NumEggs, NumHatchlings


# ----------------------------------------------------------------------------------------


Bot.OpenVideoCapture(VideoCaptureNum)
Bot.OpenController(ComPort)

Bot.SendEmail(EmailTo, EmailFrom, 'Sword/Shield hatcher bot starting up', "Time: {}".format(datetime.now()))

# The first few commands often get ignored. Flushing that behavior
Bot.ShowLive(1.0)
Bot.SendCommandOnce(Bot.Controller.BTN_B)
Bot.SendCommandOnce(Bot.Controller.BTN_B)
Bot.SendCommandOnce(Bot.Controller.BTN_B)

#Bot.SendEmail(EmailTo, EmailFrom, 'Sword/Shield Shiny Hatcher Started Up', '')

numEggs, numHatchlings = GetTeamState()
timeLastEggTransaction = time.time()
lapsUntilCheck = 0

MoveRight(2.6)
while True:
    print("Eggs: {0}, Hatchlings: {1}".format(numEggs, numHatchlings))
    if (IsEggHatching()):
        HatchEgg()
        numEggs -= 1
        numHatchlings += 1
        MoveRight(2.6)
        timeLastEggTransaction = time.time()
    elif (numHatchlings == 5):
        DepositAllHatchlingsIntoPokebox()
        numEggs = 0
        numHatchlings = 0
        timeLastEggTransaction = time.time()
        lapsUntilCheck = 0
    elif (numEggs + numHatchlings < 5) and lapsUntilCheck <= 0:
        OpenDayCareLadyPrompt()
        if (DoesDaycareLadyHaveEgg()):
            AcceptEggFromDayCareLady()
            numEggs += 1
            timeLastEggTransaction = time.time()
        else:
            CloseDayCareLadyPrompt()
        MoveLeft(2.5)
        MoveRight(2.6)
        lapsUntilCheck = 2
    else:
        MoveLeft(2.5)
        MoveRight(2.5)
        lapsUntilCheck -= 1

    if (time.time() - timeLastEggTransaction > 10 * 60):
        print('Nothing happened for a long time. Quitting out')
        Bot.SendEmail(EmailTo, EmailFrom, 'Sword/Shield hatcher bot got stuck',
                      "Time: {}".format(datetime.now()))
        break

Bot.CloseController()
Bot.CloseVideoCapture()
