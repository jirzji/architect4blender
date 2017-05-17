import bpy
import math
import mathutils
import architecture
import elements
from  lists import CItemList
        
class CWallHole():
    def __init__(self, position=(0,0), dimensions=(0,0), componentsToDrill='ALL'):
        self.position = position
        self.dimensions = dimensions
        self.componentsToDrill = componentsToDrill
        self.origins = []

class CWallHoles(CItemList):
    def add(self, position=(0,0), dimensions=(0,0), componentsToDrill='ALL'):
        return super(CWallHoles,self).add(CWallHole(position, dimensions, componentsToDrill))

class CWallCornerFillet():
    def __init__(self, corner, dimensions):
        self.corner = corner
        self.dimensions = dimensions

class CWallCornerFillets(CItemList):
    def add(self, corner, dimensions = (0,0)):
        super(CWallCornerFillets,self).add(CWallCornerFillet(corner, dimensions))

class CWallComponent():
    def __init__(self, height=0, thickness=0, reveal=0, elevation=0, type = 'WALL', color=0):
        self.type = type
        self.reveal = reveal
        self.elevation = elevation
        self.height = height
        self.thickness = thickness
        self.color = color
        
class CWallComponents(CItemList):
    def add(self, height=0, thickness=0, reveal=0, elevation=0, type = 'WALL', color=0):                      
        print("CWallComponents.add")
        return super(CWallComponents,self).add(CWallComponent(height, thickness, reveal, elevation, type, color))

    def getOffset(self, index):
        result = 0
        for component in range(0, index):
            result += self[component].thickness
        return result
    def count(self, type='ANY'):
        if type == 'ANY':
            result = super(CWallComponents,self).count()
        else:
            result = 0
            for item in self:
                if item.type == type:
                    result += 1
        return result
                
class CWallSectionFootPrint():
    def __init__(self, outerHead = (0,0,0), outerTail = (0,0,0), innerHead = (0,0,0), innerTail = (0,0,0)):
        self.outerHead = outerHead
        self.outerTail = outerTail
        self.innerHead = innerHead
        self.innerTail = innerTail
        
class CWallSection():
    def __init__(self, length=0, angle=0, inclination=0, close=True):
        self.length = length
        self.angle = angle
        self.inclination = inclination
        self.close = close
        self.headAngle = 0
        self.tailAngle = 0
        self.holes = CWallHoles(self)
        self.cornerFillets = CWallCornerFillets(self)
        self.footPrint = CWallSectionFootPrint()
    def reshape(self, type='REGULAR'):
        if type=='GABLE':
            self.cornerFillets.add('HEAD_TOP', (self.list.parent.getHeight(),self.length/2))
            self.cornerFillets.add('TAIL_TOP', (self.list.parent.getHeight(),self.length/2))

class CWallSections(CItemList):
    def add(self, length=0, angle=0, inclination=0, close=True):
        print("CWallSections.add")
        return super(CWallSections,self).add(CWallSection(length, angle, inclination, close))

    def _getPreviousSection(self, index):
        return self.get((index-1+self.count())%self.count())
    def _getNextSection(self, index):
        return self.get((index-1+self.count())%self.count())
    def _calcHeadTailAngles(self, index):
        section = self.get(index)
        sectionCount = self.count()
        prevSection = self.get((index-1+sectionCount)%sectionCount)
        nextSection = self.get((index+1)%sectionCount)
        if ((index==0) and (not self.parent.close)):
            section.headAngle = 0
        else:
            section.headAngle = ((prevSection.angle - section.angle)/2 + 180)%180
        if ((index == sectionCount-1) and (not self.parent.close)):
            section.tailAngle = 0
        else:
            section.tailAngle = ((nextSection.angle - section.angle)/2 - 180)%(-180)
  
