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
import csv
from googletrans import Translator
import datetime


sr_hotkey='f2'

NAME='Adam'
LANGUAGE='en'

commands_csv='commands.csv'
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
      
############## HELPER FUNCTIONS #####################
#convert a list of strings into a single string
def list2str(listofstr):
    returnstr=''
    for i in range(len(listofstr)):
        if i!=0:
            returnstr+=" "
        returnstr+=listofstr[i]
    return returnstr
def list2str_comma(listofstr):
    returnstr=''
    for i in range(len(listofstr)):
        if i!=0:
            returnstr+=","
        returnstr+=listofstr[i]
    return returnstr

#text to speech for given input string
def tts(mytext):
    global LANGUAGE
    if mytext!='':
        myobj = gTTS(text=mytext, lang=LANGUAGE, slow=False)
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
    
#confused phrases indicating there was an error with speech regog
def no_voice_recog():
    phrases=["I missed that","I couldn't hear you"]
    rand_tts(phrases)
    
#confused phrases indicating the command was not recognized
def bad_command():
    phrases=["What did you say?","I don't know that one","Sorry?"]
    rand_tts(phrases)
    

#play listening sound
def listeningsound():
    playsound('listening.mp3')


#play failure sound
def failsound():
    playsound('error_sound.mp3')
    
#key press
def pressbutton(button):
    pya.press(button)
    
#key press n times in rapid succession
def pressbuttonn(button,n):
    for i in range(int(n)):
        pya.press(button)
        
#press combination of hotkeys
def hotkeys(*arg):
    pya.hotkey(*arg)
    
#digest csv file with commands and return id, fn, args (strings or lists of strings)
def csv2lists(fname):
    datafile = open(fname, 'r')
    myreader = csv.reader(datafile)
    
    identifiers=[]
    functions=[]
    arguments=[]
    for row in myreader:
        identifiers.append(row[0].split(','))
        functions.append(row[1])
        arguments.append(row[2].split(','))
        
    identifiers=identifiers[1:len(identifiers)]
    functions=functions[1:len(functions)]
    arguments=arguments[1:len(arguments)]
    return identifiers,functions,arguments



#take command and a phrase and trim the command to everything after this phrase
def trim_cmd_2_phrase(cmd,phrase):
    cmdlist=cmd.split(phrase)
    text2write=cmdlist[1][1:]#also remove space from first char spot
    return text2write


# write note in text file
def write_note(cmd,idp):
    text2write=trim_cmd_2_phrase(cmd,idp)
    f = open(notefolder+"\\notes.txt", "a")
    f.write(text2write+'\n')
    f.close()
    completion()
    
# search for program in windows and open
def open_program(cmd,idp):
    text2write=trim_cmd_2_phrase(cmd,idp)
    affirmation()
    pya.press('win')
    time.sleep(0.5)
    pya.write(text2write)
    time.sleep(0.5)
    pya.press('enter')
    
#change name of user
def name_change(cmd,idp):
    global NAME
    NAME=trim_cmd_2_phrase(cmd,idp)
    tts("OK, "+NAME)
    
#name confirmation
def myname(dne):
    tts("You asked me to call you "+NAME)

#calculate math equation
def calc(cmd,idp):
    eqn=trim_cmd_2_phrase(cmd,idp)
    soln=eval(eqn)
    response=eqn + " = " +str(soln)
    print(response)
    tts(response)
    
#repeat the following phrase
def repeat(cmd,idp):
    phrase=trim_cmd_2_phrase(cmd,idp)
    tts(phrase)
    
#change language of tts speaker
def chng_lang(cmd,idp):
    global LANGUAGE
    lang=trim_cmd_2_phrase(cmd,idp)
    langlist=['Spanish','English','French','Portuguese','Mandarin']
    abbrevlist=['es','en','fr','pt','zh-CN']
    for i in range(len(langlist)):
        if langlist[i]==lang:
            LANGUAGE=abbrevlist[i]
            tts("OK, I am "+langlist[i]+" now.")
            return 0

    tts("I don't know that language.")
    
#type text
def type_text(cmd,idp):
    textblock=trim_cmd_2_phrase(cmd,idp)
    pya.write(textblock)
    completion()
    
def type_code(*args):
    pya.write(list2str_comma(args))
    
    
#translate english to some other language
# def translate(cmd,idp):
#     textblock=trim_cmd_2_phrase(cmd,idp)
#     textlist=textblock.split(" to ")
#     translator = Translator()
#     translated=translator.translate(textlist, dest='ko')
#     tts(translated)
#     completion()

################# MAIN CONTROL FUNCTIONS #####################

#convert function and arguments into function evaluation
# - additionally take cmd and idp to optionally pass to function
def stringeval(strfn,cmd,idp,strargs):
    argsstring=''
    if strargs[-1]=='singlearg':
        argsstring="'"+list2str_comma(strargs[0:-1])+"'"
    else:
        for i in range(len(strargs)):
            if i>0:
                argsstring+=","
            if strargs[i]=='cmd' or strargs[i]=='idp':
                argsstring+=strargs[i]
            else:
                argsstring+="\'"+strargs[i]+"\'"
    
    funeval=strfn+"("+argsstring+")"
    eval(funeval)
    
#determine if given command starts with any of the identifiers
# - currently only takes first word (ie if id=next song, and cmd=next)
# - return boolean and the id that was used
def iscommand(cmd,ids):
    for i in range(len(ids)):
        cmdsec=list2str(cmd.split(' ')[0:len(ids[i].split(" "))])
        if cmdsec==ids[i]:
            return True,ids[i]
    return False,None


#define what to do with speech recognition command
def control_fn(cmd):
    #look through CSV for matching identifier and function/argument pair
    identifiers,functions,arguments=csv2lists(commands_csv)
    for i in range(len(identifiers)):
        [iscmd,idp]=iscommand(cmd,identifiers[i])
        if iscmd:
            fn=functions[i]
            args=arguments[i]
            stringeval(fn,cmd,idp,args)
            return 0
    #if it gets here, something has failed
    bad_command()
        
    
#define function for starting speech recognition
def start_sr():
    cmd=listen_sr()
    if cmd!=0:
        try:
            print("You said: " + cmd)
            control_fn(cmd)
        except Exception as e:
            print("ERROR",e)
            failsound()

#only the speech recognition part
# - output is user command
def listen_sr():
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
        return recog

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        no_voice_recog()
        return 0
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        no_voice_recog()
        return 0
        
        
def welcome_msg():
    global NAME
    
    time_hour=datetime.datetime.now().hour
    if time_hour>3 and time_hour<12:
        greeting="Good morning"
    elif time_hour>=12 and time_hour<6:
        greeting="Good afternoon"
    else:
        greeting="Good evening"
    
    msg=greeting+" "+NAME#+". Press "+sr_hotkey+" to give commands."
    tts(msg)

########## Start of Program ##############

#look for hotkey press
keyboard.add_hotkey(sr_hotkey, start_sr)


#welcome message
welcome_msg()
    


    




