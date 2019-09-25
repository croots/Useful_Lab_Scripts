"""
Generates a nice looking thermocycler program schematic for input into a lab notebook or presentation
Requires python 3ish, PILLOW, NUMPY
Example input at bottom of file. You will probably have to alter the image saving feature to fit your filesystem.

@author: croots
@version: 0.1
"""

import PIL
from PIL import ImageDraw
from IPython.display import Image, display
import numpy as np
import hashlib

def pcr_image(program):
    # Decode String
    program_string = program
    program = program.split(" ")
    encoded_program = {}
    encoded_program["1"] = {}
    current_subprogram = 1
    subprograms = 1
    for step in program:
        if "" is step:
            continue
        elif "/" in step:
            if "cycles" not in encoded_program[f"{current_subprogram}"].keys():
                encoded_program[f"{current_subprogram}"] = {}
                encoded_program[f"{current_subprogram}"]["cycles"] = 1
                encoded_program[f"{current_subprogram}"]["steps"] = []
            encoded_program[f"{current_subprogram}"]["steps"].append(step.split("/"))
            continue
        elif "[" in step or "]" in step:
            if "cycles" in encoded_program[f"{current_subprogram}"].keys():
                current_subprogram += 1
                subprograms += 1
                encoded_program[f"{current_subprogram}"] = {}
            if "[" in step:
                try:
                    encoded_program[f"{current_subprogram}"] = {}
                    encoded_program[f"{current_subprogram}"]["cycles"] = int(step[:-1])
                    encoded_program[f"{current_subprogram}"]["steps"] = []
                    continue
                except:
                    pass
            elif "]" is step:
                continue
        raise ValueError(f"Unrecognized Step {step}.")
    # Clean up if the last subprogram has no steps
    if "cycles" not in encoded_program[f"{subprograms}"].keys():
        del(encoded_program[f"{subprograms}"])
    # Find unique temperatures
    unique_temperatures = []
    for sub_program in encoded_program:
        for step in encoded_program[f"{sub_program}"]["steps"]:
            if step[0] not in unique_temperatures:
                unique_temperatures.append(step[0])
    ordered_temperatures = []
    if len(unique_temperatures) > 1:
        for temperature in unique_temperatures:
            for i, ordered_temperature in enumerate(ordered_temperatures):
                if int(temperature) > int(ordered_temperature):
                    ordered_temperatures = ordered_temperatures[:i] + [temperature] + ordered_temperatures[i:]
                    continue
            if temperature not in ordered_temperatures:
                ordered_temperatures.append(temperature)
    else:
        ordered_temperatures = unique_temperatures
    ordered_temperatures=tuple(ordered_temperatures)
    # Draw Image
    imgwidth = 700
    imgheight = 70+25*ordered_temperatures.index(step[0])
    img = PIL.Image.new('RGB', (imgwidth, imgheight), color = 'white')
    pcr_diagram = PIL.ImageDraw.Draw(img)
    current_position = [0,5]
    line_ends = []
    text_color = (50,50,50)
    line_color = (150,150,150)
    for i, sub_program in enumerate(encoded_program):
        if i != 0:
            pcr_diagram.line((current_position[0]-5, 0) + (current_position[0]-5, imgheight), fill=line_color)
        pcr_diagram.text((current_position[0],0),
                         f"{encoded_program[f'{sub_program}']['cycles']}x",
                         fill=text_color)
        current_position[0] -= 30
        for step in encoded_program[f"{sub_program}"]["steps"]:
            current_position[0] += 50
            pcr_diagram.text((current_position[0]+5,current_position[1]+25+25*ordered_temperatures.index(step[0])),
                         f"{step[0]}",
                         fill=text_color)
            line_ends.append([current_position[0]-8,current_position[1]+38+25*ordered_temperatures.index(step[0])])
            line_ends.append([current_position[0]+30,current_position[1]+38+25*ordered_temperatures.index(step[0])])
            pcr_diagram.text((current_position[0],current_position[1]+42+25*ordered_temperatures.index(step[0])),
                         f"{step[1]}",
                         fill=text_color)
        current_position[0] += 50
    for i, line_end in enumerate(line_ends[1:]):
        pcr_diagram.line((line_ends[i][0], line_ends[i][1]) + (line_end[0], line_end[1]), fill=line_color)
    program_hash = hashlib.md5(program_string.encode("UTF-8")) 
    img.save(f"pcr_images/{program_hash.hexdigest()}.png")
    display(Image(filename=f"pcr_images/{program_hash.hexdigest()}.png"))
    print(f"Image saved as pcr_images/{program_hash.hexdigest()}.png")

pcr_image("98/2:00 35[ 98/0:10 66/0:30 72/1:15 ] 72/10:00 4/0:00")
