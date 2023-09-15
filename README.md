# Introduction

This repo provides a way to specify complex events which reads in event information from multiple sensor sources.  See the example_data/ folder to format input.  Ideally this repo should be used as part of https://github.com/nesl/DANCER which provides a client that generates this information.  However, we have also provided some examples so this repo can be used standalone.
See the main function under test_ce.py to see how this can be used.

### Setting up a Complex Event

First, we have to set up complex events.  The complexEvent class is responsible for executing our symbolic logic.  The initialization takes only one parameter - class_mappings.  Class mappings map a string describing the object into the object label.  For example, {"person": 0,"car": 2,"package": 30}.  The string description is used by our later atomic event syntax to target particular objects.
```
ce_name = complexEvent(class_mappings)
```

### Adding Watchboxes

Next, we have to set up our spatial detection features, such as watchboxes.  These take the following format:
```
ce_name.addWatchbox(name='XX', region_id='YY', positions=[aa,bb,cc,dd], classes=['ZZ'], watchbox_id=WBID , class_mappings=class_mappings)")
```
Here, XX is the name of our watchbox which can be referenced in later events.  YY is corrsponds to a particular ID of a camera.  The positions of aa,bb,cc,dd refer to the top left (aa,bb) and bottom right (cc,dd) coordinates of the watchbox in the image.  ZZ is an string describing the class of object that this watchbox should monitor for.  There may be multiple strings for classes.  WBID is a unique integer ID assigned to this watchbox - this will later be removed since it serves the same function as name.  class_mappings is the same dictionary object described earlier.


### Events which Affect Watchboxes

In this system, we receive data about events which alter the state of watchboxes.  These events originate from distributed sensors, or in our examples, as text files which list out each event.  These events are structured as follows:
```
{'frame_index': FRAME_INDEX, 'tracks': {}, 'vicinal_events': []}
```
FRAME_INDEX is an integer describes the current frame index of, for example, a video.  'tracks' describes a dictionary consisting of { trackID : {'bbox_data': BB_DATA, 'prediction' : PRED_LABEL} }.  trackID is a unique integer assigned to a detected object after a tracking algorithm is applied.  BB_DATA is a list of coordinates within an image where the object is located.  PRED_LABEL is an integer corresponding to the detected object's label.  'vicinal_events' further includes information about the object and how it interacted with a watchbox.
For example, in example_data/ce1_carla_example/ae_cam1.txt:
```
{'frame_index': 161, 'tracks': {3082: {'bbox_data': [743.06, 353.0, 790.74, 418.8], 'prediction': 0}}, 'vicinal_events': [{'camera_id': 1, 'results': [{'track_id': 3082, 'watchboxes': [0], 'enters': [True], 'directions': ['middle'], 'class': 0}], 'time': 161}]}
```
This line describes the detected objects and vicinal events at frame index 161.  It detects a unique object, which is assigned the trackID of 3082 with class 0 (pedestrian if we use the previously mentioned class_mapping).  The vicinal event shows that this object showed up in camera with ID 1, and it entered watchbox ID of 0 from the middle of the watchbox.


### Adding Atomic Events

To add an event we can simply use the following syntax:
```
event_name = Event("WATCHBOX_NAME.composition(at=EVENT_INDEX, model=OBJECT_CLASS).ATTRIBUTE==CC")
```
where WATCHBOX_NAME refers to the name of our watchbox declared previously (e.g. XX).  The '.composition()' takes several parameters:

at=EVENT_INDEX, which refers to the current and previous events occurring in this watchbox.  Importantly, the order of time is reversed: at=0 refers to the current time, while at=1 refers to the previous event, and at=2 refers to the previous to previous event, etc.

model=OBJECT_CLASS refers to the name of the object class we want the watchbox to filter for (which should correspond to the string description used in our class_mappings).  In the current implementation it is not used internally yet.

ATTRIBUTE is really just a class attribute which is returned from the composition() function.  For more information, see class watchboxResult in ce_builder.py.
This attribute can have some arithmetic or logical operators, the same which Python uses.  **In fact, every statement inside Event() is really just a string which is executed as a Python command.**

### Creating more complicated atomic events

