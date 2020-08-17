from django.test import TestCase
from api.obj_classification_api import faceRec
from PIL import Image


class ImageClassificationTestCase(TestCase):
    def setUp(self):
        self.models = faceRec.FacialRecognition()

    def test_face_image_labeled(self):
        image_object = Image.open('api/tests/integrations/test_images/test.jpg')
        
        name, probability, boxes = self.models.predict_face(image_object)

        self.assertEqual(name, 'Elbert Widjaja')

    def test_face_image_ignored(self):
        image_object = Image.open('api/tests/integrations/test_images/ignored.jpg')
        
        name, probability, boxes = self.models.predict_face(image_object)

        self.assertEqual(name, 'ignore')

    def test_no_face_image(self):
        image_object = Image.open('api/tests/integrations/test_images/wallpaper.jpg')
        
        name, probability, boxes = self.models.predict_face(image_object)

        self.assertEqual(name, None)
