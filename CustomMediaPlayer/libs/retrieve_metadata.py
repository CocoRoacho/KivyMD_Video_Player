import ffmpeg
import os, sys, tkinter as tk
from random import randint


def get_vid_duration(vpath):
    """ 
        try to read the length of a video file from meta data.
    
        Needs arg filename(with path)

        returns a float type (duration in milliseconds) 
    """

    # uses ffprobe command to extract all possible metadata from the media file
    meta = ffmpeg.probe(vpath)["streams"]

    # tries to retrieve the video duration, if metadata does not exist set value to -1
    
    # video stream
    try:
        v_dur = float(meta[0]['duration'])
    except KeyError:
        v_dur = -1

    # audio stream
    try:
        a_dur = float(meta[1]['duration'])
    except KeyError:
        a_dur = -1

    #print(f"duration: {v_dur}; {a_dur} -> max: {max(v_dur, a_dur)}")
    
    # compare video and audio stream and use the higher value as right choice
    return max(v_dur, a_dur)


def generate_thumbnail(in_filename, out_filename, targetwidth=300):
    """ 
        generate a thumbnail from the video file from a randomly chosen position. 
    
        needs args: 'input file', 'output file' 
    
    """

    #targetwidth = 300 # my prefered size of the thumbnail width
    targetheight = -1 # to keep original aspect ratio with width

    ###probe = ffmpeg.probe(in_filename) # needed for working with metadata

    # try to retrieve the duration from metadata, on error set value to 10 seconds (are good, shorter videos possible???)
    try:
        time = get_vid_duration(in_filename) #float(probe['streams'][0]['duration']) // 2
    except KeyError:
        time = float(10)
        # TODO find a way to calc duration and not set default value to 10 seconds

    try:
        (
            ffmpeg
            .input(in_filename, ss=time*(randint(10, 90)/100)) #ss='00:05:32.435' for get the pic from a random position in the stream between 10 and 90 %
            .filter('scale', targetwidth, targetheight)
            .output(out_filename, vframes=1)
            .overwrite_output() 
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        sys.exit(1)

