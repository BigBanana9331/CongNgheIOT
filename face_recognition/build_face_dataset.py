# import the necessary packages
import argparse
import imutils
import time
import cv2
import os

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
# ap.add_argument("-c", "--cascade", required=True,
# 	help = "path to where the face cascade resides")
ap.add_argument("-o", "--output", required=True,
	help="path to output directory")
args = vars(ap.parse_args())
def gstreamer_pipeline(
    capture_width=1280,
    capture_height=720,
    display_width=600,
    display_height=480,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )
# load OpenCV's Haar cascade for face detection from disk
detector = cv2.CascadeClassifier("xml/haarcascade_frontalface_default.xml")
# initialize the video stream, allow the camera sensor to warm up,
# and initialize the total number of example faces written to disk
# thus far
print("[INFO] starting video stream...")
cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
# cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
# vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)
total = 0
# loop over the frames from the video stream
fpsReport = 0
font = cv2.FONT_HERSHEY_SIMPLEX
timeStamp = time.time()
while True:
	# grab the frame from the threaded video stream, clone it, (just
	# in case we want to write it to disk), and then resize the frame
	# so we can apply face detection faster
	ret, frame = cap.read()
	orig = frame.copy()
	# frame = imutils.resize(frame, width=300)
	# detect faces in the grayscale frame
	rects = detector.detectMultiScale(
		cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), scaleFactor=1.1, 
		minNeighbors=5, minSize=(30, 30))
	# loop over the face detections and draw them on the frame
	for (x, y, w, h) in rects:
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # show the output frame
	dt=time.time()-timeStamp
	fps=1/dt
	fpsReport=.90*fpsReport + .1*fps
	timeStamp = time.time()
	cv2.putText(frame,str(round(fpsReport,1))+ 'fps',(0,25),font,.75,(0,255,255,2))
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
 
	# if the `k` key was pressed, write the *original* frame to disk
	# so we can later process it and use it for face recognition
	if key == ord("k"):
		p = os.path.sep.join([args["output"], "{}.png".format(
			str(total).zfill(5))])
		cv2.imwrite(p, orig)
		total += 1
	# if the `q` key was pressed, break from the loop
	elif key == ord("q"):
		break
    # print the total faces saved and do a bit of cleanup
print("[INFO] {} face images stored".format(total))
print("[INFO] cleaning up...")
cap.release()
cv2.destroyAllWindows()
