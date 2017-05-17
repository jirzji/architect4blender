import bpy
import os
import json
from enum import Enum
import math
from mathutils import Vector
#import utilities
import elements
import architecture
import walls
from lists import CItemList

class CPane(elements.CGeometry):
    def __init__(self, element, owner, depth = 0.05, indent=0):
        super(CPane,self).__init__(element)
        self.owner = owner
        self.depth = depth
        self.indent = indent
    def _build(self):
        print("CPane._build")
        vertIndex = self.element.vertices.count()
        for i, p in enumerate(self.owner.inner):
            self.element.vertices.add((p[0],self.indent, p[1]))
            self.element.vertices.add((p[0],self.indent+self.depth, p[1])) 
            
        count = 4*2
        refIndex = 0
        for p in self.owner.inner:    
            self.element.faces.add((vertIndex+refIndex+1, vertIndex+refIndex, vertIndex+(refIndex+2)%count, vertIndex+(refIndex+3)%count))
            refIndex += 2
        
        self.element.faces.add((vertIndex, vertIndex+6, vertIndex+4, vertIndex+2))
        self.element.faces.add((vertIndex+1, vertIndex+3, vertIndex+5, vertIndex+7))
    def fromData(self, data):
        if "depth" in data:
            self.depth = data["depth"]
        if "indent" in data:
            self.indent = data["indent"]

class CFrame(elements.CGeometry):
    def __init__(self, element, owner, thickness = 0.05, depth = 0.05, indent=0):
        super().__init__(element)
        self.owner = owner
        self.thickness = thickness
        self.depth = depth
        self.indent = indent
        self.divisions = CDivisions(element, self)
        self.pane = None
    def insertPane(self, depth = None, indent=None):
        if depth == None:
            depth = self.depth/2
        if indent == None:
            indent = self.depth/4
        if self.pane == None:
            self.pane = CPane(self.element, self, depth, indent)
        else:
            self.pane.depth = depth
            self.pane.indent = indent
        return self
    def clear(self):
        del self.divisions
        self.divisions = CDivisions(self.element, self)
    def _build(self):
        print("CFrame._build")
        corners = [(1,1), (1,-1), (-1,-1),(-1,1)]
        vertIndex = self.element.vertices.count()

        for i, p in enumerate(self.owner.inner):
            c = corners[i]
            self.element.vertices.add((p[0],self.indent, p[1]))
            self.element.vertices.add((p[0],self.indent+self.depth, p[1])) 
            self.element.vertices.add((p[0]+self.thickness*c[0],self.indent, p[1]+self.thickness*c[1]))
            self.element.vertices.add((p[0]+self.thickness*c[0],self.indent+self.depth, p[1]+self.thickness*c[1]))
            
        count = 4*4
        refIndex = 0
        for c in corners:    
            self.element.faces.add((vertIndex+refIndex+1, vertIndex+refIndex, vertIndex+(refIndex+4)%count, vertIndex+(refIndex+5)%count))
            self.element.faces.add((vertIndex+refIndex, vertIndex+refIndex+2, vertIndex+(refIndex+6)%count, vertIndex+(refIndex+4)%count))
            self.element.faces.add((vertIndex+refIndex+2, vertIndex+refIndex+3, vertIndex+(refIndex+7)%count, vertIndex+(refIndex+6)%count))
            self.element.faces.add((vertIndex+refIndex+3, vertIndex+refIndex+1, vertIndex+(refIndex+5)%count, vertIndex+(refIndex+7)%count))

            refIndex += 4
            
        self.inner = []    
        for i, p in enumerate(self.owner.inner):
            c = corners[i]
            self.inner.extend([(p[0]+self.thickness*c[0], p[1]+self.thickness*c[1])])
            
        self.divisions._build()
        
        if self.pane != None:
            self.pane._build()
    def fromData(self, data):
        print("CFrame.fromData", data)
        if "pane" in data:
            self.insertPane()
            self.pane.fromData(data["pane"])
        if "divisions" in data:
            self.divisions.fromData(data["divisions"])
        
