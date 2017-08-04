import argparse, ffmpy, json, os, re, urllib.request
from datetime import date
from apscheduler.schedulers.blocking import BlockingScheduler

parser = argparse.ArgumentParser('Munich stream ripper + timelapse')
parser.add_argument('--source', type=int, required=True, help='0 - wetter.com, 1 - ludwigbeck.de')
parser.add_argument('--debug', type=int, default=0, help='0 - default stage, 1 - fade in/out stage, 2 - merge files stage')
args = parser.parse_args()
ff_exec = 'raw/ffmpeg.exe'

def ffmpeg_fade_merge(folder):
	print('ffmpeg routine')
	files = os.listdir('raw/%s' % folder) #get files
	if not os.path.exists('raw/%s/out/' % (folder)): #create output folder
		os.makedirs('raw/%s/out/' % (folder))
	for f in files:
		file = open('raw/%s/out/list.txt' % (folder),'a')
		file.write("file '%s'\n" % f) #list.txt for merge func later on
		file.close()
		
		ffmpeg_run(ff_exec, 'raw/%s/%s' % (folder, f), None, 'raw/%s/out/%s' % (folder, f), '-vf "fade=in:0:40,fade=out:1272:40" -af "afade=in:st=0:d=1,afade=out:st=51:d=1" -c:v "libx264" -crf "22" -preset "veryfast"')
		ffmpeg_run(ff_exec, 'raw/%s/out/list.txt' % (folder), '-f concat -safe 0', 'raw/%s.mp4' % (folder), '-c copy')
	
	os._exit(0)
	return
	
def ffmpeg_run(exec_, inputF, inputV, outputF, outputV):
	ff = ffmpy.FFmpeg(executable = exec_, inputs={inputF: inputV}, outputs={outputF: outputV})
	ff.run()
	return
	
def download(r, filename):
	with open(filename, 'wb') as f:
		while True:
			chunk = r.read(1024)
			if not chunk:
				break
			f.write(chunk)
	return
	
''' Munich Hauptbahnhof '''
def downloadStreamW(today_temp):
	#create today's folder
	today = str(date.today())
	if not os.path.exists('raw/' + today):
		os.makedirs('raw/' + today)
	
	if today_temp in str(date.today()):
		#get source url
		source_url = urllib.request.urlopen('http://www.wetter.com/hd-live-webcams/urls/54c645b312c4f/');
		data = json.loads(source_url.read().decode('utf-8'))
		stream_url = data[0]['file']

		#rip video from the stream
		global countW
		print('Downloading from %s' % stream_url)
		r = urllib.request.urlopen(stream_url)
		matchObj = re.match(r'http:(.*?)\/streams\/1\/(.*?)\?dcsdesign=WTP_wetter.com', stream_url, re.M|re.I)
		download(r, 'raw/%s/%06d_%s' % (today, countW, matchObj.group(2)))
		countW += 1
		print('Done')
		
	else:
		print('next day')
		ffmpeg_fade_merge(today_temp)
	return
	
''' Munich Marienplatz '''
def downloadStreamL(today_temp):
	#create today's folder
	today = str(date.today())
	if not os.path.exists('raw/' + today):
		os.makedirs('raw/' + today)
		
	if today_temp in str(date.today()):
		global countL
		r = urllib.request.urlopen('http://kaufhaus.ludwigbeck.de/manual/webcam/1sec.jpg')
		download(r, 'raw/%s/img%06d.jpg' % (today, countL))
		print('%s Saved' % countL)
		countL += 1
	else:
		print('next day')
		ffmpeg_run(ff_exec, 'raw/' + today_temp + '/img%06d.jpg', '-framerate 15', 'raw/%s.mp4' % (today_temp), '-c:v libx264 -pix_fmt yuv420p')
		os._exit(0)
	return

# main()
today_temp = str(date.today())
countW = 0
countL = 0
if (args.source == 0):
	if (args.debug == 0):
		print('STAGE 0 | Rip stream (wetter.com)')
		s = BlockingScheduler() #init scheduler
		s.add_job(downloadStreamW, 'interval', [today_temp], minutes=20)
		s.start()
	elif (args.debug == 1):
		print('STAGE 1 | Add fade in/out effect')
		ffmpeg_fade_merge(today_temp)
	elif (args.debug == 2):
		print('STAGE 2 | Merge files')
		ffmpeg_run(ff_exec, 'raw/%s/out/list.txt' % (folder), '-f concat -safe 0', 'raw/%s.mp4' % (folder), '-c copy')
		os._exit(0)
elif (args.source == 1):
	if (args.debug == 0):
		print('STAGE 0 | Rip stream (ludwigbeck.de)')
		s = BlockingScheduler() #init scheduler
		s.add_job(downloadStreamL, 'interval', [today_temp], seconds=5)
		s.start()
	elif (args.debug == 1):
		print('STAGE 1 | Merge .jpg files')
		ffmpeg_run(ff_exec, 'raw/' + today_temp + '/img%06d.jpg', '-framerate 15', 'raw/%s.mp4' % (today_temp), '-c:v libx264 -pix_fmt yuv420p')
		os._exit(0)