class CWallLeaf(elements.CGeometry):
    def __init__(self, element, offset, component, section):
        super(CWallLeaf,self).__init__(element)
        self.offset = offset
        self.component = component
        self.section = section
        
    def _addHead(self): 
        print ('CWallLeaf.addHead')
    
        r = math.tan(math.radians(self.section.headAngle)) * self.offset
        a = math.radians(self.section.angle)
        x0 = math.sin(a) * self.offset + math.cos(a) * r
        y0 = - math.cos(a) * self.offset - math.sin(a) * r
        r = math.tan(math.radians(self.section.headAngle)) * self.component.thickness
        x1 = x0 + math.sin(a) * self.component.thickness + math.cos(a) * r
        y1 = y0 - math.cos(a) * self.component.thickness - math.sin(a) * r
        
        if self.offset == 0:
            self.section.footPrint.outerHead = (x0,y0,0)
        else:
            self.section.footPrint.innerHead = (x1,y1,0)
    
        self.outerHead = (x0,y0,0)
        
        self.element.vertices.add((x0, y0, self.component.elevation))
        self.element.vertices.add((x0, y0, self.component.height + self.component.elevation))
        self.element.vertices.add((x1, y1, self.component.height + self.component.elevation))
        self.element.vertices.add((x1, y1, self.component.elevation))
        
    def _addTail(self):
        print("CWallLeaf.addTail") 

        if self.element.vertices.count() == 0:
            return

        r = math.tan(math.radians(self.section.tailAngle)) * self.component.thickness
        a = math.radians(self.section.angle)
        x0 = math.cos(a) * self.section.length
        y0 = math.sin(a) * self.section.length
        x1 = x0 + math.sin(a) * self.component.thickness + math.cos(a) * r
        y1 = y0 - math.cos(a) * self.component.thickness + math.sin(a) * r
        inclinationX = math.sin(a) * self.section.inclination
        inclinationY = - math.cos(a) * self.section.inclination

        refIndex = self.element.vertices.count()-4
        refVert = self.element.vertices.get(refIndex)
        lastX0 = refVert[0]
        lastY0 = refVert[1]
        
        #for later reference and usage
        if self.offset == 0:
            self.section.footPrint.outerHead = (lastX0, lastY0,0) 
            self.section.footPrint.outerTail = (lastX0+x0, lastY0+y0,0) 
        else:
            self.section.footPrint.innerTail = (lastX0+x1, lastY0+y1,0) 
        self.outerTail = (lastX0+x0, lastY0+y0,0)
        self.innerTail = (lastX0+x1, lastY0+y1,0) 

        if self.section.inclination != 0:
            self.element.vertices.select(refIndex+1)
            self.element.vertices.translate(inclinationX,inclinationY,0)
            self.element.vertices.select(refIndex+2)
            self.element.vertices.translate(inclinationX,inclinationY,0)

        if True: #((lastX0 + x0 != self.vertices.get(0)[0]) and (lastY0 + y0 != self.vertices.get(0)[1])):        
            self.element.vertices.add((lastX0 + x0, lastY0 + y0, self.component.elevation))
            self.element.vertices.add((lastX0 + x0 + inclinationX, lastY0 + y0 + inclinationY, self.component.height+self.component.elevation))              
            self.element.vertices.add((lastX0 + x1 + inclinationX, lastY0 + y1 + inclinationY, self.component.height+self.component.elevation))
            self.element.vertices.add((lastX0 + x1, lastY0 + y1, self.component.elevation))

            self.element.faces.add([refIndex+0, refIndex+1, refIndex+5, refIndex+4]) 
            self.element.faces.add([refIndex+1, refIndex+2, refIndex+6, refIndex+5])
            self.element.faces.add([refIndex+2, refIndex+3, refIndex+7, refIndex+6])
            self.element.faces.add([refIndex+3, refIndex+0, refIndex+4, refIndex+7])
                    
        else:
            self.element.faces.add([refIndex+0, refIndex+1, 0, 1]) 
            self.element.faces.add([refIndex+1, refIndex+2, 1, 2])
            self.element.faces.add([refIndex+2, refIndex+3, 2, 3])
            self.element.faces.add([refIndex+3, refIndex+0, 3, 0])
        
    def _build(self):        
        if (self.section.index == 0):
            self._addHead()                   
        self.section.length = self.section.length - math.tan(math.radians(self.section.headAngle))*self.offset - math.tan(math.radians(-self.section.tailAngle))*self.offset
        
        self._addTail()
      
