from PIL import Image
import numpy as np
from numpy import expand_dims
from keras_vggface.utils import preprocess_input
import cv2
from keras.models import load_model


class FacialRecognition:
    def __init__(self):
        self.model = load_model('api/obj_classification_api/saved_model.hdf')
        # https://github.com/keras-team/keras/issues/6124
        self.model._make_predict_function()
        self.face_cascade = cv2.CascadeClassifier('api/obj_classification_api/haarcascade_frontalface_alt2.xml')
        self.labels = {0: 'Elbert Widjaja', 1: 'Jason Gunawan', 2: 'Nicholas', 3: 'QunJia', 4: 'ignore'}

    def predict_face(self, data):
        try:
            data = np.array(data)
            extracted_face, box = self.extract_face_from_img(data)
            predicted = self.model.predict([self.resize_face(extracted_face)])
            n = np.argmax(predicted, axis=1)[0]
            score = predicted[0][n]
            (x1, y1, x2, y2) = box
            boxes = {
                'x': x1,
                'y': y1,
                'width': x2 - x1,
                'height': y2 - y1
            }
            return [self.labels[n], score, boxes]
        except Exception as e:
            return [None, None, None]

    def extract_face_from_img(self, data):
        img = data
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray)

        if faces != ():
            (x, y, w, h) = faces[0]
            x1, y1, x2, y2 = x, y, x + w, y + h
            roi_color = img[y:y + h, x:x + w]
            return roi_color, (x1, y1, x2, y2)
        else:
            return None

    def resize_face(self, face):
        # modify and resize pixels to the model size
        image = Image.fromarray(face)
        image = image.resize((224, 224))

        face_array = np.asarray(image)
        # convert face into samples
        pixels = face_array.astype('float32')

        samples = expand_dims(pixels, axis=0)
        # prepare the face for the model, e.g. center pixels
        samples = preprocess_input(samples, version=2)
        return samples