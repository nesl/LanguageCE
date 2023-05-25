# Introduction

TBD 

# Language Semantics

TBD: Defining CE and AE 


# Language Usage

## How do we express statements?


### Setting up a Complex Event

First, we have to set up complex events.  The complexEvent class is responsible for executing our symbolic logic.  The initialization takes no parameters.
```
ce_name = complexEvent()
```

### Adding Watchboxes

Next, we have to set up our spatial detection features, such as watchboxes.  These take the following format:
```
ce_name.addWatchbox("XX = watchbox('YY', positions=[aa,bb,cc,dd], id=ZZ)")
```
Here, XX is the name of our watchbox which can be referenced in later events.  YY is the camera stream name, although at this time it doesn't do anything.  The positions of aa,bb,cc,dd refer to the top left and bottom right coordinates of the watchbox in the image.  The id of ZZ is an integer number which corresponds to the events returned by the neural components (e.g. camera + YOLOv5 + some additional processing).  An example of these returned events is shown in complex_events.json:
```
{"camera_id": 3, "results": [[[0], [true], 1]], "time": 630}
```
As you can see, this entry in complex_events.json contains a camera_id which we currently don't use.  In addition, it has a 'results field', which refers to the following:
```
"results": [[[watchbox_id], [event_occurred], object_track_id]]
```
This means that we only get results when an object enters a watchbox or exits the watchbox.  Moreover, the 'watchbox_id' corresponds to the 'id=ZZ' statement we used previously in addWatchbox.

### Adding Atomic Events

To add an event we can simply use the following syntax:
```
event_name = Event("WATCHBOX_NAME.composition(at=EVENT_INDEX, model=VEHICLE_CLASS).ATTRIBUTE==CC")
```
where WATCHBOX_NAME refers to the name of our watchbox declared previously (e.g. XX).  The '.composition()' takes several parameters:

at=EVENT_INDEX, which refers to the current and previous events occurring in this watchbox.  Importantly, the order of time is reversed: at=0 refers to the current time, while at=1 refers to the previous event, and at=2 refers to the previous to previous event, etc.

model=VEHICLE_CLASS refers to the name of the vehicle class we want the watchbox to filter for.  In the current implementation it is not used internally yet.

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
ev1 = Event("bridgewatchbox1.composition(at=0, model='rec_vehicle').size==3") and
bridgewatchbox1.composition(at=1, model='rec_vehicle').size==0
```
and GEN_PERMUTE() will handle generating all the necessary statements.

### Chaining atomic events and complex event operators together

So we can create more complex event sequences using the previously mentioned operators and atomic events:
```
ev_name.addEventSequence([ OR(event1, event2), GEN_PERMUTE(event3, "size"), AND(event4, event5)])
```

```
ce1.addEventSequence([ OR(event1, event2), WITHIN(event3, event4, 300), AND(event5, event6)])
```
So let's go through this example, as if our program was executing it:
- First, we check if event1 or event2 occurs.  If either occurs, we can move onto the next event, which is GEN_PERMUTE().
- We check if any of the possible cases leading to event3 happens - these possible cases are generated based on the 'size' attribute.  If any of those cases occurs, we can move onto the next statement, which is AND(event4, event5).
- In the final case, we evaluate if both event4 and event5 occur, and both of them are true at the same time.  If so, our complex event is completed.

# Running the code

### Setup

First, check the 'requirements.txt'.  Use it to install the necessary packages.

### Execution

#### Running the ChatGPT examples:

First, please change the value of the variable "openai.api_key" in chatgpt_frontend.py to your API key.
```
python chatgpt_frontend.py
```

You have several ways of communicating with ChatGPT via this file:
- Selecting a predefined message based on a file under chatgpt_examples
    The selected file is from the variable "file_of_interest", and you can use a number to select one of the json entries.  0 is the preamble, and 1+ is usually a query based on the preamble (e.g. create an event).  An example interaction is shown below.
```
Select a message option (0-N), or type it here:0
ChatGPT: Yes, I am ready. How can I help you?
Select a message option (0-N), or type it here:2
```
- Another way of communicating is just to type your query in the input.
```
Select a message option (0-N), or type it here:0
ChatGPT: Yes, I am ready. How can I help you?
Select a message option (0-N), or type it here:2
```
Select a message option (0-N), or type it here: what is the tallest building in the world?
ChatGPT: As of 2021, the tallest building in the world is the Burj Khalifa, located in Dubai, United Arab Emirates. It stands at a height of 828 meters (2,716 feet) with 163 floors.
```

#### Todos:

TBD - need to create a sample AE generator.