###############################################################################################

class CWall(architecture.CElement):
    def __init__(self, name='Wall', components=None, sections=None, close=False, cloneFrom = None):
        print('walls.CWall.__init__')
        if components == None:
            components = CWallComponents(self)
        if sections == None:
            sections = CWallSections(self)
        self.components = components
        self.sections = sections
        self.leafs = []
        self.close = close
        super().__init__(name = name,  cloneFrom = cloneFrom)   
        
    def __del__(self):    
        del self.components
        del self.sections
        super().__del__()
   
    @staticmethod
    def isWall(name):
        return name in bpy.context.scene.wallProperties
        
    def _buildMesh(self):
        print("CWall._buildMesh")   
        sectionCount = len(self.sections)
        offset = 0
        del self.leafs[:]
        for component in self.components:
            if component.type == 'WALL':
                for index, section in enumerate(self.sections):
                    self.sections._calcHeadTailAngles(index)
                    section.index = index
                    leaf = CWallLeaf(self, offset, component, section)
                    leaf._build()
                    self.leafs.append(leaf)
                    
            offset += component.thickness  
        
        #close heading and tailing faces
        if not self.close:
            refIndex = 0
            for component in self.components:
                if component.type == 'WALL':
                    self.faces.add((refIndex+0,refIndex+3,refIndex+2,refIndex+1))
                    refIndex += sectionCount*4
                    self.faces.add((refIndex+0,refIndex+1,refIndex+2,refIndex+3))
                    refIndex += 4
                                                  
    def clear(self):
        super(architecture.CElement, self).clear()
        self.components.clear()
        self.sections.clear()
                   
    def getHeight(self):
        height = 0
        for component in self.components:
            height = max(height, component.height+component.elevation)
        return height
            
    def getThickness(self):
        thickness = 0
        for component in self.components:
            thickness += component.thickness
        return thickness
            
    def _applyModifiers(self):        
        print('apply colors')
        #apply colors to components
        sectionCount = self.sections.count()
        componentCount = self.components.count('WALL')
        componentIndex = 0 #only take real WALL type in consideration
        for component in self.components:
            if component.type == 'WALL':
                for sectionIndex in range(0, sectionCount):
                    for i in range(0,4):
                        index = componentIndex * sectionCount * 4 + sectionIndex * 4 + i
                        self._object.data.polygons[index].material_index = component.color
                if self.close == False:
                    index = componentCount * sectionCount * 4 + componentIndex * 2
                    print('wall head or tail polygon index=', index)
                    print('set to color index', component.color)
                    self._object.data.polygons[index].material_index = component.color
                    self._object.data.polygons[index+1].material_index = component.color
                componentIndex += 1 

        #make holes
        print('make holes')
        for sectionIndex, section in enumerate(self.sections):
            print(section.holes)
            if section.holes.count()>0:
                for hole in section.holes:
                    offset = 0
                    if hole.componentsToDrill == 'ALL':
                        hole.componentsToDrill = range(0, self.components.count())
                    for cIndex in hole.componentsToDrill:
                        component = self.components[cIndex]
                        hole.origins.append(self.addHole(offset, component, section, hole))
                        offset += component.thickness 
            if section.cornerFillets.count()>0:
                for fillet in section.cornerFillets:
                    self.addCornerFillet(section, sectionIndex, fillet)

    def addHole(self, offset, component, section, holeData):
        position = (holeData.position[0]-component.reveal, holeData.position[1])

        width = holeData.dimensions[0]+component.reveal*2
        height = holeData.dimensions[1]+component.reveal
        thickness = component.thickness * 1.02
        origin = section.footPrint.outerHead

        a = math.radians(section.angle)
        x0 = origin[0] + position[0]*math.cos(a) - (-offset + 0.01 * thickness) * math.sin(a)
        y0 = origin[1] + position[0]*math.sin(a) + (-offset + 0.01 * thickness) * math.cos(a)
        x1 = x0 + width*math.cos(a)
        y1 = y0 + width*math.sin(a)
        x2 = x0 + thickness*math.sin(a)
        y2 = y0 - thickness*math.cos(a)
        x3 = x1 + thickness*math.sin(a)
        y3 = y1 - thickness*math.cos(a)
        z0 = origin[2]+position[1]
        z1 = z0 + height
    
        if (component.type == 'WALL'):
            hole = elements.CElement('Hole')
            hole.setEditMode()
            hole.vertices.add((x0,y0,z0))
            hole.vertices.add((x1,y1,z0))
            hole.vertices.add((x2,y2,z0))
            hole.vertices.add((x3,y3,z0)) 
            hole.vertices.add((x0,y0,z1))
            hole.vertices.add((x1,y1,z1))
            hole.vertices.add((x2,y2,z1))
            hole.vertices.add((x3,y3,z1))        
            hole.faces.add([0,1,3,2])
            hole.faces.add([0,4,5,1])
            hole.faces.add([1,5,7,3])
            hole.faces.add([3,7,6,2]) 
            hole.faces.add([2,6,4,0]) 
            hole.faces.add([4,6,7,5])  
            hole.setObjectMode() 
            hole.translate(self.getLocation())
            self.cutWith(hole)            
            hole.free() 
            
        return (x1,y1,z0)
            
    def addCornerFillet(self, section, sectionIndex, filletData):
        dimensions = filletData.dimensions
        print("CWall.addCornerFillet ", dimensions)

        #avoid this case:    
        if (dimensions[0] < 0 )and (dimensions[1] < 0):
            return    

        corner = filletData.corner
        length = section.length
        thickness = 0
        height = self.getHeight()
        thickness = self.getThickness()
                
        vertDim = dimensions[0]
        horDim = dimensions[1]

        fillet = elements.CElement('Fillet')
        fillet.setEditMode()
  
        if corner == 'HEAD_BOTTOM':
            fillet.vertices.add((-.01,.01,0))
            fillet.vertices.add((-.01,.01,vertDim))
            fillet.vertices.add((horDim,.01,0))
            fillet.vertices.add((-.01,-thickness-.02,0))
            fillet.vertices.add((-.01,-thickness-.02,vertDim)) 
            fillet.vertices.add((horDim,-thickness-.02,0))
        
            fillet.faces.add([0,1,2]) 
            fillet.faces.add([5,4,3]) 
            fillet.faces.add([0,2,5,3]) 
            fillet.faces.add([0,3,4,1]) 
            fillet.faces.add([1,4,5,2]) 
            
        if corner == 'HEAD_TOP':
            fillet.vertices.add((-.01,.01,0))
            fillet.vertices.add((-.01,.01,-vertDim))
            fillet.vertices.add((horDim,.01,0))
            fillet.vertices.add((-.01,-thickness-.02,0))
            fillet.vertices.add((-.01,-thickness-.02,-vertDim)) 
            fillet.vertices.add((horDim,-thickness-.02,0))
        
            fillet.faces.add([2,1,0]) 
            fillet.faces.add([3,4,5]) 
            fillet.faces.add([3,5,2,0]) 
            fillet.faces.add([1,4,3,0]) 
            fillet.faces.add([2,5,4,1]) 
            
        if corner == 'TAIL_BOTTOM':
            fillet.vertices.add((.01,.01,0))
            fillet.vertices.add((.01,.01,vertDim))
            fillet.vertices.add((-horDim,.01,0))
            fillet.vertices.add((.01,-thickness-.02,0))
            fillet.vertices.add((.01,-thickness-.02,vertDim)) 
            fillet.vertices.add((-horDim,-thickness-.02,0))
        
            fillet.faces.add([2,1,0]) 
            fillet.faces.add([3,4,5]) 
            fillet.faces.add([3,5,2,0]) 
            fillet.faces.add([1,4,3,0]) 
            fillet.faces.add([2,5,4,1]) 

        if corner == 'TAIL_TOP':
            fillet.vertices.add((.01,.01,0))
            fillet.vertices.add((.01,.01,-vertDim))
            fillet.vertices.add((-horDim,.01,0))
            fillet.vertices.add((.01,-thickness-.02,0))
            fillet.vertices.add((.01,-thickness-.02,-vertDim)) 
            fillet.vertices.add((-horDim,-thickness-.02,0))
        
            fillet.faces.add([0,1,2]) 
            fillet.faces.add([5,4,3]) 
            fillet.faces.add([0,2,5,3]) 
            fillet.faces.add([0,3,4,1]) 
            fillet.faces.add([1,4,5,2]) 
            
        fillet.setObjectMode()
        
        if corner == 'HEAD_BOTTOM':          
            fillet.locate(section.footPrint.outerHead)
            fillet.rotate(0,0,section.angle)

        if corner == 'HEAD_TOP':
            fillet.locate(section.footPrint.outerHead)
            fillet.translate(0,0,height)
            fillet.rotate(0,0,section.angle)

        if corner == 'TAIL_BOTTOM':
            fillet.locate(section.footPrint.outerTail)
            fillet.rotate(0,0,section.angle)

        if corner == 'TAIL_TOP':
            fillet.locate(section.footPrint.outerTail)
            fillet.translate(0,0,height)
            fillet.rotate(0,0,section.angle)

        fillet.translate(self.getLocation())
        self.cutWith(fillet)     
        print()
        fillet.free() 
        
    def findLeaf(self, section, component):
        for leaf in self.leafs:
            if leaf.section == section and leaf.component == component:
                return leaf
            
    def leafByIndex(self, sectionIndex, componentIndex):
        for leaf in self.leafs:
            if leaf.section == self.sections[sectionIndex] and leaf.component == self.components[componentIndex]:
                return leaf

