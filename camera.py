try:
    from picamera.array import PiRGBArray
    from picamera import PiCamera
except ImportError:
    pass


# http://picamera.readthedocs.io/en/release-1.10/fov.html
class Camera:
    def __init__(self, resolution=(320, 240)):
        self.camera = PiCamera(resolution=resolution, sensor_mode=6, framerate=42)
        self.camera.iso = 800
        self.resolution = resolution

    def capture(self):
        raw_capture = PiRGBArray(self.camera, size=self.resolution)
        self.camera.capture(raw_capture, format="bgr")
        return raw_capture.array
