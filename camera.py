try:
    from picamera.array import PiRGBArray
    from picamera import PiCamera
except ImportError:
    pass


# http://picamera.readthedocs.io/en/release-1.10/fov.html
class Camera:
    def __init__(self, resolution=(320, 240)):
        self.camera = PiCamera(resolution=resolution, framerate=90)
        self.camera.hflip = True
        self.camera.vflip = True
        self.resolution = resolution

    def capture(self):
        raw_capture = PiRGBArray(self.camera, size=self.resolution)
        self.camera.capture(raw_capture, format="bgr", use_video_port=True)
        return raw_capture.array
