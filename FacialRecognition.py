import codecs
import json
import os
import random
import time

import face_recognition
import numpy as np

from FileSettings import OUTPUT_STRING_FILE, CAMERA_OUTPUT_FILE


# turn numpy array into a json dumpable form
def np_json_dump(path: str, a: np.ndarray):
    """
    Creates a file where json dumps a numpy ndarray then dumps the array using utf-8 encoding

    :param path: path to file where numpy array will be dumped
    :param a: Numpy Array to json dump
    """
    json.dump(a.tolist(), codecs.open(path, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True,
              indent=4)  # this saves the array in .json format


# read in numpy array from json dump
def np_json_read(path: str) -> np.ndarray:
    """
    Reads in a file where json dumped a numpy ndarray

    :param path: path to file where numpy array was dumped by json
    :return: numpy ndarray from the file
    """
    return np.array(json.loads(codecs.open(path, 'r', encoding='utf-8').read()))


class FaceRecognizer:
    def __init__(self, enc_location: str, name_conv_location: str):
        self.known = enc_location
        self.name_converter = name_conv_location
        self.columnToName = dict()
        self.knownMatrix = []
        self.who = None
        self.looking = False
        self.load_known()

    # Json dump face encoding in known_faces
    def create_enc_file(self, encoding, name: str) -> str:
        """
        Creates a file and outputs the facial features encoding

        :param loaded_image: a face_recognition loaded file
        :param name: name of the individual in the loaded image
        :return: name of file where encoding was outputted
        """
        # Creates a file by generating a file of form #.enc
        # Will continue to attempt different encoding names until it finds a new path
        i = 0
        while os.path.exists(os.path.join(self.known, f"{i}.enc")):
            i += 1
        # save the encoding using np_json_dump encoding in directory self.known
        if len(encoding) > 0:
            np_json_dump(os.path.join(self.known, f"{i}.enc"), encoding)
        else:
            return None
        # save the encoding file to the name of the face
        with open(os.path.join(self.known, self.name_converter), 'a') as n:
            n.write(f"\n{i}.enc:{name}")
        return f"{i}.enc"

    def load_known(self):
        """
        Loads in all face encodings and names of people to recognize from the self.known file path
        """
        conversion_file = os.path.join(self.known, self.name_converter)
        with open(conversion_file) as file:
            for i, line in enumerate(file):
                # Adds the encoding to the knownMatrix as a row for effecient mass comparison Least Squares
                self.knownMatrix.append(np_json_read(os.path.join(self.known, line.split(sep=':')[0].strip())))
                # Generates a dictionary of rows to names
                self.columnToName[i] = line.split(sep=':')[1].strip()
        print("Loaded all known faces")

    # add person to known_faces
    def add_person(self, image: str, name: str) -> bool:
        """
        Adds a person to the set of known people to recognize

        :param image: path to image file
        :param name: output of identifying that individual
        :return: boolean as to whether the person was successfully added
        """
        # begin facial recognition on image
        loaded_image = face_recognition.load_image_file(image)
        # Run facial recognition on loaded image
        encoding = face_recognition.face_encodings(loaded_image)[0]
        # passes the first encoding as a parameter to create the encoding file
        enc = self.create_enc_file(encoding, name)
        # Add the new user to the current knownMatrix and add mapping
        if enc is not None:
            self.knownMatrix.append(np_json_read(os.path.join(self.known, enc)))
            self.columnToName[len(list(self.knownMatrix)) - 1] = self.who.clear()
            return True
        else:
            return False

    def who_is_it(self, unknown_file_name: str):
        """
        Runs image against list of known faces

        :param unknown_file_name: path to image of person
        """
        # Get encodings of faces
        unknown_picture = face_recognition.load_image_file(unknown_file_name)
        unknown_face_encoding = face_recognition.face_encodings(unknown_picture)
        # Clear old users
        self.who = []
        # If no encodings set current user to unknown
        if len(unknown_face_encoding) < 1:
            self.who = ['unknown']
        else:
            for face in unknown_face_encoding:
                # Compare the faces in unknown face encoding to the knownMatrix rows
                comparison = face_recognition.compare_faces(self.knownMatrix, face)
                # if face matches a known face, add the names of each user to currently identified
                self.who.extend([self.columnToName[i] for i, index in enumerate(comparison) if index])
            if not self.who:
                self.who = ['unknown']

    def are_they_looking(self, unknown_file_name: str):
        """
        Detects whether or not anyone is directly looking at the camera in
        the unknown_file_name
        :param unknown_file_name:
        """
        # run face landmarks on image
        image = face_recognition.load_image_file(unknown_file_name)
        landmarks = face_recognition.face_landmarks(image)
        # return if any of the people in the image had distinctly found left and right eyes
        for index in landmarks:
            if 'left_eye' in index and 'right_eye' in index:
                self.looking = True
                return
        self.looking = False

    def update(self, unknown_file_name: str):
        """
            Runs who_is_it() and are_they_looking, which will update
            self.who and self.looking
            :param unknown_file_name: path to image of person
        """
        self.are_they_looking(unknown_file_name)
        self.who_is_it(unknown_file_name)


if __name__ == "__main__":
    PYCAMERA = False
    SAY_HELLO_TIMER = 60  # seconds since last recogntion before removing them
    SLEEP = 0.25  # Seconds between photo
    POSSIBLE_GREETINGS = ['You look wonderful', 'Hello', 'Nice to see you', 'Whats the haps', 'Hows it hanging',
                          'Welcome', 'Welcome to your doom', 'You are crushing it today', 'Good morning',
                          ' Good afternoon', 'Good evening', 'Hi', 'Hey', 'Good to see you', "It's great to see you"]
    # Take a photo every second and if the user is identified ask the mirror to say hello to the user
    last_run = time.time()
    users = {}  # hold the user and their last recognition time
    if PYCAMERA:
        import picamera

        camera = picamera.PiCamera()
    rec = FaceRecognizer(enc_location='known_faces', name_conv_location='pictureNames.conv')
    try:
        while True:
            # Wait until sleep timer is done
            while time.time() < last_run + SLEEP:
                time.sleep(SLEEP / 10)
            last_run = time.time()  # Update the last run timer
            if PYCAMERA:
                # Take a picture and run recogntion
                camera.capture(CAMERA_OUTPUT_FILE)
            rec.update('unknown.png')  # CAMERA_OUTPUT_FILE)
            print('Finished running facial recognition on image')
            # Say hello if new user recognition
            for user in rec.who:
                if user not in users:
                    users[user] = time.time()
                    with open(OUTPUT_STRING_FILE, "a") as fout:
                        # Select a random greeting
                        fout.write(f'\n{POSSIBLE_GREETINGS[random.randrange(len(POSSIBLE_GREETINGS))]}, {user}')
                # Update last seen timer if recognized again
                else:
                    users[user] = time.time()
            # Remove old users
            for key, value in users.items():
                if value > time.time() + SAY_HELLO_TIMER:
                    del users[key]

    except KeyboardInterrupt:
        if PYCAMERA:
            camera.close()
    finally:
        if PYCAMERA:
            camera.close()