class CDoorFrame(CFrame):
    def _build(self):
        print("CDoorFrame._build")
        corners = [(1,0), (1,-1), (-1,-1),(-1,0)]
        count = 4*4
        vertIndex = self.element.vertices.count()

        for i, p in enumerate(self.owner.inner):
            c = corners[i]
            self.element.vertices.add((p[0],self.indent, p[1]))
            self.element.vertices.add((p[0],self.indent+self.depth, p[1])) 
            self.element.vertices.add((p[0]+self.thickness*c[0],self.indent, p[1]+self.thickness*c[1]))
            self.element.vertices.add((p[0]+self.thickness*c[0],self.indent+self.depth, p[1]+self.thickness*c[1]))
            
        refIndex = 0
        for i in range(0, 3):    
            self.element.faces.add((vertIndex+refIndex+1, vertIndex+refIndex, vertIndex+(refIndex+4)%count, vertIndex+(refIndex+5)%count))
            self.element.faces.add((vertIndex+refIndex, vertIndex+refIndex+2, vertIndex+(refIndex+6)%count, vertIndex+(refIndex+4)%count))
            self.element.faces.add((vertIndex+refIndex+2, vertIndex+refIndex+3, vertIndex+(refIndex+7)%count, vertIndex+(refIndex+6)%count))
            self.element.faces.add((vertIndex+refIndex+3, vertIndex+refIndex+1, vertIndex+(refIndex+5)%count, vertIndex+(refIndex+7)%count))

            refIndex += 4
            
        self.inner = []    
        for i, p in enumerate(self.owner.inner):
            c = corners[i]
            self.inner.extend([(p[0]+self.thickness*c[0], p[1]+self.thickness*c[1])])
            
        self.divisions._build()

