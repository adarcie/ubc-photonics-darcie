# -*- coding: utf-8 -*-
"""
Created on Sun Nov  7 11:56:23 2021

@author: Adam
"""

import pyaudio
import speech_recognition as sr
import pyautogui as pya
import time
import keyboard
from playsound import playsound
from gtts import gTTS
import os
import random

sr_hotkey='f2'

NAME='Adam'


temp_folder='C:\\Users\\Bigbo\\Downloads\\AI_Temp'
notefolder='C:\\Users\\Bigbo\\Downloads\\AI_Temp\\Notes'
temp_tts=temp_folder+'\\tts.mp3'

####### RUN TO DETERMINE MIC #############
# p = pyaudio.PyAudio()
# info = p.get_host_api_info_by_index(0)
# numdevices = info.get('deviceCount')

# for i in range(0, numdevices):
#         if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
#             print ("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
      
#convert a list of strings into a single string
def list2str(listofstr):
    returnstr=''
    for i in range(len(listofstr)):
        if i!=0:
            returnstr+=" "
        returnstr+=listofstr[i]
    return returnstr

#text to speech for given input string
def tts(mytext):
    if mytext!='':
        language='en'
        myobj = gTTS(text=mytext, lang=language, slow=False)
        myobj.save(temp_tts)
        playsound(temp_tts)
        os.remove(temp_tts)
    
#play random phrase from list through tts
def rand_tts(phrases):
    tts(random.choice(phrases))

#complete phrases
def completion():
    phrases=["done","finished","all done"]
    rand_tts(phrases)
    
#affirmation phrases
def affirmation():
    phrases=["you got it","you bet","on it"]
    rand_tts(phrases)

#play listening sound
def listeningsound():
    playsound('listening.mp3')


#play failure sound
def failsound():
    playsound('error_sound.mp3')

#define what to do with speech recognition command
def control_fn(cmd):
    global  NAME
    # SIMPLE HOTKEYS
    if cmd=="pause" or cmd=="play" or cmd=="resume":
        pya.press('playpause')
    elif cmd=="next" or cmd=="next song":
        pya.press('nexttrack')
    elif cmd=="previous" or cmd=="previous song":
        pya.press('prevtrack')
        pya.press('prevtrack')
    elif cmd=="louder" or cmd=="volume up":
        for i in range(10):
            pya.press('volumeup')
    elif cmd=="softer" or cmd=="volume down":
        for i in range(10):
            pya.press('volumedown')
    elif cmd=="mute" or cmd=="silence":
        pya.press('volumemute')
    elif cmd=="speakers":
        pya.hotkey('alt','delete')
    elif cmd=="headphones":
        pya.hotkey('alt','insert')
    elif cmd=="brighter":
        pya.hotkey('alt','pgup')
    elif cmd=="dimmer":
        pya.hotkey('alt','pgdn')
    elif cmd=="run code" or cmd=="run program":
        pya.press('f5')
        tts("executing")
        
        
    # type text
    elif cmd.split(" ")[0] == "enter":
        cmdlist=cmd.split(" ")
        if len(cmdlist)>1:
            textblock=cmdlist[1:len(cmdlist)]
            pya.write(list2str(textblock))
            completion()
        else:
            failsound()
            
    # write note in text file
    elif cmd.split(" ")[0] == "make" and cmd.split(" ")[1] == "a" and cmd.split(" ")[2] == "note":
        cmdlist=cmd.split(" ")
        if len(cmdlist)>3:
            textblock=cmdlist[3:len(cmdlist)]
            text2write=list2str(textblock)

            f = open(notefolder+"\\notes.txt", "a")
            f.write(text2write+'\n')
            f.close()
            completion()
        else:
            failsound()
                
                
        
    # SEARCH PROGRAM IN TASKBAR
    elif cmd.split(" ")[0] == "open":
        cmdlist=cmd.split(" ")
        if len(cmdlist)>1:
            programsearch=list2str(cmdlist[1:len(cmdlist)])
            affirmation()
            pya.press('win')
            time.sleep(0.5)
            pya.write(programsearch)
            time.sleep(0.5)
            pya.press('enter')
        else:
            failsound()
            
        
        
    # NAME RECOGNITION
    elif "call me" in cmd:
        NAME=cmd.split("all me")[1]
        tts("OK, "+NAME)
    elif cmd=="what is my name" or cmd=="what's my name":
        tts("You asked me to call you "+NAME)
    
        
    # CALCULATOR    
    elif "what's" in cmd: #imply simple mathematical statement
        # currently doesn't work if the numbers are too big, \
        # eg 1 million + 1 million gives an error because million is text
        eqn=cmd.split("hat's ")[1]
        soln=eval(eqn)
        response=eqn + " = " +str(soln)
        print(response)
        tts(response)
        
    # TTS REPEAT
    elif "repeat after me" in cmd:
        phrase=cmd.split("epeat after me")[1]
        tts(phrase)
        
    else:
        failsound()
    
#define function for starting speech recognition
def start_sr():
    
    r = sr.Recognizer()
    r.pause_threshold = 0.5
    speech = sr.Microphone(device_index=1)
    with speech as source:
        print("say something!…")
        listeningsound()
        # audio = r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        recog = r.recognize_google(audio, language = 'en-US')
        control_fn(recog)
    
        print("You said: " + recog)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        failsound()
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        failsound()


def welcome_msg():
    global NAME
    msg="Welcome, "+NAME#+". Press "+sr_hotkey+" to give commands."
    tts(msg)

########## Start of Program ##############

#look for hotkey press
keyboard.add_hotkey(sr_hotkey, start_sr)


#welcome message
welcome_msg()
    


    




