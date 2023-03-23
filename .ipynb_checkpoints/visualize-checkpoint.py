import cv2
import numpy as np
  
# Create a VideoCapture object and read from input file
cap = cv2.VideoCapture('videos/synthvideo3.mp4')
  
# Our bounding boxes are as follows:
wb1 = [(213,274),(772,772)]
wb2 = [(816,366),(1200,725)]
wb3 = [(1294,290),(1881,765)]

font = cv2.FONT_HERSHEY_SIMPLEX
# fontScale
fontScale = 1
# Blue color in BGR
color = (255, 255, 255)
# Line thickness of 2 px
thickness = 2

# Check if camera opened successfully
if (cap.isOpened()== False):
    print("Error opening video file")
  
# Read until video is completed
while(cap.isOpened()):
      
# Capture frame-by-frame
    ret, frame = cap.read()

    frame = cv2.rectangle(frame, wb1[0], wb1[1], (255, 0, 0), 2)
    frame = cv2.rectangle(frame, wb2[0], wb2[1], (255, 0, 0), 2)
    frame = cv2.rectangle(frame, wb3[0], wb3[1], (255, 0, 0), 2)

    frame = cv2.putText(frame, "bridgewatchbox1", wb1[0], font, 
                   fontScale, color, thickness, cv2.LINE_AA)
    frame = cv2.putText(frame, 'bridgewatchbox2', wb2[0], font, 
                   fontScale, color, thickness, cv2.LINE_AA)
    frame = cv2.putText(frame, 'bridgewatchbox3', wb3[0], font, 
                   fontScale, color, thickness, cv2.LINE_AA)

    if ret == True:
    # Display the resulting frame
        cv2.imshow('Frame', frame)
          
    # Press Q on keyboard to exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
  
# Break the loop
    else:
        break
  
# When everything done, release
# the video capture object
cap.release()
  
# Closes all the frames
cv2.destroyAllWindows()