def eyelinkChildFunction(
qTo
, qFrom
, windowSize = [200,200]
, windowPosition = [0,0]
, calibrationDisplayRes = [1920,1080]
, calibrationDisplayPosition = [1920,0]
, calibrationDotSize = 10
, eyelinkIP = '100.1.1.1'
, edfFileName = 'temp.edf'
, edfPath = './_Data/temp.edf'
, saccadeSoundFile = '_Stimuli/stop.wav'
, blinkSoundFile = '_Stimuli/stop.wav'
):
	import sdl2
	import sdl2.ext
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
	eyelink.sendCommand("screen_pixel_coords =  0 0 %d %d" %(calibrationDisplayRes[0],calibrationDisplayRes[1]))
	eyelink.sendMessage("DISPLAY_COORDS  0 0 %d %d" %(calibrationDisplayRes[0],calibrationDisplayRes[1]))
	eyelink.sendCommand("saccade_velocity_threshold = 60")
	eyelink.sendCommand("saccade_acceleration_threshold = 19500")

	class EyeLinkCoreGraphicsPySDL2(pylink.EyeLinkCustomDisplay):
		def __init__(self,targetSize,windowSize,windowPosition):
			self.targetSize = targetSize
			self.windowPosition = windowPosition
			self.windowSize = windowSize
			self.__target_beep__ = Sound('_Stimuli/type.wav')
			self.__target_beep__done__ = Sound('qbeep.wav')
			self.__target_beep__error__ = Sound('error.wav')
		def play_beep(self,beepid):
			if beepid == pylink.DC_TARG_BEEP or beepid == pylink.CAL_TARG_BEEP:
				self.__target_beep__.play()
			elif beepid == pylink.CAL_ERR_BEEP or beepid == pylink.DC_ERR_BEEP:
				self.__target_beep__error__.play()
			else:#	CAL_GOOD_BEEP or DC_GOOD_BEEP
				self.__target_beep__done__.play()
		def clear_cal_display(self): 
			sdl2.ext.fill(self.windowSurf.contents,sdl2.pixels.SDL_Color(r=0, g=0, b=0, a=255))
			self.window.refresh()
			sdl2.ext.fill(self.windowSurf.contents,sdl2.pixels.SDL_Color(r=0, g=0, b=0, a=255))
		def setup_cal_display(self):
			self.window = sdl2.ext.Window("Calibration",size=self.windowSize,position=self.windowPosition,flags=sdl2.SDL_WINDOW_SHOWN)#|sdl2.SDL_WINDOW_BORDERLESS)
			self.windowID = sdl2.SDL_GetWindowID(self.window.window)
			self.windowSurf = sdl2.SDL_GetWindowSurface(self.window.window)
			self.windowArray = sdl2.ext.pixels3d(self.windowSurf.contents)
			for i in range(10):
				sdl2.SDL_PumpEvents() #to show the windows
			self.clear_cal_display()
		def exit_cal_display(self): 
			sdl2.SDL_DestroyWindow(self.window.window)
		def erase_cal_target(self):
			self.clear_cal_display()
		def draw_cal_target(self, x, y):
			radius = self.targetSize/2
			yy, xx = numpy.ogrid[-radius: radius, -radius: radius]
			index = numpy.logical_and( (xx**2 + yy**2) <= (radius**2) , (xx**2 + yy**2) >= ((radius/4)**2) )
			self.windowArray[ (x-radius):(x+radius) , (y-radius):(y+radius) ,  ][index] = [155,155,155,255]
			self.window.refresh()
		def get_input_key(self):
			sdl2.SDL_PumpEvents()
			return None

	def checkGaze(gaze,newGazeTarget):
		distFromFixation = numpy.linalg.norm(numpy.array(gaze)-gazeTarget)
		if newGazeTarget:
			if distFromFixation<gazeTargetCriterion:
				#print ['gazeTargetMet',gaze,gazeTarget,distFromFixation,gazeTargetCriterion]
				qFrom.put(['gazeTargetMet',gazeTarget])
				newGazeTarget = False
			else:
				qFrom.put(['gazeTargetNotMet',gazeTarget])
				#print ['gazeTargetNotMet',gaze,gazeTarget,distFromFixation,gazeTargetCriterion]
		else:
			if distFromFixation>gazeTargetCriterion:
				#print ['gazeTargetLost',gaze,gazeTarget,distFromFixation,gazeTargetCriterion]
				if reportSaccades:
					qFrom.put(['gazeTargetLost',gazeTarget])
				if (not saccadeSound.stillPlaying()) and (not blinkSound.stillPlaying()):
					if doSounds:
						saccadeSound.play()
		return newGazeTarget

	customDisplay = EyeLinkCoreGraphicsPySDL2(targetSize=calibrationDotSize,windowSize=calibrationDisplayRes,windowPosition=calibrationDisplayPosition)
	pylink.openGraphicsEx(customDisplay)
	eyeUsed = eyelink.eyeAvailable()
	newGazeTarget = False
	gazeTarget = numpy.array(calibrationDisplayRes)/2.0
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
			if (eyeData==pylink.SAMPLE_TYPE) or (eyeData==pylink.ENDSACC):
				if eyeData==pylink.SAMPLE_TYPE:
					if eyeUsed == 1 and eyeData.isRightSample():
						gaze = eyeData.getRightEye().getGaze()
						newGazeTarget = checkGaze(gaze,newGazeTarget)
					elif eyeUsed == 0 and eyeData.isLeftSample():
						gaze = eyeData.getLeftEye().getGaze()
						newGazeTarget = checkGaze(gaze,newGazeTarget)
				else: #eyeData==pylink.ENDSACC
					eyeEvent = eyelink.getFloatData()
					gaze = eyeEvent.getEndGaze()
					newGazeTarget = checkGaze(gaze,newGazeTarget)
			elif eyeData==pylink.STARTBLINK:
				if reportBlinks:
					qFrom.put('blink')
				#print 'blink'
				if (not saccadeSound.stillPlaying()) and (not blinkSound.stillPlaying()):
					if doSounds:
						#blinkSound.play()
						qFrom.put('blink')

eyelinkChildFunction(qTo,qFrom,**initDict)