class CDivision(elements.CGeometry):
    def __init__(self, list, element, owner, size=100):
        self.list = list
        self.owner = owner
        self.element = element
        self.size = size
        
        self.thickness = list.thickness
        self.depth = list.depth
        self.indent = list.indent

        self.divisions = None
        self.frame = None
        self.pane = None
    def insertDivisions(self, direction=None, thickness = None, depth = None, indent=0):
        if direction == None:
            if self.list.direction == "HORIZONTAL":
                direction = "VERTICAL"
            if self.list.direction == "VERTICAL":
                direction = "HORIZONTAL"
        self.divisions = CDivisions(self.element, self, direction, thickness, depth, indent)
        del self.frame
        self.frame = None
        return self.divisions
    def insertFrame(self,thickness = None, depth = None, indent=None):
        if thickness == None:
            thickness = self.thickness
        if depth == None:
            depth = self.depth
        if indent == None:
            indent = self.indent
        self.frame = CFrame(self.element, self, thickness, depth, indent)
        del self.divisions
        self.divisions = None
        return self.frame
    def insertPane(self, depth = None, indent=None):
        if depth == None:
            depth = self.depth/2
        if indent == None:
            indent = self.depth/4
        self.pane = CPane(self.element, self, depth, indent) 
        return self
    def _build(self):
        print("CDivision._build")
        minX = self.owner.inner[0][0]
        maxX = self.owner.inner[3][0]
        minZ = self.owner.inner[0][1]
        maxZ = self.owner.inner[1][1]
        minY = self.indent
        maxY = self.indent + self.depth

        vertIndex = self.element.vertices.count()
        
        if self.list.direction == 'HORIZONTAL':
            position = (maxX-minX)/100*self.size+minX
            t = self.thickness/2

            if (self.size < 100):
                self.element.vertices.add((position-t, minY, minZ))
                self.element.vertices.add((position+t, minY, minZ))
                self.element.vertices.add((position-t, minY, maxZ))
                self.element.vertices.add((position+t, minY, maxZ))
                self.element.vertices.add((position-t, maxY, minZ))
                self.element.vertices.add((position+t, maxY, minZ))
                self.element.vertices.add((position-t, maxY, maxZ))
                self.element.vertices.add((position+t, maxY, maxZ))

                self.element.faces.add((vertIndex+0, vertIndex+1, vertIndex+3, vertIndex+2))
                self.element.faces.add((vertIndex+1, vertIndex+5, vertIndex+7, vertIndex+3))
                self.element.faces.add((vertIndex+5, vertIndex+4, vertIndex+6, vertIndex+7))
                self.element.faces.add((vertIndex+4, vertIndex+0, vertIndex+2, vertIndex+6))
                
                self.inner = [
                    (self.list.lastPosition,minZ),
                    (self.list.lastPosition,maxZ),
                    (position-t,maxZ),
                    (position-t,minZ),
                ]
            else:
                self.inner = [
                    (self.list.lastPosition,minZ),
                    (self.list.lastPosition,maxZ),
                    (position,maxZ),
                    (position,minZ),
                ]
                
        if self.list.direction == 'VERTICAL':
            position = (maxZ-minZ)/100*self.size+minZ
            t = self.thickness/2

            if (self.size < 100):
                self.element.vertices.add((minX, minY, position+t))
                self.element.vertices.add((minX, minY, position-t))
                self.element.vertices.add((maxX, minY, position+t))
                self.element.vertices.add((maxX, minY, position-t))
                self.element.vertices.add((minX, maxY, position+t))
                self.element.vertices.add((minX, maxY, position-t))
                self.element.vertices.add((maxX, maxY, position+t))
                self.element.vertices.add((maxX, maxY, position-t))

                self.element.faces.add((vertIndex+0, vertIndex+1, vertIndex+3, vertIndex+2))
                self.element.faces.add((vertIndex+1, vertIndex+5, vertIndex+7, vertIndex+3))
                self.element.faces.add((vertIndex+5, vertIndex+4, vertIndex+6, vertIndex+7))
                self.element.faces.add((vertIndex+4, vertIndex+0, vertIndex+2, vertIndex+6))
                
                self.inner = [
                    (minX,self.list.lastPosition),
                    (minX,position-t),
                    (maxX,position-t),
                    (maxX,self.list.lastPosition),
                ]
            else:
                self.inner = [
                    (minX,self.list.lastPosition),
                    (minX,position),
                    (maxX,position),
                    (maxX,self.list.lastPosition),
                ]
        
        if self.frame != None:
            self.frame._build()
        if self.divisions != None:
            self.divisions._build()
        
        return position+t
    def fromData(self, data):
        print("CDivision.fromData", data)
        if "frame" in data:
            self.insertFrame()
            self.frame.fromData(data["frame"])
        if "pane" in data:
            self.insertPane()
            self.pane.fromData(data["pane"])
        if "divisions" in data:
            self.insertDivisions()
            self.divisions.fromData(data["divisions"])
    
class CDivisions(CItemList):
    def __init__(self, element, owner, direction='HORIZONTAL', thickness=None, depth=None, indent=0):
        self.direction = direction
        self.element = element
        self.owner = owner
        self.configure(thickness, depth, indent)        
    def configure(self, thickness=None, depth=None, indent=0):    
        if thickness == None:
            thickness = self.owner.thickness
        if depth == None:
            depth = self.owner.depth
            
        self.thickness = thickness
        self.depth = depth
        
        self.indent = self.owner.indent+indent
    def add(self, size=100):
        division = CDivision(self, self.element, self.owner, size)
        super().add(division)
        return division
    def divide(self, number):
        self.clear()
        for i in range(1, number+1):
            self.add(i*100/number)
        return self
    def _build(self):
        print("CDivisions._build", self.count())
        if self.direction == "HORIZONTAL":
            self.lastPosition = self.owner.inner[0][0]
        if self.direction == "VERTICAL":
            self.lastPosition = self.owner.inner[0][1]
        for d in self:
            self.lastPosition = d._build()
    def fromData(self, data):
        print("CDivisions.fromData", data)
        if "direction" in data:
            self.direction = data["direction"]
        self.clear()
        if "items" in data:
            for item in data["items"]:
                division = self.add(item["size"])
                division.fromData(item)

class CWallInfo():
    def __init__(self, wall, hole, componentIndex, angle):
        self.wall = wall
        self.hole = hole
        self.componentIndex = componentIndex
        self.angle = angle

###############################################################################################################

