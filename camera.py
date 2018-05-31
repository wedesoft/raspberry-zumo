try:
    from picamera.array import PiRGBArray
    from picamera import PiCamera
except ImportError:
    pass


class Camera:
    def __init__(self, resolution=(640, 480)):
        self.camera = PiCamera(resolution=resolution, sensor_mode=3, framerate=10)
        self.raw_capture = PiRGBArray(self.camera, size=resolution)

    def capture(self):
        self.camera.capture(self.raw_capture, format="bgr")
        return self.raw_capture.array
