import pytest
from mock import MagicMock, call
import logger
from logger import *


class TestLogger:
    @pytest.fixture
    def target(self):
        return Logger('/tmp/image%06d.%s')

    @pytest.fixture
    def image(self):
        return MagicMock(name='image')

    @pytest.fixture(autouse=True)
    def write_image(self, monkeypatch):
        monkeypatch.setattr(logger, 'write_image', MagicMock(name='write_image'))
        return logger.write_image

    @pytest.fixture(autouse=True)
    def count_files(self, monkeypatch):
        monkeypatch.setattr(logger, "count_files", MagicMock(name='count_files'))
        logger.count_files.return_value = 0
        return logger.count_files

    def test_save_image(self, target, image, write_image):
        target.log(image, 0, 0)
        write_image.assert_called_with('/tmp/image000000.jpg', image)

    def test_increase_counter(self, target, image, write_image):
        target.log(image, 0, 0)
        target.log(image, 0, 0)
        assert write_image.call_args_list == [call('/tmp/image000000.jpg', image), call('/tmp/image000001.jpg', image)]

    def test_check_for_old_files(self, image, target, count_files):
        count_files.assert_called_with('/tmp/image%06d.jpg')

    def test_dont_overwrite_old_files(self, image, write_image, count_files):
        count_files.return_value = 10
        target = Logger('/tmp/image%06d.%s')
        target.log(image, 0, 0)
        write_image.assert_called_with('/tmp/image000010.jpg', image)

    def test_write_yaml(self, target, image):
        target.log(image, 25.0, 65.0)
        with open('/tmp/image000000.yml') as f:
            assert yaml.load(f) == [25.0, 65.0]

    def test_write_second_yaml_file(self, target, image):
        target.log(image, 25.0, 65.0)
        target.log(image, 35.0, 75.0)
        with open('/tmp/image000001.yml') as f:
            assert yaml.load(f) == [35.0, 75.0]
