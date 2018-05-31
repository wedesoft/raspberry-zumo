import pytest
from mock import MagicMock, call
import logger
from logger import *


class TestLogger:
    @pytest.fixture
    def target(self):
        return Logger('/tmp/image%04d.%s')

    @pytest.fixture
    def image(self):
        return MagicMock(name='image')

    @pytest.fixture(autouse=True)
    def write_image(self, monkeypatch):
        monkeypatch.setattr(logger, 'write_image', MagicMock(name='write_image'))
        return logger.write_image

    def test_save_image(self, target, image, write_image):
        target.log(image, 0, 0)
        write_image.assert_called_with('/tmp/image0000.png', image)

    def test_increase_counter(self, target, image, write_image):
        target.log(image, 0, 0)
        target.log(image, 0, 0)
        assert write_image.call_args_list == [call('/tmp/image0000.png', image), call('/tmp/image0001.png', image)]

    def test_write_yaml(self, target, image):
        target.log(image, 25.0, 65.0)
        with open('/tmp/image0000.yml') as f:
            assert yaml.load(f) == [25.0, 65.0]

    def test_write_second_yaml_file(self, target, image):
        target.log(image, 25.0, 65.0)
        target.log(image, 35.0, 75.0)
        with open('/tmp/image0001.yml') as f:
            assert yaml.load(f) == [35.0, 75.0]
