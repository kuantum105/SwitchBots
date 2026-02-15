# Gmail API
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import base64
# OpenCV2 API
import cv2
# Misc
import time
import sys
import os
# HORIPAD Controller input
dirPath = os.path.dirname(os.path.realpath(__file__))
sys.path.append("{}\\SwitchInputEmulator\\Arduino\\utils".format(dirPath))
import client as Controller


# HORIPAD Controller Emulation ------------------------------------------------

def OpenController(commPort):
    Controller.ser = \
        Controller.serial.Serial(commPort, baudrate=19200, timeout=1)

    if not Controller.sync():
        print('Could not sync!')
        Controller.ser.close()
        sys.exit()


def CloseController():
    if not Controller.send_cmd():
        print('Packet Error!')
        Controller.ser.close
        sys.exit()

    Controller.ser.close()


# Send command for seconds then clear.
def SendCommandForSeconds(command, seconds):
    Controller.send_cmd(command)
    ShowLive(seconds)
    Controller.send_cmd()


# Send command for a short period of time. Emulates a human pushing the button.
def SendCommandOnce(command):
    Controller.send_cmd(command)
    ShowLive(0.05)
    Controller.send_cmd()

# Video Capture ---------------------------------------------------------------


Cap = None
OpenedDeviceIndex = 0


def OpenVideoCapture(deviceIndex):
    global Cap
    global OpenedDeviceIndex

    OpenedDeviceIndex = deviceIndex
    Cap = cv2.VideoCapture(deviceIndex)
    Cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    Cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    Cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)


def CloseVideoCapture():
    Cap.release()
    cv2.destroyAllWindows()


# Gets the next frame. Doesn't buffer.
def GetFrame():
    while Cap is None:
        OpenVideoCapture(OpenedDeviceIndex)

    ret, frame = Cap.read()
    while not ret or frame is None or frame.size == 0:
        ret, frame = Cap.read()

    return frame


# Gets the next frame in grayscale. Doesn't buffer.
def GetFrameGrayscale():
    frame = GetFrame()
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


FrameDuration = 1 / 30


# Shows live video capture footage for seconds.
def ShowLive(Seconds):
    Start = time.time()
    Now = Start
    while (Now - Start) < Seconds:
        frame = GetFrame()
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            sys.exit()
        time.sleep(min(Start + Seconds - Now, FrameDuration))
        Now = time.time()


# Returns the match score for the given template in the given frame. Ranges
# from 0 to 1, which larger numbers indicating a stronger match.
def GetMatchScore(frame, template):
    res = cv2.matchTemplate(frame, template, eval('cv2.TM_CCOEFF_NORMED'))
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    return max_val, min_loc, max_loc


# Email -----------------------------------------------------------------------


SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def SendEmail(messageTo, messageFrom, subject, body):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    tokenFilePath = "{}\\token.pickle".format(dirPath)
    if os.path.exists(tokenFilePath):
        with open(tokenFilePath, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "{}\\credentials.json".format(dirPath), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(tokenFilePath, 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    message = MIMEText(body)
    message['to'] = messageTo
    message['from'] = messageFrom
    message['subject'] = subject
    encodedMessage = \
        {'raw':
         base64.urlsafe_b64encode(message.as_string().encode()).decode()}

    try:
        service.users().messages().send(userId='me',
                                        body=encodedMessage).execute()
    except error:
        print("An error occurred: {}".format(error))
