# import torch
import json
import os

# Antlr stuff
from antlr4 import *
from antlr4.tree.Trees import Trees
from antlr.languageLexer import languageLexer  # This is the lexer 
from antlr.language import language   # This is the parser
from nltk import Tree
from nltk.draw.tree import TreeView

# Our custom visitor
from ceVisitor import ceVisitor


def pretty_print(treestring):

    indents = treestring.split("(")

    p1 = treestring.count("(")
    p2 = treestring.count(")")

    print(p1)
    print(p2)

    # num_indents = 0
    # for x in indents:
    #     indent_string = '\t'*num_indents
    #
    #     print(indent_string + x)
    #
    #     if ")" in x:
    #         num_indents -= 1
    #     else:
    #         num_indents += 1

    # s = printtree + "\\"
    # s = printtree.replace(')', '\)').replace('(', '\(') # fix
    # print(treestring)
    nltk_tree = Tree.fromstring(treestring)

    TreeView(nltk_tree)._cframe.print_to_file('output.ps')
    os.system('convert output.ps output.png')


# def perform_inference():

#     # Model
#     model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=False)
#     model.load_state_dict(torch.load('multiV1_weights.pt'))['model'].state_dict()

#     # Images
#     imgs = ['output/image272.png']  # batch of images

#     # Inference
#     results = model(imgs)

#     # Results
#     results.print()


# Apply labelme to necessary locations
def label_locations(entity_locations):

    entity_location_names = list(entity_locations.keys())
    # For each entity location name
    for entity_location_name in entity_location_names:

        # Get the data, and label the image
        location_data = entity_locations[entity_location_name]

        if not os.path.exists(entity_locations[entity_location_name]["label_file"]):
            os.system("labelme --nodata " + location_data["image_file"])

        # # If this file doesn't exist, then call the labelme
        # if not os.path.exists(entity_locations[entity_location_name]["label_file"]):
        #     print("hi")
        # #    os.system("labelme ")

        


# Obtain all the entities involved in the event
def obtain_event_entities(event_str, entities):


    # First, check the locations and label them if necessary
    label_locations(entities["locations"])

    overall_entities = {}
    overall_entities.update(entities["locations"])
    overall_entities.update(entities["objects"])
    # overall_entities.update(entities["groups"])

    return overall_entities


# Extract the entities from an atomic event
def extract_entity_from_atomic_event(atomic_event):

    # First, find all starts of each variable
    entity_id_starts = [i for i, ltr in enumerate(atomic_event) if ltr == "@"]
    
    # For each '@' that we find, build the entity string until a non-alphanumeric
    #  character is found
    entity_names = []
    for id_start in entity_id_starts:
        current_name = []
        current_id = id_start+1
        current_letter = atomic_event[current_id]
        while current_letter.isalnum() or current_letter == "_":
            current_name.append(current_letter)
            current_id += 1
            current_letter = atomic_event[current_id]
        
        entity_names.append(''.join(current_name))

    return entity_names

# Get the bounding box for a location
def get_location_bounding_box(location_name, filepath):
    
    f = open(filepath)
    data = json.load(f)
    f.close()

    results = None
    # Iterate through the marked objects
    for location_data in data["shapes"]:
        
        if location_data["label"] == location_name:
            results = location_data["points"]
    
    return results




# Match an atomic event to a camera
def match_event_to_camera(atomic_events, json_entities):

    
    matched_events = []
    
    # Iterate through each atomic event, and decide which camera we need to map to.
    for atomic_event in atomic_events:
        
        # Figure out what entities are part of this event
        # First, extract the entities
        event_entities = extract_entity_from_atomic_event(atomic_event)

        atomic_event_request = {"operation" : atomic_event}
        # For each event entity, see if it is a location or object
        for event_entity in event_entities:
            
            if event_entity in json_entities["objects"]:

                # First, check the objects we are requesting.
                atomic_event_request.update({"object" : json_entities["objects"][event_entity]})

            elif event_entity in json_entities["locations"]:
                
                # Get the location we are looking for
                location_data = json_entities["locations"][event_entity]
                # Check if this is camera 1 or 2
                if "camera1" in location_data["image_file"]:
                    atomic_event_request.update({"camera_id" : "camera1"})
                else:
                    atomic_event_request.update({"camera_id" : "camera2"})
                
                # Then, get the bounding box for this location
                bbox_data = get_location_bounding_box(event_entity, location_data["label_file"])
                atomic_event_request.update({"location_bbox" : bbox_data})

        matched_events.append(atomic_event_request)
                
    return matched_events
        

# Send an event to a camera
def sendToCamera(matched_event):

    # STILL UNDER IMPLEMENTATION

    # Check which camera this event should go to
    if matched_event["camera_id"] == "camera1":
        print("sent to camera 1")
    elif matched_event["camera_id"] == "camera2":
        print("sent to camera 2")



# Parse the query
def parse_query(filepath="example_carla.json"):

    f = open(filepath)
    data = json.load(f)
    f.close()

    # Get all the entities
    entities = data["entities"]
    # Get the event
    event = data["event"]
    # Get all entities involved in the event
    obtain_event_entities(event, entities)

    input_text = InputStream(event)
    lexer = languageLexer(input_text)
    stream = CommonTokenStream(lexer)
    # parser
    parser = language(stream)
    tree = parser.expr()

    # Print tree
    printtree = Trees.toStringTree(tree, None, parser)
    # printtree = "(" + printtree
    pretty_print(printtree)

    # evaluator
    visitor = ceVisitor()

    # We have to split up the query and determine how to transmit it to each camera
    visitor.visit(tree)
    visitor.track_atomic_events = False # Stop tracking atomic events
    matched_events = match_event_to_camera(visitor.atomic_events, entities)

    # Now, here we need to transmit these events to different cameras
    for matched_event in matched_events:
        sendToCamera(matched_event)

    asdf

    test_input1 = [(i, 1) for i in range(1, 20)]
    test_input2 = [(i, 0) for i in range(21, 40)]
    test_input3 = [(i, 1) for i in range(41, 55)]
    test_input4 = [(i, 0) for i in range(56, 60)]
    test_input = test_input1 + test_input2 + test_input3 + test_input4

    # Output should be True for 11-21, 51-56, and False otherwise

    # Now, we run our evaluation.
    for val in test_input:

        print("\n\n next value:")
        visitor.addEvent(val)
        visitor.visit(tree)
        # The root node id is 0
        print(val)
        print(visitor.state_dict[0])


#  Some events to try out:
# "within[1KM](@rec_vehicle , @bridge1_watchbox)"
# "@rec_vehicle . type == 5"
# overlap(@rec_group, @bridge_watchbox1) and[10m, 10m] overlap(@rec_group, @bridge_watchbox2)
parse_query()