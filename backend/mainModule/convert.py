import ffmpeg


video = ffmpeg.input('vid.mp4')
video.audio.output('audio.mp3').run()
