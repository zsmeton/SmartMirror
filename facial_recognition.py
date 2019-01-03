import codecs
import json
import os

import face_recognition
import numpy as np


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
        self.people = dict()
        self.load_known()

    # Json dump face encoding in known_faces
    def create_enc_file(self, loaded_image, name: str) -> str:
        """
        Creates a file and outputs the facial features encoding

        :param loaded_image: a face_recognition loaded file
        :param name: name of the individual in the loaded image
        :return: name of file where encoding was outputted
        """
        i = 0
        while os.path.exists(os.path.join(self.known, f"{i}.enc")):
            i += 1
        encoding = face_recognition.face_encodings(loaded_image)[0]
        if len(encoding) > 0:
            np_json_dump(os.path.join(self.known, f"{i}.enc"), encoding)
        else:
            return None
        with open(os.path.join(self.known, self.name_converter), 'a') as n:
            n.write(f"\n{i}.enc:{name}")
        return f"{i}.enc"

    def load_known(self):
        """
        Loads in all face encodings and names of people to recognize from the self.known file path
        """
        conversion_file = os.path.join(self.known, self.name_converter)
        with open(conversion_file) as file:
            for line in file:
                self.people[line.split(sep=':')[1].strip()] = \
                    np_json_read(os.path.join(self.known, line.split(sep=':')[0].strip()))
        print("Loaded all known faces")

    # add person to known_faces
    def add_person(self, image: str, name: str) -> bool:
        """
        Adds a person to the set of known people to recognize

        :param image: path to image file
        :param name: output of identifying that individual
        :return: boolean as to whether the person was successfully added
        """
        loaded_image = face_recognition.load_image_file(image)
        enc = self.create_enc_file(loaded_image, name)
        if enc is not None:
            self.people[name] = np_json_read(os.path.join(self.known, enc))
            return True
        else:
            return False

    def who_is_it(self, unknown_file_name: str) -> set:
        """
        Runs image against list of known faces

        :param unknown_file_name: path to image of person
        :return: name of person(s) in image or unknown
        """
        unknown_picture = face_recognition.load_image_file(unknown_file_name)
        unknown_face_encoding = face_recognition.face_encodings(unknown_picture)
        if len(unknown_face_encoding) < 1:
            print('Unable to identify any individuals')
        else:
            known_faces = set()
            for face in unknown_face_encoding:
                for name, enc in self.people.items():
                    # Now we can see the two face encodings are of the same person with `compare_faces`!
                    if face_recognition.compare_faces([enc], face)[0]:
                        known_faces.add(name)
            if known_faces:
                return known_faces
        return {'unknown'}


if __name__ == "__main__":
    rec = FaceRecognizer(enc_location='known_faces', name_conv_location='pictureNames.conv')
    path = input('Type in path to unknown image')
    print(rec.who_is_it(path))

