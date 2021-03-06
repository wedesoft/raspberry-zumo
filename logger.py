import cv2
import yaml
from data import count_files


def write_image(file_name, image):
    cv2.imwrite(file_name, image)


class Logger:
    def __init__(self, image_file_format='images/image%06d.%s'):
        self.image_file_format = image_file_format
        self.count = count_files(image_file_format.replace('%s', 'jpg'))

    def log(self, image, left_drive, right_drive):
        write_image(self.image_file_format % (self.count, 'jpg'), image)
        with open(self.image_file_format % (self.count, 'yml'), 'w') as f:
            yaml.dump([left_drive, right_drive], f)
        self.count += 1
