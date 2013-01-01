def eyelinkChildFunction(
qTo
, qFrom
, windowSize = [200,200]
, windowPosition = [0,0]
, stimDisplayRes = [1920,1080]
, stimDisplayPosition = [1920,0]
, calibrationDisplaySize = [1920,1080]
, calibrationDotSize = 10
, eyelinkIP = '100.1.1.1'
, edfFileName = 'temp.edf'
, edfPath = './_Data/temp.edf'
, saccadeSoundFile = '_Stimuli/stop.wav'
, blinkSoundFile = '_Stimuli/stop.wav'
):
	import sdl2
	import sdl2.ext
	import math
	import OpenGL.GL as gl
	import sdl2.sdlmixer
	import pylink
	import numpy
	import sys
	import shutil
	import subprocess
	import time
	import os
	try:
		import appnope
		appnope.nope()
	except:
		pass

	byteify = lambda x, enc: x.encode(enc)

	sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
	window = sdl2.ext.Window("eyelink",size=windowSize,position=windowPosition,flags=sdl2.SDL_WINDOW_SHOWN)
	windowID = sdl2.SDL_GetWindowID(window.window)
	windowSurf = sdl2.SDL_GetWindowSurface(window.window)
	sdl2.ext.fill(windowSurf.contents,sdl2.pixels.SDL_Color(r=0, g=0, b=0, a=255))
	window.refresh()

	for i in range(10):
		sdl2.SDL_PumpEvents() #to show the windows


	sdl2.SDL_Init(sdl2.SDL_INIT_AUDIO)
	sdl2.sdlmixer.Mix_OpenAudio(44100, sdl2.sdlmixer.MIX_DEFAULT_FORMAT, 2, 1024)
	class Sound:
		def __init__(self, fileName):
			self.sample = sdl2.sdlmixer.Mix_LoadWAV(sdl2.ext.compat.byteify(fileName, "utf-8"))
			self.started = False
		def play(self):
			self.channel = sdl2.sdlmixer.Mix_PlayChannel(-1, self.sample, 0)
			self.started = True
		def stillPlaying(self):
			if self.started:
				if sdl2.sdlmixer.Mix_Playing(self.channel):
					return True
				else:
					self.started = False
					return False
			else:
				return False

	saccadeSound = Sound(saccadeSoundFile)
	blinkSound = Sound(blinkSoundFile)

	def exitSafely():
		if 'eyelink' in locals():
			if eyelink.isRecording():
				eyelink.stopRecording()
			eyelink.setOfflineMode()
			eyelink.closeDataFile()
			eyelink.receiveDataFile('temp.edf','temp.edf')
			eyelink.close()
			if os.path.isfile('temp.edf'):
				shutil.move('temp.edf', edfPath)
				if os.path.isfile(edfPath):
					subprocess.call('./edf2asc -y ./'+edfPath,shell=True)
		sys.exit()


	edfPath = './_Data/temp.edf' #temporary default location, to be changed later when ID is established
	eyelink = pylink.EyeLink(eyelinkIP)
	eyelink.sendCommand('select_parser_configuration 0')# 0--> standard (cognitive); 1--> sensitive (psychophysical)
	eyelink.sendCommand('sample_rate 250')
	eyelink.setLinkEventFilter("SACCADE,BLINK,LEFT,RIGHT")
	eyelink.openDataFile(edfFileName)
	eyelink.sendCommand("screen_pixel_coords =  %d %d %d %d" %(stimDisplayRes[0]/2 - calibrationDisplaySize[0]/2 , stimDisplayRes[1]/2 - calibrationDisplaySize[1]/2 , stimDisplayRes[0]/2 + calibrationDisplaySize[0]/2 , stimDisplayRes[1]/2 + calibrationDisplaySize[1]/2 ))
	eyelink.sendMessage("DISPLAY_COORDS  0 0 %d %d" %(stimDisplayRes[0],stimDisplayRes[1]))
	eyelink.sendCommand("saccade_velocity_threshold = 60")
	eyelink.sendCommand("saccade_acceleration_threshold = 19500")

	class EyeLinkCoreGraphicsPySDL2(pylink.EyeLinkCustomDisplay):
		def __init__(self):
			self.__target_beep__ = Sound('_Stimuli/type.wav')
			self.__target_beep__done__ = Sound('qbeep.wav')
			self.__target_beep__error__ = Sound('error.wav')
			if sys.byteorder == 'little':
				self.byteorder = 1
			else:
				self.byteorder = 0
			self.imagebuffer = array.array('L')
			self.pal = None
			self.__img__ = None
		def record_abort_hide(self):
			pass
		def play_beep(self,beepid):
			if beepid == pylink.DC_TARG_BEEP or beepid == pylink.CAL_TARG_BEEP:
				self.__target_beep__.play()
			elif beepid == pylink.CAL_ERR_BEEP or beepid == pylink.DC_ERR_BEEP:
				self.__target_beep__error__.play()
			else:#	CAL_GOOD_BEEP or DC_GOOD_BEEP
				self.__target_beep__done__.play()
		def clear_cal_display(self):
			qFrom.put('clear_cal_display')
			# print 'clear_cal_display'
		def setup_cal_display(self):
			qFrom.put('setup_cal_display')
			# print 'setup_cal_display'
		def exit_cal_display(self): 
			qFrom.put('exit_cal_display')
			# print 'exit_cal_display'
		def erase_cal_target(self):
			qFrom.put('erase_cal_target')
			# print 'erase_cal_target'
		def draw_cal_target(self, x, y):
			qFrom.put(['draw_cal_target',x,y])
			# print 'draw_cal_target'
		def setup_image_display(self, width, height):
			print 'eyelink: setup_image_display'
			self.img_size = (width,height)
		def exit_image_display(self):
			pass
		def image_title(self,text):
			pass
		def set_image_palette(self, r,g,b):
			self.imagebuffer = array.array('L')
			sz = len(r)
			i = 0
			self.pal = []
			while i < sz:
				rf = int(b[i])
				gf = int(g[i])
				bf = int(r[i])
				if self.byteorder:
					self.pal.append((rf<<16) | (gf<<8) | (bf))
				else:
					self.pal.append((bf<<24) |  (gf<<16) | (rf<<8)) #for mac
				i = i+1
		def draw_image_line(self, width, line, totlines,buff):
			i = 0
			while i < width:
				if buff[i] > len(self.pal):
					buff[i] = len(self.pal) - 1
				self.imagebuffer.append(self.pal[buff[i]&0x000000FF])
				i += 1
			if line == totlines:
				img = Image.new('RGBX',self.img_size)
				img.fromstring(self.imagebuffer.tostring())
				self.__img__ = img
				self.draw_cross_hair() #inherited method!
				self.__img__ = None
				qFrom.put(['image',img])
				self.imagebuffer = array.array('l')
		def getColorFromIndex(self,colorindex):
			if colorindex   ==  pylink.CR_HAIR_COLOR:          return (255,255,255,255)
			elif colorindex ==  pylink.PUPIL_HAIR_COLOR:       return (255,255,255,255)
			elif colorindex ==  pylink.PUPIL_BOX_COLOR:        return (0,255,0,255)
			elif colorindex ==  pylink.SEARCH_LIMIT_BOX_COLOR: return (255,0,0,255)
			elif colorindex ==  pylink.MOUSE_CURSOR_COLOR:     return (255,0,0,255)
			else: return (0,0,0,0)
		def draw_line(self,x1,y1,x2,y2,colorindex):
			imr = self.__img__.size
			x1 = int((float(x1)/float(self.img_size[0]))*imr[0])
			x2 = int((float(x2)/float(self.img_size[0]))*imr[0])
			y1 = int((float(y1)/float(self.img_size[1]))*imr[1])
			y2 = int((float(y2)/float(self.img_size[1]))*imr[1])
			color = self.getColorFromIndex(colorindex)
			qFrom.put(['line',x1,y1,x2,y2, color])
		def draw_lozenge(self,x,y,width,height,colorindex):
			color = self.getColorFromIndex(colorindex)
			imr = self.__img__.size
			x=int((float(x)/float(self.img_size[0]))*imr[0])
			width=int((float(width)/float(self.img_size[0]))*imr[0])
			y=int((float(y)/float(self.img_size[1]))*imr[1])
			height=int((float(height)/float(self.img_size[1]))*imr[1])
			qFrom.put(['losenge',x,y,width,height,color])
		def get_mouse_state(self):
			pos = pygame.mouse.get_pos()
			state = pygame.mouse.get_pressed()
			return (pos,state[0])
		def get_input_key(self):
			ky=[]
			while not qTo.empty():
				message = qTo.get()
				if message=='quit':
					exitSafely()
				elif message[0]=='keycode':
					key = message[1]
					if key == 'f1':           keycode = pylink.F1_KEY
					elif key == 'f2':         keycode = pylink.F2_KEY
					elif key == 'f3':         keycode = pylink.F3_KEY
					elif key == 'f4':         keycode = pylink.F4_KEY
					elif key == 'f5':         keycode = pylink.F5_KEY
					elif key == 'f6':         keycode = pylink.F6_KEY
					elif key == 'f7':         keycode = pylink.F7_KEY
					elif key == 'f8':         keycode = pylink.F8_KEY
					elif key == 'f9':         keycode = pylink.F9_KEY
					elif key == 'f10':        keycode = pylink.F10_KEY
					elif key == 'pageup':     keycode = pylink.PAGE_UP
					elif key == 'pagedown':   keycode = pylink.PAGE_DOWN
					elif key == 'up':         keycode = pylink.CURS_UP
					elif key == 'down':       keycode = pylink.CURS_DOWN
					elif key == 'left':       keycode = pylink.CURS_LEFT
					elif key == 'right':      keycode = pylink.CURS_RIGHT
					elif key == 'backspace':  keycode = ord('\b')
					elif key == 'return':     keycode = pylink.ENTER_KEY
					elif key == 'escape':     keycode = pylink.ESC_KEY
					elif key == 'tab':        keycode = ord('\t')
					else:                     keycode = 0
					ky.append(pylink.KeyInput(keycode))
			return ky

	customDisplay = EyeLinkCoreGraphicsPySDL2()
	pylink.openGraphicsEx(customDisplay)
	eyeUsed = eyelink.eyeAvailable()
	newGazeTarget = False
	gazeTarget = numpy.array(calibrationDisplaySize)/2.0
	gazeTargetCriterion = calibrationDotSize
	doSounds = False
	reportSaccades = False
	reportBlinks = False
	lastMessageTime = time.time()
	while True:
		sdl2.SDL_PumpEvents()
		for event in sdl2.ext.get_events():
			if event.type==sdl2.SDL_WINDOWEVENT:
				if (event.window.event==sdl2.SDL_WINDOWEVENT_CLOSE):
					exitSafely()
		if not qTo.empty():
			message = qTo.get()
			if message=='quit':
				exitSafely()
			elif message[0]=='edfPath':
				edfPath = message[1]
			elif message[0]=='doSounds':
				doSounds = message[1]
			elif message[0]=='reportSaccades':
				reportSaccades = message[1]
			elif message[0]=='reportBlinks':
				reportBlinks = message[1]
			elif message[0]=='sendMessage':
				eyelink.sendMessage(message[1])
			elif message[0]=='newGazeTarget':
				# print message
				newGazeTarget = True
				gazeTarget = numpy.array(message[1])
				gazeTargetCriterion = numpy.array(message[2])
				#print message
				#print 'waiting for gaze confirmation'
			elif message[0]=='accept_trigger':
				eyelink.accept_trigger()
			elif message=='doCalibration':
				doSounds = False
				if eyelink.isRecording():
					eyelink.stopRecording()
				eyelink.doTrackerSetup()
				qFrom.put('calibrationComplete')
				eyelink.startRecording(1,1,1,1) #this retuns immediately takes 10-30ms to actually kick in on the tracker
		if eyelink.isRecording()==0:
			eyeData = eyelink.getNextData()
			if eyeData==pylink.SAMPLE_TYPE:
				eyeSample = eyelink.getFloatData()
				if eyeSample.isRightSample():
					gaze = eyeSample.getRightEye().getGaze()
				elif eyeSample.isLeftSample():
					gaze = eyeSample.getLeftEye().getGaze()
				distFromFixation = numpy.linalg.norm(numpy.array(gaze)-gazeTarget)
				if newGazeTarget:
					if distFromFixation<gazeTargetCriterion:
						# print ['gazeTargetMet',gaze,gazeTarget,distFromFixation,gazeTargetCriterion]
						qFrom.put(['gazeTargetMet',gazeTarget])
						newGazeTarget = False
					else:
						qFrom.put(['gazeTargetNotMet',gazeTarget])
						# print ['gazeTargetNotMet',gaze,gazeTarget,distFromFixation,gazeTargetCriterion]
				else:
					if distFromFixation>gazeTargetCriterion:
						# print ['gazeTargetLost',gaze,gazeTarget,distFromFixation,gazeTargetCriterion]
						if reportSaccades:
							qFrom.put(['gazeTargetLost',gazeTarget])
						if (not saccadeSound.stillPlaying()) and (not blinkSound.stillPlaying()):
							if doSounds:
								saccadeSound.play()
			elif eyeData==pylink.STARTBLINK:
				if reportBlinks:
					qFrom.put('blink')
				# print 'blink'
				if (not saccadeSound.stillPlaying()) and (not blinkSound.stillPlaying()):
					if doSounds:
						#blinkSound.play()
						qFrom.put('blink')

eyelinkChildFunction(qTo,qFrom,**initDict)