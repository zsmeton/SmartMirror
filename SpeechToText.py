import speech_recognition as sr

from FileSettings import INPUT_STRING_FILE

r = sr.Recognizer()
while True:
    with sr.Microphone() as source:
        # Wait for audio
        audio = r.listen(source)
        with open(INPUT_STRING_FILE, "a+") as speechFile:
            try:
                # Run recognition on audio
                micIn = r.recognize_google(audio)
                # Write the string of text to the input file
                speechFile.write(micIn + '\n')
                print('Heard:', micIn)
            except sr.UnknownValueError:
                print("Mirror could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech  Recognition service; {0}".format(e) + '\n')
