import google.cloud.vision as vision
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secret_key.json"
import io


class PlagiarismCheck(object):
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()

    def get_text(self, path):
        with io.open(path, 'rb') as image_file:
            content = image_file.read()
        image = vision.types.Image(content=content)
        resp = self.client.text_detection(image=image)
        text = ' '.join([d.description for d in resp.text_annotations])
        print(text)
        return text



if __name__=="__main__":
    obj = PlagiarismCheck()
    obj.get_text("text_2.png")