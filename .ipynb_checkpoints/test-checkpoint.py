from ce_builder import sensor_event_stream, watchbox, complexEvent, Event, OR, AND, GEN_PERMUTE
import time
import os
import cv2
import numpy as np

import json
data_file = open("complex_results.json", "r")
json_results = json.load(data_file)
data_file.close()

def get_data(frame_index):
    data = []
    
    for x in json_results:
        if x['time'] == frame_index:
            data.append(x)
    return data

# CE1

# First, initialize our complex event
ce1 = complexEvent()
# Set up our watchboxes
ce1.addWatchbox("bridgewatchbox1 = watchbox('camera3', positions=[213,274,772,772], id=0)")
ce1.addWatchbox("bridgewatchbox2 = watchbox('camera3', positions=[816,366,1200,725], id=1)")
ce1.addWatchbox("bridgewatchbox3 = watchbox('camera3', positions=[1294,290,1881,765], id=2)")

# Now we set up the atomic events

# First, four vehicles approach the bridge from one side
ev11a = Event("bridgewatchbox1.composition(at=0, model='rec_vehicle').size==4 and bridgewatchbox1.composition(at=1, model='rec_vehicle').size!=4")

ev11a1 = Event("bridgewatchbox1.composition(at=0, model='rec_vehicle').size==4 and bridgewatchbox1.composition(at=1, model='rec_vehicle').size==5")

# Next, we have two vehicles on either side of the bridge
ev11b = Event( "bridgewatchbox1.composition(at=0, model='rec_vehicle').size==2 and bridgewatchbox3.composition(at=0, model='rec_vehicle').size==2" )

# Then we have two vehicles exit watchbox 3
ev11c1 = Event( "bridgewatchbox3.composition(at=1, model='rec_vehicle').size==2 and bridgewatchbox3.composition(at=0, model='rec_vehicle').size==0" )

# And then two vehicles show up in watchbox 1
ev11c2 = Event( "bridgewatchbox1.composition(at=0, model='rec_vehicle').size==4 and bridgewatchbox1.composition(at=1, model='rec_vehicle').size!=4" )

ev11d = Event( "bridgewatchbox1.composition(at=0, model='rec_vehicle').size==4 and bridgewatchbox1.composition(at=1, model='rec_vehicle').size==5" )

# And finally we add these events together
ce1.addEventSequence([ OR(ev11a, ev11a1), ev11b, GEN_PERMUTE(ev11c1, "size"), AND(ev11c2, ev11d)])

print(GEN_PERMUTE(ev11c1, "size").event)



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
frame_index = 0
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
        
        # Parse our result data, and display it at the correct frame index
        incoming_data = get_data(frame_index)
        # print(frame_index)
        if incoming_data:
            #### RUN OUR EVALUATION ON THE EVENT ANYTIME WE GET NEW DATA
            ce1.update(incoming_data)
            result, change_of_state, old_results = ce1.evaluate()
            
            if change_of_state:
                print()
                print(old_results)
                print(result)
            
#             event_occurred, results = ce1.evaluate()
#             if event_occurred:
                
#                 for result in results:
#                     print("Event %s has changed to %s at frame %d" %(result[0], str(result[1]), frame_index))
          
    # Press Q on keyboard to exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
        # Break the loop
    else:
        break
        
            
    
  
    frame_index += 1
    # time.sleep(1/120)
    # event_occurred, event_name = ce1.evaluate()
    # if event_occurred:
    #     print("Event %s occurred at frame %d" %(event_name, frame_index))
        
# When everything done, release
# the video capture object
cap.release()
  
# Closes all the frames
cv2.destroyAllWindows()

    
    