
from imutils import contours
from collections import deque
import numpy as np
import argparse
import imutils
import cv2

#get timestamp for text file output
from time import gmtime, strftime
Time = strftime("%Y-%m-%d %H%M%S", gmtime())

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", default='60fps.mp4',
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=10,
	help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "dot"
# in the HSV color space
dotLower = (18, 139, 218)
dotUpper = (50, 255, 255)

# initialize values
camera = cv2.VideoCapture(args["video"])
pts = deque(maxlen=args["buffer"])
counter = 0
FirstInitial = 0
SecondInitial = 0
FirstPoint = 0
SecondPoint = 0
(d1, d2) = (0, 0)
Difference = 0
Delta = 0

# keep looping
while True:
     # get the current frame
     (grabbed, frame) = camera.read()

	# if no frame,then end of the video
     if args.get("video") and not grabbed:
		break

    # resize the frame and blur it and convert it to the HSV color space
     frame = imutils.resize(frame, width=600)
     blurred = cv2.GaussianBlur(frame, (11, 11), 0)
     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
     
     # construct a mask for the dot, then perform
     # dilations and erosions to remove small
     # blobs of noise left in the mask
     mask = cv2.inRange(hsv, dotLower, dotUpper)
     mask = cv2.erode(mask, None, iterations=2)
     mask = cv2.dilate(mask, None, iterations=2)
     
     # find contours in the mask and generate the current
     # (x, y) center of the dot
     cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                             cv2.CHAIN_APPROX_SIMPLE)
     cnts = cnts[0] if imutils.is_cv2() else cnts[1]
     cnts = contours.sort_contours(cnts,"top-to-bottom")[0]
     center = None
     
     # loop over the contours
     for (i, c) in enumerate(cnts):
         # draw the spot on the image
         (x, y, w, h) = cv2.boundingRect(c)
         ((cX, cY), radius) = cv2.minEnclosingCircle(c)
         
         if radius > 10:
             cv2.circle(frame, (int(cX), int(cY)), int(radius),(0, 0, 255), 3)
             cv2.circle(frame, (int(cX), int(cY)), 5, (0, 0, 255), -1)
             M = cv2.moments(c)
             cv2.putText(frame, "#{}".format(i + 1), (x, y - 15),
                         cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
             if i == 0:
                 FirstPoint = int(cX)
                 
             if i == 1 :
                 SecondPoint = int(cX)
                 
             if counter ==1:             
                 FirstInitial = FirstPoint
                 SecondInitial = SecondPoint
                 DeltaInitial = FirstPoint - SecondPoint
                 
     center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
     pts.appendleft(center) 
         
     # only proceed if one or more contours are found
     if len(cnts) > 0:
             
         # loop over the set of tracked points
         for i in np.arange(1, len(pts)):
             # if either of the tracked points are None, ignore them
             if pts[i - 1] is None or pts[i] is None:
                 continue

             if counter >= 2:
                 #d1 = int(FirstInitial - FirstPoint)
                 #d2 = int(SecondInitial - SecondPoint)
                 Difference = int(FirstPoint - SecondPoint)
                 Delta = Difference - DeltaInitial
                 
        # show the movement deltas
         cv2.putText(frame, "Delta : {}, ".format(Delta),
         (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,0.35,
         (0, 0, 255), 1)

         if counter ==1:
             
             #Create text file with headers
             f = open(Time + ".txt", "a")
             f.write(Time + '\n' + "Dot 1 Initial X" + '\t' + 
                     str(FirstInitial) + '\t' + "Dot 2 Initial X" + '\t' + 
                     str(SecondInitial) + '\n' + "|Frame|" + '\t' + 
                    "|Dot 1 X|" + '\t' + "|Dot 2 X|" + '\t' + "|Difference|" 
                    + '\t' + "|Delta|"+ '\n')
             f.close()
             
         if counter >=2:  
             #Open new text file with new timestamp
             f = open(Time + ".txt", "a") 
             f.write(str(counter) + '\t' + str(FirstPoint) + '\t' +
                 str(SecondPoint) + '\t' + str(Difference) + '\t' + str(Delta) 
                 + '\n')
             f.close()
                 
        # show the frame to the screen and increment the frame counter
         cv2.imshow("Frame", frame)
         key = cv2.waitKey(1) & 0xFF
         counter += 1

         # if the 'q' key is pressed, stop the loop
     if key == ord("q"): 
         break
     
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
