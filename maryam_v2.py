if __name__ == '__main__':
	########
	#Important parameters
	########

	viewingDistance = 58.0 #units can be anything so long as they match those used in stimDisplayWidth below
	stimDisplayWidth = 51.6 #units can be anything so long as they match those used in viewingDistance above
	stimDisplayRes = (1920,1200) #pixel resolution of the stimDisplay
	stimDisplayPosition = (1024,0)

	writerWindowSize = (200,200)
	writerWindowPosition = (200,0)

	stamperWindowSize = (200,200)
	stamperWindowPosition = (0,0)
	stamperWindowColor = [255,255,255]
	stamperDoBorder = True

	photoStimSize = [20,20]
	photoStimPosition = [1920-photoStimSize[0]/2,1200-photoStimSize[1]/2]

	doEyelink = True
	eyelinkWindowSize = (200,200)
	eyelinkWindowPosition = (400,0)
	eyelinkIP = '100.1.1.1'
	edfFileName = 'temp2.edf'
	edfPath = './'
	saccadeSoundFile = '_Stimuli/stop.wav'
	blinkSoundFile = '_Stimuli/stop.wav'
	calibrationDotSizeInDegrees = .5
	gazeTargetCriterionInDegrees = 1

	hiSoundFile = './_Stimuli/hi.wav'
	loSoundFile = './_Stimuli/lo.wav'
	t1ResponseKeys = ['z','a']
	t2ResponseKeys = [',','.']

	ttoaList = [0.200,0.400,0.800] 
	cueLocationList = ['left','right','center']
	t1IdentityList = ['hi','lo','NA'] #NA means no T1 (for cuing-only trials)
	t2LocationList = ['left','right']

	fixationDuration = .500
	cueTargetOA = 1.200
	cueDuration = 0.050
	cueCuebackOA = 0.200
	cuebackDuration = 0.050
	responseTimeout = 1.500
	feedbackDuration = .500

	numberOfBlocks = [4,5]
	repsPerT1Practice = 3
	repsPerT2Practice = 3

	instructionSizeInDegrees = .5 #specify the size of the instruction text
	feedbackSizeInDegrees = .5 #specify the size of the feedback text
	fixationRadiusInDegrees = .1
	targetRadiusInDegrees = .5 #specify the width of the target
	targetOffsetInDegrees = 6 #specify the distance of the target to center
	placeholderRadiusInDegrees = 1
	placeholderThicknessProportion = .8

	textWidth = .9 #proportion of the stimDisplay to use when drawing instructions


	########
	# Import libraries
	########
	import sdl2 #for input and display
	import sdl2.sdlmixer
	import numpy #for image and display manipulation
	import scipy.misc #for resizing numpy images via scipy.misc.imresize
	from PIL import Image #for image manipulation
	from PIL import ImageFont
	from PIL import ImageOps
	#import aggdraw #for drawing
	import math #for rounding
	import sys #for quitting
	import os
	import random #for shuffling and random sampling
	import time #for timing
	import shutil #for copying files
	import hashlib #for encrypting
	import OpenGL.GL as gl
	try:
		os.nice(-20)
	except:
		pass#print('Can\'t nice')
	try:
		import appnope
		appnope.nope()
	except:
		pass
	import fileForker
	byteify = lambda x, enc: x.encode(enc)

	########
	# Initialize audio and define a class for playing sounds
	########
	sdl2.SDL_Init(sdl2.SDL_INIT_AUDIO)
	sdl2.sdlmixer.Mix_OpenAudio(44100, sdl2.sdlmixer.MIX_DEFAULT_FORMAT, 2, 1024)
	class Sound:
		def __init__(self, fileName):
			self.sample = sdl2.sdlmixer.Mix_LoadWAV(byteify(fileName, "utf-8"))
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

	hiSound = Sound(hiSoundFile)
	loSound = Sound(loSoundFile)

	########
	# Define a custom time function using the same clock as that which generates the SDL2 event timestamps
	########

	#define a function that gets the time (unit=seconds,zero=?)
	def getTime():
		return sdl2.SDL_GetPerformanceCounter()*1.0/sdl2.SDL_GetPerformanceFrequency()


	########
	# Initialize the timer and random seed
	########
	sdl2.SDL_Init(sdl2.SDL_INIT_TIMER)
	seed = getTime() #grab the time of the timer initialization to use as a seed
	random.seed(seed) #use the time to set the random seed


	########
	#Perform some calculations to convert stimulus measurements in degrees to pixels
	########
	stimDisplayWidthInDegrees = math.degrees(math.atan((stimDisplayWidth/2.0)/viewingDistance)*2)
	PPD = stimDisplayRes[0]/stimDisplayWidthInDegrees #compute the pixels per degree (PPD)

	calibrationDotSize = calibrationDotSizeInDegrees*PPD
	instructionSize = instructionSizeInDegrees*PPD
	feedbackSize = feedbackSizeInDegrees*PPD
	fixationRadius = fixationRadiusInDegrees*PPD
	targetRadius = targetRadiusInDegrees*PPD
	targetOffset = targetOffsetInDegrees*PPD
	placeholderRadius = placeholderRadiusInDegrees*PPD
	placeholderThickness = placeholderRadiusInDegrees*PPD*placeholderThicknessProportion
	gazeTargetCriterion = gazeTargetCriterionInDegrees*PPD

	########
	# Initialize fonts
	########
	feedbackFontSize = 2
	feedbackFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", feedbackFontSize)
	feedbackHeight = feedbackFont.getsize('XXX')[1]
	while feedbackHeight<feedbackSize:
		feedbackFontSize = feedbackFontSize + 1
		feedbackFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", feedbackFontSize)
		feedbackHeight = feedbackFont.getsize('XXX')[1]

	feedbackFontSize = feedbackFontSize - 1
	feedbackFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", feedbackFontSize)
	feedbackHeight = feedbackFont.getsize('XXX')[1]

	instructionFontSize = 2
	instructionFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", instructionFontSize)
	instructionHeight = instructionFont.getsize('XXX')[1]
	while instructionHeight<instructionSize:
		instructionFontSize = instructionFontSize + 1
		instructionFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", instructionFontSize)
		instructionHeight = instructionFont.getsize('XXX')[1]

	instructionFontSize = instructionFontSize - 1
	instructionFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", instructionFontSize)
	instructionHeight = instructionFont.getsize('XXX')[1]

	########
	# initialize the eyelink
	########
	if doEyelink:
		eyelinkChild = fileForker.childClass(childFile='eyelinkChild.py')
		eyelinkChild.initDict['windowSize'] = eyelinkWindowSize
		eyelinkChild.initDict['windowPosition'] = eyelinkWindowPosition
		eyelinkChild.initDict['stimDisplayPosition'] = stimDisplayPosition
		eyelinkChild.initDict['stimDisplayRes'] = stimDisplayRes
		eyelinkChild.initDict['calibrationDisplaySize'] = stimDisplayRes#[int(targetOffset*2),int(targetOffset)]
		eyelinkChild.initDict['calibrationDotSize'] = int(calibrationDotSize)
		eyelinkChild.initDict['eyelinkIP'] = eyelinkIP
		eyelinkChild.initDict['edfFileName'] = edfFileName
		eyelinkChild.initDict['edfPath'] = edfPath
		eyelinkChild.initDict['saccadeSoundFile'] = saccadeSoundFile
		eyelinkChild.initDict['blinkSoundFile'] = blinkSoundFile
		eyelinkChild.start()


	########
	# Initialize the writer
	########
	writerChild = fileForker.childClass(childFile='writerChild.py')
	writerChild.initDict['windowSize'] = writerWindowSize
	writerChild.initDict['windowPosition'] = writerWindowPosition
	time.sleep(1) #give the other windows some time to initialize
	writerChild.start()

	# ########
	# # Initialize the stimDisplayMirrorChild
	# ########
	# stimDisplayMirrorChild = fileForker.childClass(childFile='stimDisplayMirrorChild.py')
	# stimDisplayMirrorChild.initDict['windowSize'] = [1920/2,1200/2]#[stimDisplayRes[0]/2,stimDisplayRes[1]/2]
	# stimDisplayMirrorChild.initDict['windowPosition'] = [0,0]
	# time.sleep(1) #give the other windows some time to initialize
	# stimDisplayMirrorChild.start()

	########
	# Initialize the stimDisplay
	########
	class stimDisplayClass:
		def __init__(self,stimDisplayRes,stimDisplayPosition):#,stimDisplayMirrorChild):
			self.stimDisplayRes = stimDisplayRes
			# self.stimDisplayMirrorChild = stimDisplayMirrorChild
			sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
			self.stimDisplayRes = stimDisplayRes
			self.stimDisplayPosition = stimDisplayPosition
			self.Window = sdl2.video.SDL_CreateWindow(byteify('stimDisplay', "utf-8"),self.stimDisplayPosition[0],self.stimDisplayPosition[1],self.stimDisplayRes[0],self.stimDisplayRes[1],sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP | sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC)
			self.glContext = sdl2.SDL_GL_CreateContext(self.Window)
			gl.glMatrixMode(gl.GL_PROJECTION)
			gl.glLoadIdentity()
			gl.glOrtho(0, stimDisplayRes[0],stimDisplayRes[1], 0, 0, 1)
			gl.glMatrixMode(gl.GL_MODELVIEW)
			gl.glDisable(gl.GL_DEPTH_TEST)
			gl.glReadBuffer(gl.GL_FRONT)
			start = time.time()
			while time.time()<(start+2):
				sdl2.SDL_PumpEvents()
			self.refresh()
			self.refresh()
		def refresh(self,clearColor=[0,0,0,1]):
			sdl2.SDL_GL_SwapWindow(self.Window)
			# self.stimDisplayMirrorChild.qTo.put(['frame',self.stimDisplayRes,gl.glReadPixels(0, 0, self.stimDisplayRes[0], self.stimDisplayRes[1], gl.GL_BGR, gl.GL_UNSIGNED_BYTE)])
			gl.glClearColor(clearColor[0],clearColor[1],clearColor[2],clearColor[3])
			gl.glClear(gl.GL_COLOR_BUFFER_BIT)


	time.sleep(1)
	stimDisplay = stimDisplayClass(stimDisplayRes=stimDisplayRes,stimDisplayPosition=stimDisplayPosition)#,stimDisplayMirrorChild=stimDisplayMirrorChild)


	########
	# start the event timestamper
	########
	stamperChild = fileForker.childClass(childFile='stamperChild.py')
	stamperChild.initDict['windowSize'] = stamperWindowSize
	stamperChild.initDict['windowPosition'] = stamperWindowPosition
	stamperChild.initDict['windowColor'] = stamperWindowColor
	stamperChild.initDict['doBorder'] = stamperDoBorder
	stamperChild.start()


	########
	# Drawing functions
	########

	def text2numpy(myText,myFont,fg=[255,255,255,255],bg=[0,0,0,0]):
		glyph = myFont.getmask(myText,mode='L')
		a = numpy.asarray(glyph)#,dtype=numpy.uint8)
		b = numpy.reshape(a,(glyph.size[1],glyph.size[0]),order='C')
		c = numpy.zeros((glyph.size[1],glyph.size[0],4))#,dtype=numpy.uint8)
		# c[:,:,0][b>0] = b[b>0]
		# c[:,:,1][b>0] = b[b>0]
		# c[:,:,2][b>0] = b[b>0]
		# c[:,:,3][b>0] = b[b>0]
		c[:,:,0][b>0] = fg[0]*b[b>0]/255.0
		c[:,:,1][b>0] = fg[1]*b[b>0]/255.0
		c[:,:,2][b>0] = fg[2]*b[b>0]/255.0
		c[:,:,3][b>0] = fg[3]*b[b>0]/255.0
		c[:,:,0][b==0] = bg[0]
		c[:,:,1][b==0] = bg[1]
		c[:,:,2][b==0] = bg[2]
		c[:,:,3][b==0] = bg[3]
		return c.astype(dtype=numpy.uint8)


	def blitNumpy(numpyArray,xLoc,yLoc,xCentered=True,yCentered=True):
		gl.glEnable(gl.GL_BLEND)
		gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
		ID = gl.glGenTextures(1)
		gl.glBindTexture(gl.GL_TEXTURE_2D, ID)
		gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_REPLACE);
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
		gl.glTexImage2D( gl.GL_TEXTURE_2D , 0 , gl.GL_RGBA , numpyArray.shape[1] , numpyArray.shape[0] , 0 , gl.GL_RGBA , gl.GL_UNSIGNED_BYTE , numpyArray )
		gl.glEnable(gl.GL_TEXTURE_2D)
		gl.glBindTexture(gl.GL_TEXTURE_2D, ID)
		gl.glBegin(gl.GL_QUADS)
		x1 = xLoc + 1.5 - 0.5
		x2 = xLoc + numpyArray.shape[1] - 0.0 + 0.5
		y1 = yLoc + 1.0 - 0.5
		y2 = yLoc + numpyArray.shape[0] - 0.5 + 0.5
		if xCentered:
			x1 = x1 - numpyArray.shape[1]/2.0
			x2 = x2 - numpyArray.shape[1]/2.0
		if yCentered:
			y1 = y1 - numpyArray.shape[0]/2.0
			y2 = y2 - numpyArray.shape[0]/2.0
		gl.glTexCoord2f( 0 , 0 )
		gl.glVertex2f( x1 , y1 )
		gl.glTexCoord2f( 1 , 0 )
		gl.glVertex2f( x2 , y1 )
		gl.glTexCoord2f( 1 , 1)
		gl.glVertex2f( x2 , y2 )
		gl.glTexCoord2f( 0 , 1 )
		gl.glVertex2f( x1, y2 )
		gl.glEnd()
		gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
		gl.glDeleteTextures([ID])
		del ID
		gl.glDisable(gl.GL_TEXTURE_2D)
		return None


	def drawText( myText , myFont , textWidth , xLoc , yLoc , fg=[255,255,255,255] , bg=[0,0,0,0] , xCentered=True , yCentered=True , lineSpacing=1.2):
		lineHeight = myFont.getsize('Tj')[0]*lineSpacing
		paragraphs = myText.splitlines()
		renderList = []
		for thisParagraph in paragraphs:
			words = thisParagraph.split(' ')
			if len(words)==1:
				renderList.append(words[0])
				if (thisParagraph!=paragraphs[len(paragraphs)-1]):
					renderList.append(' ')
			else:
				thisWordIndex = 0
				while thisWordIndex < (len(words)-1):
					lineStart = thisWordIndex
					lineWidth = 0
					while (thisWordIndex < (len(words)-1)) and (lineWidth <= textWidth):
						thisWordIndex = thisWordIndex + 1
						lineWidth = myFont.getsize(' '.join(words[lineStart:(thisWordIndex+1)]))[0]
					if thisWordIndex < (len(words)-1):
						#last word went over, paragraph continues
						renderList.append(' '.join(words[lineStart:(thisWordIndex-1)]))
						thisWordIndex = thisWordIndex-1
					else:
						if lineWidth <= textWidth:
							#short final line
							renderList.append(' '.join(words[lineStart:(thisWordIndex+1)]))
						else:
							#full line then 1 word final line
							renderList.append(' '.join(words[lineStart:thisWordIndex]))
							renderList.append(words[thisWordIndex])
						#at end of paragraph, check whether a inter-paragraph space should be added
						if (thisParagraph!=paragraphs[len(paragraphs)-1]):
							renderList.append(' ')
		numLines = len(renderList)
		for thisLineNum in range(numLines):
			if renderList[thisLineNum]==' ':
				pass
			else:
				thisRender = text2numpy( renderList[thisLineNum] , myFont , fg=fg , bg=bg )
				if xCentered:
					x = xLoc - thisRender.shape[1]/2.0
				else:
					x = xLoc
				if yCentered:
					y = yLoc - numLines*lineHeight/2.0 + thisLineNum*lineHeight
				else:
					y = yLoc + thisLineNum*lineHeight
				blitNumpy(numpyArray=thisRender,xLoc=x,yLoc=y,xCentered=False,yCentered=False)
		return None


	def drawFeedback(feedbackText):
		if type(feedbackText)==type('a'):
			feedbackArray = text2numpy(feedbackText,feedbackFont,fg=[255,0,0,255],bg=[0,0,0,0])
			blitNumpy(feedbackArray,stimDisplayRes[0]/2,stimDisplayRes[1]/2,xCentered=True,yCentered=True)
		else:
			feedbackArray = text2numpy(feedbackText[0],feedbackFont,fg=[127,127,127,255],bg=[0,0,0,0])
			blitNumpy(feedbackArray,stimDisplayRes[0]/2,stimDisplayRes[1]/2-feedbackHeight,xCentered=True,yCentered=True)
			feedbackArray = text2numpy(feedbackText[1],feedbackFont,fg=[127,127,127,255],bg=[0,0,0,0])
			blitNumpy(feedbackArray,stimDisplayRes[0]/2,stimDisplayRes[1]/2+feedbackHeight,xCentered=True,yCentered=True)


	def drawDot(size,xOffset=0):
		gl.glColor3f(.5,.5,.5)
		gl.glBegin(gl.GL_POLYGON)
		for i in range(360):
			gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin(i*math.pi/180)*size , stimDisplayRes[1]/2 + math.cos(i*math.pi/180)*size)
		gl.glEnd()


	def drawRing(xOffset=0,color=.5):
		outer = placeholderRadius
		inner = placeholderThickness
		gl.glColor3f(color,color,color)
		gl.glBegin(gl.GL_QUAD_STRIP)
		for i in range(361):
			gl.glVertex2f(stimDisplayRes[0]/2+xOffset + math.sin(i*math.pi/180)*outer,stimDisplayRes[1]/2 + math.cos(i*math.pi/180)*outer)
			gl.glVertex2f(stimDisplayRes[0]/2+xOffset + math.sin(i*math.pi/180)*inner,stimDisplayRes[1]/2 + math.cos(i*math.pi/180)*inner)
		gl.glEnd()

	
	def drawPhotoStim():
		pass
		# gl.glColor3f(1,1,1)
		# gl.glBegin(gl.GL_QUAD_STRIP)
		# gl.glVertex2f( photoStimPosition[0] - photoStimSize[0]/2 , photoStimPosition[1] - photoStimSize[1]/2 )
		# gl.glVertex2f( photoStimPosition[0] - photoStimSize[0]/2 , photoStimPosition[1] + photoStimSize[1]/2 )
		# gl.glVertex2f( photoStimPosition[0] + photoStimSize[0]/2 , photoStimPosition[1] + photoStimSize[1]/2 )
		# gl.glVertex2f( photoStimPosition[0] + photoStimSize[0]/2 , photoStimPosition[1] - photoStimSize[1]/2 )
		# gl.glVertex2f( photoStimPosition[0] - photoStimSize[0]/2 , photoStimPosition[1] - photoStimSize[1]/2 )
		# gl.glEnd()
		# gl.glColor3f(0,0,0)

	def drawCalTarget(x=stimDisplayRes[0]/2,y=stimDisplayRes[1]/2):
		gl.glColor3f(.5,.5,.5)
		gl.glBegin(gl.GL_POLYGON)
		for i in range(360):
			gl.glVertex2f( x + math.sin(i*math.pi/180.0)*(calibrationDotSize/2.0) , y + math.cos(i*math.pi/180.0)*(calibrationDotSize/2.0))
		gl.glEnd()
		gl.glColor3f(0,0,0)
		gl.glBegin(gl.GL_POLYGON)
		for i in range(360):
			gl.glVertex2f( x + math.sin(i*math.pi/180.0)*(calibrationDotSize/8.0) , y + math.cos(i*math.pi/180.0)*(calibrationDotSize/8.0))
		gl.glEnd()


	########
	# Helper functions
	########

	#define a function that simply waits untile a specified end time
	def waitUntil(waitEndTime):
		while getTime() < waitEndTime:
			pass

	#define a function that waits for a given duration to pass
	def simpleWait(duration):
		start = getTime()
		while getTime() < (start + duration):
			pass


	#define a function that will kill everything safely
	def exitSafely():
		# stimDisplayMirrorChild.stop()
		writerChild.stop()
		stamperChild.stop(killAfter=60)
		while stamperChild.isAlive():
			time.sleep(.1)
		if doEyelink:
			eyelinkChild.stop()
		sys.exit()


	#define a function that waits for a response
	def waitForResponse():
		done = False
		while not done:
			if not stamperChild.qFrom.empty():
				event = stamperChild.qFrom.get()
				if event['type']=='key':
					response = event['value']
					if response=='escape':
						exitSafely()
					else:
						done = True
		return response


	#define a function that prints a message on the stimDisplay while looking for user input to continue. The function returns the total time it waited
	def showMessage(myText):
		messageViewingTimeStart = getTime()
		gl.glClearColor(0,0,0,1)
		gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		stimDisplay.refresh()
		drawText( myText , instructionFont , stimDisplayRes[0] , xLoc=stimDisplayRes[0]/2 , yLoc=stimDisplayRes[1]/2 , fg=[200,200,200,255] )
		simpleWait(0.500)
		stimDisplay.refresh()
		waitForResponse()
		stimDisplay.refresh()
		simpleWait(0.500)
		messageViewingTime = getTime() - messageViewingTimeStart
		return messageViewingTime


	#define a function that requests user input
	def getInput(getWhat):
		getWhat = getWhat
		textInput = ''
		gl.glClearColor(0,0,0,1)
		gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		stimDisplay.refresh()
		simpleWait(0.500)
		myText = getWhat+textInput
		drawText( myText , instructionFont , stimDisplayRes[0] , xLoc=stimDisplayRes[0]/2 , yLoc=stimDisplayRes[1]/2 , fg=[200,200,200,255] )
		stimDisplay.refresh()
		done = False
		while not done:
			if not stamperChild.qFrom.empty():
				event = stamperChild.qFrom.get()
				if event['type'] == 'key' :
					response = event['value']
					if response=='escape':
						exitSafely()
					elif response == 'backspace':
						if textInput!='':
							textInput = textInput[0:(len(textInput)-1)]
							myText = getWhat+textInput
							drawText( myText , instructionFont , stimDisplayRes[0] , xLoc=stimDisplayRes[0]/2 , yLoc=stimDisplayRes[1]/2 , fg=[200,200,200,255] )
							stimDisplay.refresh()
					elif response == 'return':
						done = True
					else:
						textInput = textInput + response
						myText = getWhat+textInput
						drawText( myText , instructionFont , stimDisplayRes[0] , xLoc=stimDisplayRes[0]/2 , yLoc=stimDisplayRes[1]/2 , fg=[200,200,200,255] )
						stimDisplay.refresh()
		stimDisplay.refresh()
		return textInput


	#define a function that obtains subject info via user input
	def getSubInfo():
		year = time.strftime('%Y')
		month = time.strftime('%m')
		day = time.strftime('%d')
		hour = time.strftime('%H')
		minute = time.strftime('%M')
		sid = getInput('ID (\'test\' to demo): ')
		order = getInput('Order (1 or 2): ')
		if sid != 'test':
			sex = getInput('Sex (m or f): ')
			age = getInput('Age (2-digit number): ')
			handedness = getInput('Handedness (r or l): ')
		else:
			sex = 'test'
			age = 'test'
			handedness = 'test'
		subInfo = [ sid , order , year , month , day , hour , minute , sex , age , handedness ]
		return subInfo

	def getT1PracticeTrials():
		trials=[]
		t2Location = 'NA'
		trialsToPrint = ''
		for rep in range(repsPerT1Practice):
			for ttoa in ttoaList:
				for cueLocation in cueLocationList:
					for t1Identity in t1IdentityList:
						if t1Identity!='NA':
							trials.append([ttoa,cueLocation,t1Identity,t2Location])
							trialsToPrint += '\t'.join(map(str,trials[-1]))+'\n'
		# print trialsToPrint
		random.shuffle(trials)
		return trials

	def getT2PracticeTrials():
		trials=[]
		t1Identity = 'NA'
		trialsToPrint = ''
		for rep in range(repsPerT2Practice):
			for cueLocation in cueLocationList:
				for t2Location in t2LocationList:
					for ttoa in ttoaList:
						trials.append([ttoa,cueLocation,t1Identity,t2Location])
						trialsToPrint += '\t'.join(map(str,trials[-1]))+'\n'
		# print trialsToPrint
		random.shuffle(trials)
		return trials

	def getTrials():
		trials=[]
		trialsToPrint = ''
		for t2Location in t2LocationList:
			for cueLocation in cueLocationList:
				for t1Identity in t1IdentityList:
					# if t1Identity=='NA':
					# 	ttoa = 'NA'
					# 	trials.append([ttoa,cueLocation,t1Identity,t2Location])
					# 	trialsToPrint += '\t'.join(map(str,trials[-1]))+'\n'
					# else:
					for ttoa in ttoaList:
						trials.append([ttoa,cueLocation,t1Identity,t2Location])
						trialsToPrint += '\t'.join(map(str,trials[-1]))+'\n'
		# print trialsToPrint
		random.shuffle(trials)
		return trials

	def checkResponses():
		responses = []
		while not stamperChild.qFrom.empty():
			event = stamperChild.qFrom.get()
			if event['type'] == 'key' :
				key = event['value']
				time = event['time']
				if key=='escape':
					exitSafely()
				responses.append([key,time])
		return responses


	def doCalibration():
		drawDot(fixationRadius)
		stimDisplay.refresh()
		eyelinkChild.qTo.put('doCalibration')
		calibrationDone = False
		while not calibrationDone:
			if not stamperChild.qFrom.empty():
				event = stamperChild.qFrom.get()
				if event['type'] == 'key' :
					# key = event['value']
					# if key=='escape':
					# 	exitSafely()
					# else: #pass keys to eyelink
					eyelinkChild.qTo.put(['keycode',event['keysym']])
			if not eyelinkChild.qFrom.empty():
				message = eyelinkChild.qFrom.get()
				print message
				if message=='calibrationComplete':
					calibrationDone = True
				elif (message=='setup_cal_display') or (message=='exit_cal_display'):
					drawDot(fixationRadius)
					stimDisplay.refresh()
				elif message=='erase_cal_target':
					pass
				elif message=='clear_cal_display':
					stimDisplay.refresh()
				elif message[0]=='draw_cal_target':
					x = message[1]
					y = message[2]
					drawCalTarget(x,y)
					stimDisplay.refresh()
				elif message[0]=='image':
					blitNumpy(message[1],stimDisplayRes[0]/2,stimDisplayRes[1]/2,xCentered=True,yCentered=True)
					stimDisplay.refresh()


	#define a function that runs a block of trials
	def runBlock(block,messageViewingTime):

		if not doEyelink:
			#clear any residual between-block responses (not necessary if doing eyelink)
			start = getTime()
			while (getTime()-start)<1:
				checkResponses()
		
		#get a trial list
		if block=='t1Practice':
			trialList = getT1PracticeTrials()
		elif block=='t2Practice':
			trialList = getT2PracticeTrials()
		else:
			trialList = getTrials()
		
		#run the trials
		trialNum = 0
		while len(trialList)>0:
			#bump the trial number
			trialNum = trialNum + 1
			print 'Block: '+str(block)+'; Trial: '+str(trialNum)
			#parse the trial info
			ttoa , cueLocation , t1Identity , t2Location = trialList.pop()
			
			trialDescrptor = '\t'.join(map(str,[subInfo[0],block,trialNum]))

			drawRing(-targetOffset)
			drawRing(targetOffset)
			drawRing()
			drawCalTarget()
			stimDisplay.refresh()
			start = getTime()
			if doEyelink:
				outerDone = False
				while not outerDone:
					drawRing(-targetOffset)
					drawRing(targetOffset)
					drawRing()
					drawCalTarget()
					stimDisplay.refresh()
					outerDone = True #set to False below if need to re-do drift correct after re-calibration
					eyelinkChild.qTo.put('doDriftCorrect')
					innerDone = False
					while not innerDone:
						if not eyelinkChild.qFrom.empty():
							message = eyelinkChild.qFrom.get()
							if message=='driftCorrectComplete':
								innerDone = True
							elif message=='doCalibration':
								doCalibration()
								innerDone = True
								outerDone = False
						while not stamperChild.qFrom.empty():
							event = stamperChild.qFrom.get()
							if event['type'] == 'key' :
								key = event['value']
								time = event['time']
								eyelinkChild.qTo.put(['keycode',event['keysym']])
								#print ['main','keycode',key]
				eyelinkChild.qTo.put(['reportBlinks',True])
				eyelinkChild.qTo.put(['reportSaccades',True])
				eyelinkChild.qTo.put(['sendMessage','trialStart\t'+trialDescrptor])
			trialInitiationTime = getTime() - start

			#prep and show the fixation twice (ensures 2nd refresh will block; for better trial start time accuracy)
			for i in range(2):
				drawRing(-targetOffset)
				drawRing(targetOffset)
				drawRing()
				drawDot(fixationRadius)
				if i==0: #only draw on the first frame
					drawPhotoStim()
				stimDisplay.refresh()

			#get the trial start time 
			trialStartTime = getTime() - 1/60.0 #time that the previous (first) refresh returned

			#compute event times
			cueOnTime = trialStartTime + fixationDuration
			cueOffTime = cueOnTime + cueDuration
			cuebackOnTime = cueOnTime + cueCuebackOA			
			cuebackOffTime = cuebackOnTime + cuebackDuration
			t2OnTime = cueOnTime + cueTargetOA #computed even though there might be no t2
			responseTimeoutTime = t2OnTime + responseTimeout
			t1OnTime = t2OnTime - ttoa

			#initialize some variables
			blink = 'FALSE'
			saccade = 'FALSE'
			cueOn = False
			cueOff = False
			cuebackOn = False
			cuebackOff = False
			t1On = False
			t2On = False
			badKey = 'FALSE'
			t1Response = 'NA'
			t1RT = 'NA'
			tooManyT1 = 'FALSE'
			t1TooSoon = 'FALSE'
			t1ResponseWhenT1Absent = 'FALSE'
			t2Response = 'NA'
			t2RT = 'NA'
			tooManyT2 = 'FALSE'
			t2TooSoon = 'FALSE'
			t2ResponseWhenT2Absent = 'FALSE'
			feedbackResponse = 'FALSE'
			recalibration = 'FALSE'

			#prep the cue screen
			if cueLocation=='left':
				drawRing(-targetOffset,1)
				drawRing(targetOffset)
				drawRing()
			elif cueLocation=='right':
				drawRing(-targetOffset)
				drawRing(targetOffset,1)
				drawRing()
			else:
				drawRing(-targetOffset)
				drawRing(targetOffset)
				drawRing(0,1)
			drawDot(fixationRadius)

			#start the loop
			trialDone = False
			while not trialDone:
				#manage stimuli
				if not cueOn:
					if getTime()>=cueOnTime:
						#show the cue screen
						stimDisplay.refresh()
						if doEyelink:
							eyelinkChild.qTo.put(['sendMessage','cueOn\t'+trialDescrptor])
						cueOn = True
						#prep the cue off screen
						drawRing(-targetOffset)
						drawRing(targetOffset)
						drawRing()
						drawDot(fixationRadius)
				elif not cueOff:
					if getTime()>=cueOffTime:
						#show the cueOff screen
						stimDisplay.refresh()
						cueOff = True
						if doEyelink:
							eyelinkChild.qTo.put(['sendMessage','cueOff\t'+trialDescrptor])
						#prep the cueback screen
						drawRing(-targetOffset)
						drawRing(targetOffset)
						drawRing(0,1)
						drawDot(fixationRadius)
				elif not cuebackOn:
					if getTime()>=cuebackOnTime:
						#show the cueback screen
						stimDisplay.refresh()
						cuebackOn = True
						if doEyelink:
							eyelinkChild.qTo.put(['sendMessage','cuebackOn\t'+trialDescrptor])
						#prep the cuebackOff screen
						drawRing(-targetOffset)
						drawRing(targetOffset)
						drawRing()
						drawDot(fixationRadius)
				elif not cuebackOff:
					if getTime()>=cuebackOffTime:
						#show the cueback-off screen
						stimDisplay.refresh()
						cuebackOff = True
						if doEyelink:
							eyelinkChild.qTo.put(['sendMessage','cuebackOff\t'+trialDescrptor])
						#prep the target screen
						drawPhotoStim()
						drawRing(-targetOffset)
						drawRing(targetOffset)
						drawRing()
						drawDot(fixationRadius)
						if t2Location=='left':
							drawDot(targetRadius,-targetOffset)
						elif t2Location=='right':
							drawDot(targetRadius,targetOffset)
				elif not t1On:
					if getTime()>=t1OnTime:
						t1On = True
						if t1Identity=='hi':
							hiSound.play()
						elif t1Identity=='lo':
							loSound.play()
						if doEyelink:
							eyelinkChild.qTo.put(['sendMessage','t1On\t'+trialDescrptor])
				elif not t2On:
					if getTime()>=t2OnTime:
						#show t2
						stimDisplay.refresh()
						t2On = True
						if doEyelink:
							eyelinkChild.qTo.put(['sendMessage','t2On\t'+trialDescrptor])
							# eyelinkChild.qTo.put(['reportSaccades',True])
				elif getTime()>=responseTimeoutTime:
						trialDone = True
						if (t1Response=='NA') and not (t1Identity=='NA'):
							if (t2Response=='NA') and not (t2Location=='NA'):
								feedbackText = 'Missed both!'
							else:
								feedbackText = 'Missed tone!'
						elif (t2Response=='NA') and not (t2Location=='NA'):
							feedbackText = 'Missed dot!'
				#manage responses
				while not stamperChild.qFrom.empty():
					event = stamperChild.qFrom.get()
					if event['type'] == 'key' :
						keyPressed = event['value']
						keyTime = event['time']
						if keyPressed=='escape':
							exitSafely()
						elif (keyPressed not in t1ResponseKeys) and (keyPressed not in t2ResponseKeys):
							badKey = 'TRUE'
							trialDone = True
							feedbackText = 'Bad key!'
						elif keyPressed in t1ResponseKeys:
							if t1Response!='NA': #already made a t1 response
								trialDone = True
								feedbackText = 'Too many tone keys!'
								tooManyT1 = 'TRUE'
							elif keyTime<t1OnTime:
								trialDone = True
								feedbackText = 'Tone key too soon!'
								t1TooSoon = 'TRUE'
							elif t1Identity=='NA':
								trialDone = True
								feedbackText = 'No tone!'
								t1ResponseWhenT1Absent = 'TRUE'
							else:
								t1RT = keyTime - t1OnTime
								if keyPressed==t1ResponseKeys[0]:
									t1Response = 'lo'
								else:
									t1Response = 'hi'
								t1Feedback = str(int(t1RT*10))
								if t1Response!=t1Identity:
									t1Feedback = 'x'+t1Feedback+'x'
								if (t2Response!='NA') or (t2Location=='NA'):
									trialDone = True
									if t2Location=='NA':
										t2Feedback = '0'
									feedbackText = [t1Feedback,t2Feedback]
						elif keyPressed in t2ResponseKeys:
							if t2Response!='NA':
								trialDone = True
								feedbackText = 'Too many dot keys!'
								tooManyT2 = 'TRUE'
							elif keyTime<t2OnTime:
								trialDone = True
								feedbackText = 'Dot key too soon!'
								t2TooSoon = 'TRUE'
							elif t2Location=='NA':
								trialDone = True
								feedbackText = 'No dot!'
								t2ResponseWhenT2Absent = 'TRUE'
							else:
								t2RT = keyTime - t2OnTime
								if keyPressed==t2ResponseKeys[0]:
									t2Response = 'left'
								else:
									t2Response = 'right'
								t2Feedback = str(int(t2RT*10))
								if t2Response!=t2Location:
									t2Feedback = 'x'+t2Feedback+'x'
								if (t1Response!='NA') or (t1Identity=='NA'):
									trialDone = True
									if t1Identity=='NA':
										t1Feedback = '0'
									feedbackText = [t1Feedback,t2Feedback]
				#manage eye movements
				if doEyelink:
					if not eyelinkChild.qFrom.empty():
						message = eyelinkChild.qFrom.get()
						if message=='blink':
							# print 'main: blink'
							blink = 'TRUE'
							trialDone = True
							feedbackText = 'Blinked!'
							trialList.append([ttoa , cueLocation , t1Identity , t2Location])
							random.shuffle(trialList)
						elif message[0]=='gazeTargetLost': #saccade
							# print 'main: saccade'
							saccade = 'TRUE'
							trialDone = True
							feedbackText = 'Eyes moved!'
							trialList.append([ttoa , cueLocation , t1Identity , t2Location])
							random.shuffle(trialList)
			#trial done, do feedback
			if doEyelink:
				eyelinkChild.qTo.put(['sendMessage','trialDone\t'+trialDescrptor])
				eyelinkChild.qTo.put(['reportBlinks',False])
				eyelinkChild.qTo.put(['reportSaccades',False])
			#show feedback
			gl.glClear(gl.GL_COLOR_BUFFER_BIT)
			drawRing(-targetOffset)
			drawRing(targetOffset)
			drawRing()
			drawFeedback(feedbackText)
			stimDisplay.refresh()
			feedbackDone = False
			feedbackDoneTime = getTime() + feedbackDuration
			while not feedbackDone:
				if getTime()>feedbackDoneTime:
					feedbackDone = True
				else:
					while not stamperChild.qFrom.empty():
						event = stamperChild.qFrom.get()
						if event['type'] == 'key' :
							key = event['value']
							time = event['time']
							if key=='escape':
								exitSafely()
							elif key=='p' and doEyelink:
								feedbackDone = True
								recalibration = 'TRUE'
								doCalibration()
							else: #haven't done a recalibration
								feedbackResponse = 'TRUE'
								#update feedback
								drawRing(-targetOffset)
								drawRing(targetOffset)
								drawRing()
								drawFeedback("Don't respond during feedback!")
								stimDisplay.refresh()
								feedbackDoneTime = getTime() + feedbackDuration
			#write out trial info
			dataToWrite = '\t'.join(map(str,[ subInfoForFile , messageViewingTime , block , trialNum , trialInitiationTime , ttoa , cueLocation , t1Identity , t2Location , badKey , t1Response , t1RT , tooManyT1 , t1TooSoon , t1ResponseWhenT1Absent , t2Response , t2RT , tooManyT2 , t2TooSoon , t2ResponseWhenT2Absent , feedbackResponse , recalibration , blink , saccade]))
			writerChild.qTo.put(['write','data',dataToWrite])
		print 'on break'



	########
	# Initialize the data files
	########

	if doEyelink:
		doCalibration()

	#get subject info
	subInfo = getSubInfo()
	order = subInfo[1]

	if not os.path.exists('_Data'):
		os.mkdir('_Data')
	if subInfo[0]=='test':
		filebase = 'test'
	else:
		filebase = '_'.join(subInfo[0:7])
	if not os.path.exists('_Data/'+filebase):
		os.mkdir('_Data/'+filebase)

	shutil.copy(sys.argv[0], '_Data/'+filebase+'/'+filebase+'_code.py')

	if doEyelink:
		eyelinkChild.qTo.put(['edfPath','_Data/'+filebase+'/'+filebase+'_eyelink.edf'])

	writerChild.qTo.put(['newFile','data','_Data/'+filebase+'/'+filebase+'_data.txt'])
	header ='\t'.join(['id' , 'order' , 'year' , 'month' , 'day' , 'hour' , 'minute' , 'sex' , 'age'  , 'handedness' , 'messageViewingTime' , 'block' , 'trialNum' , 'trialInitiationTime', 'ttoa' , 'cueLocation' , 't1Identity' , 't2Location' , 'badKey' , 't1Response' , 't1RT' , 'tooManyT1' , 't1TooSoon' , 't1ResponseWhenT1Absent' , 't2Response' , 't2RT' , 'tooManyT2' , 't2TooSoon' , 't2ResponseWhenT2Absent' , 'feedbackResponse' , 'recalibration' , 'blink' , 'saccade' ])
	writerChild.qTo.put(['write','data',header])


	subInfoForFile = '\t'.join(map(str,subInfo))


	########
	# Start the experiment
	########

	showMessage('During this experiment, when you see a grey dot at the center of the screen, we\'d like you to try to refrain from blinking or moving your eyes. Every few seconds the dot will be replaced by text, at which time you can blink if you need to, but when the grey dot re-appears please try to keep your eyes open and fixed onthe grey dot.\n\nEvery few minutes you\'ll be provided with a longer opportunity to blink and relax your eyes.\n\nTo continue to the next page of instructions, press any key.')

	showMessage('Throughout the experiment, grey rings will appear at the center, left and right sides of the screen. Sometimes one of these rings will flash white briefly, but which ring gets flashed is completely random. The flash can sometimes grab your attention but please try to keep your eyes looking at the grey dot at the center of the screen.\n\nTo continue to the next page of instructions, press any key.')

	t1PracticeMessage = 'During this part of the experiment you will be staring at the grey dot and listening for tones that will sound. When you hear a low tone, press the "z" key.\nWhen you hear a high tone, press the "a" key.\n\nAfter you respond, you will see a number that tells you how quickly you responded; faster responses yield lower numbers. If you pressed the wrong key (for example, if the tone was high and you pressed the low key), then the number will have an "x" on either side. Try to respond as quickly as you can without making too many errors.\n\nWhen the numbers appear you can blink if you need to but when the grey dot reappears try to keep your eyes focused at the center of the screen.\n\nWhen you are ready to begin practice, press any key.'

	t2PracticeMessage = 'During this part of the experiment you will be staring at the grey dot and watching for dots that will appear. When a dot appears on the left, press the "<" key.\nWhen a dot appears on the right, press the ">" key.\n\nAfter you respond, you will see a number that tells you how quickly you responded; faster responses yield lower numbers. If you pressed the wrong key (for example, if the dot was on the right and you pressed the left key), then the number will have an "x" on either side. Try to respond as quickly as you can without making too many errors.\n\nWhen the numbers appear you can blink if you need to but when the grey dot reappears try to keep your eyes focused at the center of the screen.\n\nWhen you are ready to begin practice, press any key.'

	bothPracticeMessage1 = 'During this part of the experiment you will be staring at the grey dot and listening for tones that will sound and also watching for dots that will appear. When you hear a low tone, press the "z" key.\nWhen you hear a high tone, press the "a" key.\n\nWhen a dot appears on the left, press the "<" key.\nWhen a dot appears on the right, press the ">" key.\n\nTo continue to the next page of instructions, press any key.'
	
	bothPracticeMessage2 = 'You will receive feedback as before, this time with two numbers reflecting how quickly and accurately you responded to each target type (tone and dot), with the tone-related number appearing slightly above the dot-related number. Try to respond quickly to both target types without making too many errors on either target type.\n\nWhen the numbers appear you can blink if you need to but when the grey dot reappears try to keep your eyes focused at the center of the screen.\n\nWhen you are ready to begin practice, press any key.'

	if order=='1':
		messageViewingTime = showMessage(t1PracticeMessage)
		block = 't1Practice'
		runBlock(block,messageViewingTime)

		messageViewingTime = showMessage(t2PracticeMessage)
		block = 't2Practice'
		runBlock(block,messageViewingTime)
	else:
		messageViewingTime = showMessage(t2PracticeMessage)
		block = 't2Practice'
		runBlock(block,messageViewingTime)

		messageViewingTime = showMessage(t1PracticeMessage)
		block = 't1Practice'
		runBlock(block,messageViewingTime)


	messageViewingTime = showMessage(bothPracticeMessage1)
	messageViewingTime = showMessage(bothPracticeMessage2)
	block = 'bothPractice'
	runBlock(block,messageViewingTime)

	messageViewingTime = showMessage('You\'re all done practice.\n\nRemember to try to keep your eyes focused at the center of the screen. When you are ready to begin the experiment, press any key.')

	t1PracticeMessage2 = 'For the next few minutes, there will be no dots and you will only hear the tones.\n\nWhen you are ready to begin, press any key.'

	t2PracticeMessage2 = 'For the next few minutes, there will be no tones and you will only see the dots.\n\nWhen you are ready to begin, press any key.'

	bothResumeMessage = 'The experiment will now resume presenting both tones and dots.\n\nWhen you are ready to begin, press any key.'

	blockNum = 0
	for i in range(len(numberOfBlocks)):
		for j in range(numberOfBlocks[i]):
			blockNum += 1
			runBlock(blockNum,messageViewingTime)
			if j<(numberOfBlocks[i]-1):
				messageViewingTime = showMessage('Take a break!\n\nWhen you are ready to continue the experiment, press any key.')
		if i<(len(numberOfBlocks)-1):
			if order=='1':
				messageViewingTime = showMessage(t1PracticeMessage2)
				block = 't1Practice'
				runBlock(block,messageViewingTime)
				messageViewingTime = showMessage(t2PracticeMessage2)
				block = 't2Practice'
				runBlock(block,messageViewingTime)
			else:
				messageViewingTime = showMessage(t2PracticeMessage2)
				block = 't2Practice'
				runBlock(block,messageViewingTime)
				messageViewingTime = showMessage(t1PracticeMessage2)
				block = 't1Practice'
				runBlock(block,messageViewingTime)
			messageViewingTime = showMessage(bothResumeMessage)

	messageViewingTime = showMessage('You\'re all done!\nPlease the person running this experiment will be with you shortly.')

	exitSafely()
