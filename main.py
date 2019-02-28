import logging
import argparse


if __name__ == "__main__":
    logging.basicConfig(filename='testing.log', level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("-dirpath", default='out')
    parser.add_argument("-url", default=None)
    kwargs = parser.parse_args()
    
    platform = TwitchPlatform(dirpath=kwargs.dirpath)

    # download all thumbnail images
    platform.download_preview_frames(kwargs.url)

    # convert to GIF
    platform.imgs_to_gif()

    # close session
    platform.done()
