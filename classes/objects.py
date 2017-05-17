### obsolete module, functions are covered by elements.CElement

import bpy
import math

def importObject(data):
    bpy.ops.wm.link_append(directory=data['directory'], filename=data['filename'], link=data['link'])
    obj = bpy.data.objects[data['filename']]  
    if 'rotation' in data:
        obj.rotation_euler = [
            math.radians(data['rotation'][0]),
            math.radians(data['rotation'][1]),
            math.radians(data['rotation'][2])
        ]    
    if 'location' in data:
        obj.location = data['location']
    if 'name' in data:
        obj.name = data['name']
    return obj

def repeatObject(obj, data):
    array_mod = obj.modifiers.new('Repeater', 'ARRAY')
    array_mod.fit_type = data['type']
    if data['type'] == 'FIXED_COUNT':
        array_mod.count = data['count']
        
def test():
    data = {
        'name': 'Test Pole Array',
        'directory': "d:\\Projects\\Python\\Libs\\construction.blend\\Object\\",
        'filename': "Concrete Pole 150", 
        'link': False,
        'location': (-1, 5, -1.5),
        'rotation': [0,0,45],
        'repeat': 
            {
                'type': 'FIXED_COUNT',
                'count': 10,
            },
    }
    obj = importObject(data)
    repeatObject(obj, data['repeat'])
    

if __name__ == '__main__':
    test()

