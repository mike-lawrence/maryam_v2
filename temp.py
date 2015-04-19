import sdl2
import time
import OpenGL.GL as gl

stimDisplayRes = (1920,1080) #pixel resolution of the stimDisplay
stimDisplayPosition = (-1440-1920,-30)

flags = sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP | sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC


byteify = lambda x, enc: x.encode(enc)

Window = sdl2.video.SDL_CreateWindow(byteify('test', "utf-8"),stimDisplayPosition[0],stimDisplayPosition[1],stimDisplayRes[0],stimDisplayRes[1],flags)
glContext = sdl2.SDL_GL_CreateContext(Window)


print 'fullscreen white'
gl.glClearColor(1,1,1,1)
gl.glClear(gl.GL_COLOR_BUFFER_BIT)
sdl2.SDL_GL_SwapWindow(Window)
start = time.time()
while time.time()<(start+5):
	sdl2.SDL_PumpEvents()

sdl2.SDL_DestroyWindow(Window)
#del Window
# del glContext
time.sleep(1)
Window = sdl2.video.SDL_CreateWindow(byteify('test', "utf-8"),stimDisplayPosition[0],stimDisplayPosition[1],stimDisplayRes[0],stimDisplayRes[1],flags)
glContext = sdl2.SDL_GL_CreateContext(Window)

print 'fullscreen grey'
gl.glClearColor(.5,.5,.5,1)
gl.glClear(gl.GL_COLOR_BUFFER_BIT)
sdl2.SDL_GL_SwapWindow(Window)
start = time.time()
while time.time()<(start+5):
	sdl2.SDL_PumpEvents()

# print 'hidden'
# sdl2.SDL_MinimizeWindow(Window)
# start = time.time()
# while time.time()<(start+2):
# 	sdl2.SDL_PumpEvents()


# print 'fullscreen'
# sdl2.SDL_RestoreWindow(Window)
# start = time.time()
# while time.time()<(start+2):
# 	sdl2.SDL_PumpEvents()

# print 'fullscreen green'
# gl.glClearColor(1,.5,1,1)
# gl.glClear(gl.GL_COLOR_BUFFER_BIT)
# sdl2.SDL_GL_SwapWindow(Window)
# start = time.time()
# while time.time()<(start+1):
# 	sdl2.SDL_PumpEvents()


# print 'fullscreen blue'
# gl.glClearColor(.5,1,1,1)
# gl.glClear(gl.GL_COLOR_BUFFER_BIT)
# sdl2.SDL_GL_SwapWindow(Window)
# start = time.time()
# while time.time()<(start+5):
# 	sdl2.SDL_PumpEvents()


