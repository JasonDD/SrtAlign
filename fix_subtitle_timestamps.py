#!/usr/bin/env python

'''
Anil Ramakrishna | akramakr@usc.edu
Uses gentle and pysrt to fix out of sync subtitles

PRE-REQUISITES:
-> gentle: https://github.com/lowerquality/gentle
-> pysrt: https://pypi.python.org/pypi/pysrt
-> ffmpeg: https://www.ffmpeg.org/download.html
-> python2.7 for gentle

USAGE:
-> This script takes as input three directories:
    * gentledir: Directory containing gentle source code,
            in specific the align.py file
    * srtdir: Directory containing srt files to be aligned
    * One of the following two should be supplied
        - videodir: Directory containing video files 
        - audeodir: Directory containing audeo files if available.
            Saves time by avoiding extracting them again
-> Set path for python2.7 below before execution
-> File usage:
    force_align_subtitles.py <gentledir> <videodir> <srtdir>
-> Output: the aligned subtitles are written in a newly created
directory named alignedsrt in the same path as <srtdir>
'''

import os
import sys
import argparse
import subprocess
#from extract_srt import extract_srt
#from extract_text import extract_text

python2 = '/Users/anil/anaconda3/envs/python2.7/bin/python'
p = argparse.ArgumentParser(description='Fix out of sync subtitles using gentle force aligner')
p.add_argument("gentledir", type=str, help="Full/relative path for gentle installation dir")
p.add_argument("srtdir", type=str, help="Full/relative path for srt files (same name as audio)")

group = p.add_mutually_exclusive_group(required=True)
group.add_argument('--videodir', type=str, dest='videodir', \
    help='Full/relative path for video files')
group.add_argument('--audiodir', type=str, dest='audiodir', \
    help='Full/relative path for audio files')

a=p.parse_args()

srtdir = a.srtdir.rstrip('/')
gentledir = a.gentledir.rstrip('/')

if a.audiodir != None:
    audiodir = a.audiodir.rstrip('/')
else:
    videodir = a.videodir.rstrip('/')

    #Extract audio files from videodir

    print("\n")
    print("----------------------")
    print("Extracting audio files")
    print("----------------------")
    print("\n")
    
    #Create new directory for audio files
    if not os.path.exists(videodir):
        sys.exit("Video directory doesn't exist")
    audiodir = os.path.dirname(videodir) + '/audiofiles'
    if not os.path.exists(audiodir):
        os.mkdir(audiodir)
    
    videofiles = os.listdir(videodir)
    for video_f in videofiles:
        audio_f = '.'.join(video_f.split('.')[:-1]) + '.wav'
    
        command_str = 'ffmpeg -i {0}/{1} -vn {2}/{3}'.\
            format(videodir, video_f, audiodir, audio_f)
    
        print(command_str)
    
        subprocess.call(command_str, shell=True)

print("\n")
print("---------------------")
print("Extracting text files")
print("---------------------")
print("\n")

#Extract text from srt
srtfiles = os.listdir(srtdir)
textdir = os.path.dirname(srtdir) + '/text'
if not os.path.exists(textdir):
    os.mkdir(textdir)

for srt_f in srtfiles:
    if not srt_f.endswith('.srt'):
        continue

    text_f = srt_f.replace('.srt', '.txt')
    command_str = './extract_text.py {0}/{1} {2}/{3}'.\
        format(srtdir, srt_f, textdir, text_f)

#    print(command_str)

    subprocess.call(command_str, shell=True)

print("\n")
print("--------------")
print("Running gentle")
print("--------------")
print("\n")

#Run gentle
audiofiles = os.listdir(audiodir)
textfiles = os.listdir(textdir)
textdir = os.path.dirname(srtdir) + '/text'
outdir = os.path.dirname(srtdir) + '/gentleout'
if not os.path.exists(outdir):
    os.mkdir(outdir)

for audio_f in audiofiles:
    #TODO: change this to accept other file formats
    if not audio_f.endswith('.wav'):
        continue

    text_f = audio_f[:-4] + '.txt'
    if text_f not in textfiles:
        sys.exit('Text file {0} not found, exiting!'.format(text_f))

    out_f = outdir + '/' + audio_f[:-4] + '.json'
    command_str = '{0} {1}/align.py {2}/{3} {4}/{5} -o {6}'.\
        format(python2, gentledir, audiodir, audio_f, textdir, text_f, out_f)

#    print(command_str)

    subprocess.call(command_str, shell=True)

print("\n")
print("---------------------------------")
print("Extracting srt from gentle output")
print("---------------------------------")
print("\n")

#Extract srt from gentle output
outfiles = os.listdir(outdir)
aligneddir = os.path.dirname(srtdir) + '/alignedsrt'
if not os.path.exists(aligneddir):
    os.mkdir(aligneddir)

for out_f in outfiles:
    if not out_f.endswith('.json'):
        continue

    aligned_f = out_f[:-5] + '.srt'
    command_str = './extract_srt.py {0}/{1} {2}/{3} {4}/{3}'.\
        format(outdir, out_f, aligneddir, aligned_f, srtdir)

#    print(command_str)
    subprocess.call(command_str, shell=True)

print("Done")