class CJoinery(architecture.CElement):
    def __init__(self, name='Joinery', height=1, width=1, cloneFrom=None):
        if cloneFrom == None:
            self.height = height
            self.width = width
        self.frame = CFrame(self, self)
        self.wallInfo = None
        super().__init__(name=name, cloneFrom = cloneFrom)

    def link(self, aJoinery):
        self.height = aJoinery.height
        self.width = aJoinery.width
        del self.frame
        self.frame = aJoinery.frame

    def _buildMesh(self):
        print("CJoinery._buildMesh")
        self.inner = [(0,0), 
            (0,self.height), 
            (self.width,self.height), 
            (self.width,0)]
        self.frame._build()

    def _applyModifiers(self):
        if self.wallInfo != None:
            wallLocation = self.wallInfo.wall.getLocation()
            self.locate(wallLocation)
            print("self.wallInfo.hole.origins=",self.wallInfo.hole.origins)
            print("self.wallInfo.componentIndex=",self.wallInfo.componentIndex)
            translation = Vector(self.wallInfo.hole.origins[self.wallInfo.componentIndex]) - Vector(wallLocation)
            self.translate(translation)
            self.rotate(0,0,self.wallInfo.angle+180)

    def insertInWall(self, wall, sectionIndex = 0, componentIndex = 0, position = (0,0)):
        if self.wallInfo != None:
            del self.wallInfo
        reveal = wall.components[componentIndex].reveal
        hole = wall.sections[sectionIndex].holes.add(position=position, dimensions=(self.width-reveal*2,self.height-reveal))
        self.wallInfo = CWallInfo(wall, hole, componentIndex, wall.sections[sectionIndex].angle)
        self.setParent(wall)
        wall.update()
    
class CWindow(CJoinery):
    def __init__(self, name='Window', height=1, width=1, cloneFrom = None):
        super().__init__(name, height, width, cloneFrom)
    
#    def _initProperties(self):
#        print('CWindow._initProperties')
#        props = bpy.context.scene.windowProperties.add()
#        props.wallInfo.component = 0
#        props.wallInfo.section = 0
#        props.wallInfo.distance = 0
#        props.wallInfo.base = 0       
#        props.name = str(id(self._object))
#        return props
#    
#    @property
#    def _properties(self):
#        return bpy.context.scene.windowProperties[str(id(self._object))]

#    @staticmethod
#    def isWindow(obj):
#        name = str(id(obj))
#        return name in bpy.context.scene.windowProperties
#    
#    def _applyType(self, type):
#        directory = os.path.join(os.path.dirname(__file__), 'img/windows/types')       
#        filepath = os.path.join(directory, type+'.json')
#        file_handle = open(filepath, "r")
#        data = json.load(file_handle)
#        if "frame" in data: 
#            self.frame.fromData(data["frame"])

#    def _syncAttrToProps(self):
#        self._properties.syncing = True
#        self._properties.height = self.height
#        self._properties.width = self.width
#        if self.wallInfo != None:
#            self._properties.wallInfo.component = self.wallInfo.component
#            self._properties.wallInfo.section = self.wallInfo.section
#            self._properties.wallInfo.distance = self.wallInfo.position[0]
#            self._properties.wallInfo.base = self.wallInfo.position[1]
#        else:
#            self._properties.wallInfo.component = 0
#            self._properties.wallInfo.section = 0
#            self._properties.wallInfo.distance = 0
#            self._properties.wallInfo.base = 0
#        self._properties.syncing = False

#    def _syncPropsToAttr(self):
#        print("CWindow._syncPropsToAttr")

#        self._properties.syncing = True
#        self.width = self._properties.width
#        self.height = self._properties.height
#        
#        self._applyType(self._properties.type)
#        if self._properties.wallInfo.wall != "-":
#            self.insertInWall()

#        self._properties.syncing = False
#    
class CDoor(CJoinery):
    def __init__(self, name='Door', height=1, width=1):
        super().__init__(name, height, width)
        self.frame = CDoorFrame(self, self)
    
