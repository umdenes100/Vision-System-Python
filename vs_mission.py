
# return the proper mission message based on mission type and curr index of mission value 
def get_mission_message(mission_type, mission, msg):
    print(f'mission attributes: {mission_type} --- {mission} --- {msg}')
    try:
        msg = int(msg.decode())
    except:
        return "ERROR - invalid mission call"

    if mission == "CRASH_SITE":
        mission = 0
    elif mission == "DATA":
        mission = 1
    elif mission == "MATERIAL":
        mission = 2
    elif mission == "FIRE":
        mission = 3
    elif mission == "WATER":
        mission = 4
    else:
        mission = -1


    ret_msg = ''
    if mission == 0: # Crash Site
        if mission_type == 0: # DIRECTION
            ret_msg += "The direction of the abnormality is in the "
            if msg == 0:
                ret_msg += "+x"
            elif msg == 1:
                ret_msg += "-x"
            elif msg == 2:
                ret_msg += "+y"
            elif msg == 3:
                ret_msg += "-y"
            else:
                ret_msg += "?????"
            ret_msg += " direction."
        elif mission_type == 1: # LENGTH
            ret_msg += f"The length of the side with abnormality is {msg}mm."
        elif mission_type == 2: # HEIGHT
            ret_msg += f"The height of the side with abnormality is {msg}mm."
        else:
            ret_msg += "Not a valid mission type!"
    
    elif mission == 1: # Data
        if mission_type == 0: # DUTY CYCLE
            ret_msg += f"The duty cycle is {msg}%."
        elif mission_type == 1: # MAGNETISM
            ret_msg += "The disk is "
            if msg == 0:
                ret_msg += "MAGNETIC"
            elif msg == 1:
                ret_msg += "NOT MAGNETIC"
            else:
                ret_msg += "?????"
            ret_msg += "."
        else:
            ret_msg += "Not a valid mission type!"

    elif mission == 2: # Material
        if mission_type == 0: # WEIGHT
            ret_msg += "The weight of the material is "
            if msg == 0:
                ret_msg += "HEAVY"
            elif msg == 1:
                ret_msg += "MEDIUM"
            elif msg == 2:
                ret_msg += "LIGHT"
            else:
                ret_msg += "?????"
            ret_msg += "."
        elif mission_type == 1: # SQUISHABILITY
            ret_msg += "The material is "
            if msg == 0:
                ret_msg += "SQUISHY"
            elif msg == 1:
                ret_msg += "NOT SQUISHY"
            else:
                ret_msg += "?????"
            ret_msg += "."
        else:
            ret_msg += "Not a valid mission type!"

    elif mission == 3: # Fire
        if mission_type == 0: # NUM_CANDLES
            ret_msg += f"The number of candles alit is {msg}."
        elif mission_type == 1: # TOPOGRAPHY
            ret_msg += "The topography of the fire mission is: "
            if msg == 0:
                ret_msg += "A"
            elif msg == 1:
                ret_msg += "B"
            elif msg == 2:
                ret_msg += "C"
            else:
                ret_msg += "?????"
        else:
            ret_msg += "Not a valid mission type!"

    elif mission == 4: # Water
        if mission_type == 0: # DEPTH
            ret_msg += f"The depth of the water is {msg}mm."
        elif mission_type == 1: # WATER_TYPE
            ret_msg += "The water is "
            if msg == 0:
                ret_msg += "FRESH and UNPOLLUTED."
            elif msg == 1:
                ret_msg += "FRESH and POLLUTED"
            elif msg == 2:
                ret_msg += "SALTY and UNPOLLUTED"
            elif msg == 3:
                ret_msg += "SALTY and POLLUTED"
            else:
                ret_msg += "?????"
        else:
            ret_msg += "Not a valid mission type!"
    
    else:
        ret_msg = f"ERROR - invalid mission type ({mission})"

    return ret_msg + '\n'

