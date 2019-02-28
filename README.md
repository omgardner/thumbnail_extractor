# Thumbnail Extractor
Extract thumbnails from videos on some websites. 

Converts the thumbnail into a gif.

> Currently supports Twitch.


# How to Run
Create ./files/auth.json with the contents: 


    {
        "twitch": {
            "client_id": "YOUR_CLIENT_ID",
            "oauth_token": "YOUR_OAUTH_TOKEN"
        }
    }


# requirements
**Python Requirements**: see requirements.txt

**ImageMagick**:
    command used follows format:
        
        "magick convert -delay 20 -loop 0 {glob_cmd} {result_filepath}"