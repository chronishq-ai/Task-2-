from core.confidence_handler import confidence_weighted_update
from core.config_loader import load_state_schema


schema = load_state_schema()


current_state = {

    "mood":8,
    "stress":3,
    "confidence":7

}


event_signal = {

    "mood":{
        "value":3,
        "confidence":0.8
    },


    "stress":{
        "value":8,
        "confidence":0.9
    }

}



for variable, signal in event_signal.items():

    speed = schema["variables"][variable]["speed"]


    current_state[variable] = confidence_weighted_update(

        current_state[variable],

        signal["value"],

        speed,

        signal["confidence"]

    )



print(current_state)