Since every statement inside Event() is just Python code, you can also use the regular logical operators of python - namely, 'and' and 'or'.  This allows you to construct statements which also operate over time:
```
bridgewatchbox1.composition(at=0, model='rec_vehicle').size==4 and bridgewatchbox1.composition(at=1, model='rec_vehicle').size!=4
```
This basically says 'for this particular watchbox named bridgewatchbox1, we are checking to see if at its most recent event (at=0), it saw four objects of type rec_vehicle, and also making sure that at the previous event (at=1) it did not see four objects of type rec_vehicle'.  In simple terms, we are checking to see if 4 rec_vehicles entered bridgewatchbox1 when there were not 4 previously.

### Combining atomic events together to create complex events

We can also chain atomic events together, expressing a sequence of them like a finite state machine.
```
ce_name.addEventSequence([ event1, event2, etc...  ], no_enforce_sequence=Y)
```
where event1, event2 are all referring to Event() objects.  The no_enforce_sequence parameter will either enforce strict ordering (e.g. event1 must occur, then event2, etc), or ignore any ordering requirements.  Set to True if you are not enforcing any ordering, and False otherwise.

### More flexible complex events

One can also make this a bit more flexible by using these operators:
```
OR(event1, event2, etc)
```
This means that as long as any of these events become true, we can move onto the next item in our sequence.
```
AND(event1, event2, etc)
```
This means that as long as all of these events become true, we can move onto the next item in our sequence.
```
WITHIN(event1, event2, time_constraint)
```
This means event2 must occur within some period of time that event1 occurs. This period of time is given by time_constraint.  Currently time_constraint is measured as frames in a video (e.g. time_constraint = 5400 means that event1 must occur within 3 minutes of event2)
```
GEN_PERMUTE(event1, "ATTRIBUTE")
```
This is a bit more complex.  Basically, when our atomic events operate over time, there is a chance for certain ambiguities to arise when determining how they occur.  For example, let's examine the following event:
```
bridgewatchbox1.composition(at=0, model='rec_vehicle').size==3 and bridgewatchbox1.composition(at=1, model='rec_vehicle').size==0
```
This means that at the most recent event, we will have three rec_vehicles, but at the previous event we will have zero rec_vehicles (meaning three rec_vehicles eventually arrive in this watchbox).  But in reality, this doesn't quite make sense - objects don't suddenly 'teleport' into an area, but rather they arrive one by one.  So this creates several possible scenarios:
```
bridgewatchbox1.composition(at=0, model='rec_vehicle').size==3 and bridgewatchbox1.composition(at=1, model='rec_vehicle').size==2 and
bridgewatchbox1.composition(at=2, model='rec_vehicle').size==1 and
bridgewatchbox1.composition(at=3, model='rec_vehicle').size==0
```
where objects arrive one by one.  Or,
```
bridgewatchbox1.composition(at=0, model='rec_vehicle').size==3 and bridgewatchbox1.composition(at=1, model='rec_vehicle').size==2 and
bridgewatchbox1.composition(at=2, model='rec_vehicle').size==0
```
where two vehicles arrive at the same time at the previous event, then one vehicle arrives at the most recent event.  You get the point - it is incredible tedious to try to write these ourselves.

This is why we have the GEN_PERMUTE() function - it generates all combinations for an attribute over time so all we have to do is express:
```
bridgewatchbox1.composition(at=0, model='rec_vehicle').size==3 and
bridgewatchbox1.composition(at=1, model='rec_vehicle').size==0
```
and GEN_PERMUTE() will handle generating all the necessary statements.

### Chaining atomic events and complex event operators together

So we can create more complex event sequences using the previously mentioned operators and atomic events:
```
ev_name.addEventSequence([ OR(event1, event2), GEN_PERMUTE(event3, "size"), AND(event4, event5)])
```
So let's go through this example, as if our program was executing it:
- First, we check if event1 or event2 occurs.  If either occurs, we can move onto the next event, which is GEN_PERMUTE().
- We check if any of the possible cases leading to event3 happens - these possible cases are generated based on the 'size' attribute.  If any of those cases occurs, we can move onto the next statement, which is AND(event4, event5).
- In the final case, we evaluate if both event4 and event5 occur, and both of them are true at the same time.  If so, our complex event is completed.

# Running the code

### Setup

First, check the 'requirements.txt'.  Use it to install the necessary packages.

### Execution

You can try evaluating some complex events by running:
```
python test_ce.py
```
This file includes a main function which demonstrates how one can evaluate a complex event given several files listing vicinal events.

