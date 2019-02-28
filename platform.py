from util import load_mime, load_json
import requests
import os
from os.path import abspath
from urllib.parse import urlparse
from pymaybe import maybe
import cv2
from glob import glob
import numpy as np
import subprocess
import logging


class Platform():
    """
    thumb_shape = (thumb height, thumb width)
    """

    def __init__(self, dirpath, thumb_shape=(124, 220), **kwargs):
        self.thumb_shape = thumb_shape
        self.dirpath = abspath(dirpath)
        self.mime = maybe(load_mime(abspath('files/mime.json')))
        self.session = requests.Session()

    def create_composite_image(self, axis=0):
        """
        Combine all the images in a directory vertically or horizontally
        axis:
            0:  vertically
            1:  horizontally
        """
        # get all images
        image_paths = glob(self.download_filepath+"/*.*")
        # load into memory as ndarray
        image_objs = [cv2.imread(path) for path in image_paths]
        # create composite image
        composite_image = np.concatenate(image_objs, axis=axis)

        # save composite image
        self.composite_filepath = os.path.join(self.dirpath, "composite.jpg")
        cv2.imwrite(self.composite_filepath, composite_image)

        logging.info('Saved images to composite:')
        logging.info(*image_paths, sep='\n')

    def split_composite_image(self):
        """
        splits the single image into individual thumbnail frames
        """
        img = cv2.imread(self.composite_filepath)

        height, width = img.shape[:2]
        step_h, step_w = self.thumb_shape

        self.split_dirpath = os.path.join(self.dirpath, 'split')
        os.makedirs(self.split_dirpath, exist_ok=True)

        # does each row, then each element in row
        count = 0
        for h in range(0, height, step_h):
            for w in range(0, width, step_w):
                count += 1
                crop_img = img[h:h+step_h, w:w+step_w]

                save_filepath = os.path.join(
                    self.split_dirpath, f'{count}.jpg')
                cv2.imwrite(save_filepath, crop_img)
                logging.info(f'{count}.jpg saved.')

    def imgs_to_gif(self):
        """ function based around multiple blogs, for example:
                http://superfluoussextant.com/making-gifs-with-python.html

        """
        # split images into individual thumbnail frames
        self.create_composite_image()
        self.split_composite_image()

        glob_cmd = "{}/*.*".format(self.split_dirpath.replace("\\", "/"))
        result_filepath = os.path.join(self.dirpath, "result.gif")
        # TODO improve method of args separation; currently splits on " " character..
        # TODO adjust speed of gif
        gif_cmd = f"magick convert -delay 20 -loop 0 {glob_cmd} {result_filepath}".split(
            " ")
        subprocess.run(gif_cmd)

        logging.info(f"GIF saved to {result_filepath}")

    def save_file(self, response, filepath):
        with open(filepath, 'wb') as f:
            for chunk in response:
                f.write(chunk)

    @staticmethod
    def file_from_url(url):
        return urlparse(url).path.split('/')[-1]

    def done(self):
        """close session
        """
        self.session.close()


class TwitchPlatform(Platform):
    def __init__(self, **kwargs):
        thumb_shape = (124, 220)
        Platform.__init__(self, thumb_shape=thumb_shape, **kwargs)

    def download_preview_frames(self, url):
        # init
        video_id = self.file_from_url(url)
        api_url = f'https://api.twitch.tv/kraken/videos/{video_id}'
        params = load_json('files/auth.json')['twitch']

        video_r = self.session.get(api_url, params=params, stream=True)
        video_json = video_r.json()

        # error handling
        if 'error' in video_json:
            logging.info(f"Error Code: {video_json['status']}")
            logging.info(video_json['error'])

        channel_name = video_json['channel']['name']

        # cannibalise another url to get the required portion
        streamer_ref = [ele for ele in video_json['preview'].split(
            '/') if channel_name in ele][0]
        quality = 'high'

        self.download_filepath = os.path.join(self.dirpath, "download")
        os.makedirs(self.download_filepath, exist_ok=True)
        # many more storyboards than expected. stop once the nth storyboard returns a bad response
        for n in range(0, 50):
            sboard_url = f"https://vod-storyboards.twitch.tv/{streamer_ref}/storyboards/{video_id}-{quality}-{n}.jpg"
            sboard_response = self.session.get(sboard_url, stream=True)

            if sboard_response.ok:
                filename = self.file_from_url(sboard_url)

                if '.' not in filename:
                    # using monad, either find the correct extension, or default to jpeg format
                    filename += self.mime[sboard_response.headers['content-type']
                                          ].or_else('.jpg')
                filepath = os.path.join(self.download_filepath, filename)

                self.save_file(sboard_response, filepath)
                logging.info(sboard_url, 'saved!')

            elif sboard_response.status_code == 429:
                logging.info(sboard_url, "Error! Too Many Requests!")
                break

            else:
                logging.info(sboard_url, 'not found.')
                break
