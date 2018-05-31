try:
    from picamera.array import PiRGBArray
    from picamera import PiCamera
except ImportError:
    pass


class Camera:
    def __init__(self, resolution=(320, 240)):
        self.camera = PiCamera(resolution=resolution, sensor_mode=3, framerate=10)
        self.resolution = resolution

    def capture(self):
        raw_capture = PiRGBArray(self.camera, size=self.resolution)
        self.camera.capture(raw_capture, format="bgr")
        return raw_capture.array