########################################################################################

class CWallGroup(CItemList):
    def __init__(self, name='WallGrid', components=None, colors=[], close=False):
        self.name = name
        if components == None:
            components = CWallComponents(self)
        self.components = components
        for color in colors:
            self.addColor(color)
    def add(self, position=(0.0,0.0,0.0), length=1, angle=0, sections=[]):
        wall = CWall(self.name+".Wall"+str(self.count()))
        wall.locate(position)
        wall.components = self.components
        if sections==[]:
            wall.sections.add(length, angle)
        else:
            for section in sections:
                wall.sections.add(section[0], section[1])
        super().add(wall)
        return wall
    def update():
        for wall in self:
            wall.update

def test():
    
    print("*** START ***")   
    
    wall = CWall()
    wall.addColor((1,1,1))
    wall.addColor((1,1,0.6))
    wall.components.add(height=2.81,thickness=0.10,color=0)
    wall.components.add(height=2.81,thickness=0.05,type='CAVITY')
    wall.components.add(height=2.61,thickness=0.15,elevation=0.1,reveal=0.05,color=1)
    section = wall.sections.add(3,0)
    section = wall.sections.add(3,-90)
    section.holes.add((1,1), (1,1))
    section = wall.sections.add(3,-180)
#    section.cornerFillets.add('HEAD_TOP',(1,1))
#    section.cornerFillets.add('TAIL_TOP',(1,1))
    section.reshape('GABLE')
    section = wall.sections.add(3,-270,0,True)
    wall.close = True
    wall.update()
#    print(wall.getHeight())
#    
#    wall = CWall()
#    wall.locate(0,1,0)
#    wall.addColor((1,1,1))
#    wall.addColor((1,0,0))
#    wall.components.add(height=2.81,thickness=0.10,color=0)
#    wall.components.add(height=2.81,thickness=0.05,type='CAVITY')
#    wall.components.add(height=2.61,thickness=0.15,elevation=0.1,reveal=0.05,color=1)
#    section = wall.sections.add(3,0)
#    wall.close = False
#    wall.update()
#    wall.setEditMode()
#    n = wall.edges.count()
#    wall.edges.select(-1)
#    wall.edges.translate(0,0,-2.81)
#    wall.setObjectMode()

#    wall = bpy.context.window_manager.elements.findByObject(wall._object)
#    print("found wall = ",wall)
#    wall.clearMesh

if __name__ == '__main__':
    test()













































































