def test():
    
    print("*** START ***")
    
    data = {
        'height': 1.65,
        'width': 2.50,
        'colors': [(0.04,0.007,0.002), (0.4,0.4,1)],
        'materials': ['glass', 'glass'],
        'frame': 
        {
            'thickness': 0.05,
            'depth': 0.05,
            'divisions':
            {
                'direction': 'vertical',
                'items': [
                            {'size': 80, 'thickness': 0.07, 
                             'divisions': 
                                {
                                    'items': [
                                        {'size': 33.3, 'thickness': 0.04,
                                         'frame':
                                            {
                                                'thickness': 0.05,
                                                'depth': 0.05,
                                                'indent': 0.02
                                            }
                                        }, 
                                        {'size': 67, 'thickness': 0.04,
                                        }, 
                                        {'size': 100, 'thickness': 0.04,
                                         'frame':
                                            {
                                                'thickness': 0.05,
                                                'depth': 0.05,
                                                'indent': 0.02
                                            }
                                        }, 
                                             ]
                                },
                            },
                            {'size': 100, 'thickness': 0.04, 
                             'divisions': 
                                {
                                    'items': [
                                        {'size': 11.1, 'thickness': 0.04,
                                        }, 
                                        {'size': 22.2, 'thickness': 0.04,
                                        }, 
                                        {'size': 33.3, 'thickness': 0.04,
                                        }, 
                                        {'size': 44.4, 'thickness': 0.04,
                                        }, 
                                        {'size': 55.5, 'thickness': 0.04,
                                        }, 
                                        {'size': 66.6, 'thickness': 0.04,
                                        }, 
                                        {'size': 77.7, 'thickness': 0.04,
                                        }, 
                                        {'size': 88.8, 'thickness': 0.04,
                                        }, 
                                        {'size': 100, 'thickness': 0.04,
                                        }, 
                                             ]
                                },
                            },
                         ]
            }

        },
    }
    #createWindowDoor(data)
    
    wall = walls.CWall()
    wall.addColor((1,1,1))
    wall.addColor((1,1,0.6))
    wall.components.add(height=2.81,thickness=0.10,color=0)
    wall.components.add(height=2.81,thickness=0.05,reveal=0.025,type='CAVITY')
    wall.components.add(height=2.61,thickness=0.15,elevation=0.1,reveal=0.025,color=1)
    wall.sections.add(4.5,0)
    wall.locate(3,0,0)
    
    joinery = CJoinery()
    joinery.addColor((0.2,0.3,0.2))
    joinery.width = 2.5
    joinery.heigh = 1.5
    joinery.frame.thickness = 0.08
    joinery.frame.divisions.direction = 'VERTICAL'
    joinery.frame.insertPane(depth=0.01)
    
    div = joinery.frame.divisions.add(85)
    div.insertDivisions().divide(3)
    xdiv = div.divisions[0].insertFrame(0.05,0.05,0.01).divisions
    xdiv.thickness = 0.02
    xdiv.depth = 0.03
    xdiv.indent = 0.02
    xdiv.divide(2)
    xdiv[0].insertDivisions(thickness = 0.02, depth=0.03, indent=0).divide(2)
    xdiv[1].insertDivisions(thickness = 0.02, depth=0.03, indent=0).divide(2)
    
    xdiv = div.divisions[1].insertDivisions(thickness = 0.02, depth=0.03, indent=0)
    xdiv.divide(2)
    xdiv[0].insertDivisions().divide(2)
    xdiv[1].insertDivisions().divide(2)

    xdiv = div.divisions[2].insertFrame(0.05,0.05,0.01).divisions
    xdiv.thickness = 0.02
    xdiv.depth = 0.03
    xdiv.indent = 0.02
    xdiv.divide(2)
    xdiv[0].insertDivisions(thickness = 0.02, depth=0.03, indent=0).divide(2)
    xdiv[1].insertDivisions(thickness = 0.02, depth=0.03, indent=0).divide(2)

    div = joinery.frame.divisions.add(100)
    div.insertDivisions(thickness = 0.02, depth=0.03, indent=0.01).divide(9)
    
    joinery.insertInWall(wall,0,1,(1,0.7))
    wall.update()
    joinery.update()

if __name__ == '__main__':
    test()
