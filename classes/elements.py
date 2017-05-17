import bpy
import bmesh
import math
import copy
from mathutils import Vector
import lists

#CTupleList differs subtantially from CItemList, 
#because data is maintained in a seperate property for easier manipulation in subclasses
class CTupleList():
    def __init__(self, tupleSize):
        self.tupleSize = tupleSize   
        self.data = []
        self.allowDuplicates = True
        self.select(-1)
    def set(self, index, item):
        self.data.ensure_lookup_table()
        if index >= self.count():
            raise Exception('CTupleList: wrong index '+str(index)+' of maximum '+str(self.count()))
        self.data[index] = item
    def get(self, index):
        self.data.ensure_lookup_table()
        if index >= self.count():
            raise Exception('CTupleList: wrong index '+str(index)+' of maximum '+str(self.count()))
        return self.data[index]
    def count(self):
        return len(self.data)
    def add(self, item):
        if len(item) == self.tupleSize:
            if not (self.allowDuplicates):
                n = self.indexOf(item)
            else: 
                n = -1                    
            if n == -1:
                self.data.new(item)
                return len(self.data)-1
            else:
                return n
    def delete(self, index):
        self.data.remove(index)
        if index<= self.selectedIndex():
            self.select(-1)
    def clear(self):
        self.data.ensure_lookup_table()
        while len(self.data)>0:
            self.data.remove(self.data[0])
        self.select(-1)
    def indexOf(self, item):
        for i in range(0, self.count()):
            if self.get(i) == item:
                return i
        return -1
    def select(self, item):
        if isinstance(item, tuple):
            item = self.indexOf(item)
        if (item >=0) and (item < self.count()):
            self.selectedIndex = item
            self.selected = self.get(self.selectedIndex)
        else:
            self.selectedIndex = -1
            self.selected = None
            
class CVertexList(CTupleList):
    def __init__(self, parent):
        super(CVertexList, self).__init__(3)
        self._parent = parent  
    def add(self, item):
        print('add vertices ',item) 
        return super().add(item)
    def get(self, index):
        self.data.ensure_lookup_table()
        return tuple(self.data[index].co)
    def set(self, index, item):
        if isinstance(item, tuple):
            item = Vector(item)
        self.data[index].co = item
    def translate(self, x=0, y=0, z=0):
        item = self.get(self.selectedIndex)
        item = (item[0] + x, item[1] + y, item[2] + z)
        self.set(self.selectedIndex, item)
        
class CEdgesList(CTupleList):
    def __init__(self, parent):
        super(CEdgesList, self).__init__(2)
        self._parent = parent  
    def get(self, index):
        return super().get(index).verts
    def set(self, index, item):
        super().get(index).verts = item
    #items: can be both vertex index list or vertex tuple list          
    def add(self, items):
        if not isinstance(items, list):
            raise Exception('need a list of vertices or vertex indexes')
        itemSize = len(items)
        if itemSize == 2:
            indices = []
            for item in items:
                if isinstance(item, tuple):
                    index = self._parent.vertices.add(item)
                else:
                    index = item
                indices.extend([index])
            self._parent._bmesh.verts.ensure_lookup_table()
            vertList = (self._parent._bmesh.verts[i] for i in indices)
            self.data.new(vertList)
            return len(self.data)-1
        else: 
            raise Exception('need 2 vertices or indexes of vertices, '+str(itemSize)+' given')       
    def translate(self, pOrX=0, y=0, z=0):
        items = self.get(self.selectedIndex)
        print(items)
        newItems = []
        for item in items:
            t = tuple(item.co)
            print(t)
            if isinstance(pOrX, tuple):
                t = (t[0] + pOrX[0], t[1] + pOrX[1], t[2] + pOrX[2])
            if isinstance(pOrX, float) or isinstance(pOrX, int):
                t = (t[0] + pOrX, t[1] + y, t[2] + z)
            item.co = t

class CFacesList(CTupleList):
    def __init__(self, parent):
        super(CFacesList, self).__init__(0)
        self._parent = parent          
    #items: can be both vertex index list or vertex tuple list          
    def add(self, items):
        print('add face(s) ',items) 
        itemSize = len(items)
        if itemSize > 2:
            indices = []
            for item in items:
                if isinstance(item, tuple):
                    index = self._parent.vertices.add(item)
                else:
                    index = item
                indices.extend([index])
            self._parent._bmesh.verts.ensure_lookup_table()
            vertList = (self._parent._bmesh.verts[i] for i in indices)
            self.data.new(vertList)
            return len(self.data)-1
    # face needs to be selected first
    def extrude(self, x, y, z):
        if self.selectedIndex > -1:
            face = self.selected
            r = bmesh.ops.extrude_discrete_faces(self._parent._bmesh, faces=[face])
            bmesh.ops.translate(self._parent._bmesh, vec=Vector((x,y,z)), verts=r['faces'][0].verts)
    def reverse(self):
        if self.selectedIndex > -1:
            face = self.selected
            bmesh.ops.reverse_faces(self._parent._bmesh, faces=[face])
        
    def remove(self, material):
        index = self.indexOf(material)
        if index > -1:
            self.delete(index)
            
########################################################################################
        
class CMaterial():
    def __init__(self, name = ''):
        self.name = name
        self.material = self._create()    
    def _create(self):
        if self.name == "":
            self.name = self._createName()
            material = bpy.materials.new(self.name)
        else:
            material = bpy.data.materials.get(self.name)
            if material==None:
                material = bpy.data.materials.new(self.name)
        return material
    def createName(self):
        return "Material"+str(len(bpy.data.materials))

class CColor(CMaterial):
    def __init__(self, name="", diffuse_rgb=(1,1,1), specular_rgb=(1,1,1), alpha=1.0):
        super().__init__(name)
        self.diffuse_rgb = diffuse_rgb
        self.specular_rgb = specular_rgb
        self.alpha = alpha
    @property
    def diffuse_rgb(self):
        return self.material.diffuse_color
    @diffuse_rgb.setter
    def diffuse_rgb(self, value):
        self.material.diffucse_color = diffuse_rgb
    @property
    def specular_rgb(self):
        return self.material.specular_color
    @specular_rgb.setter
    def specular_rgb(self, value):
        self.material.specular_color = diffuse_rgb
    @property
    def alpha(self):
        return self.material.alpha
    @alpha.setter
    def alpha(self, value):
        self.material.alpha = diffuse_rgb
        
class CMaterialList(lists.CItemList):
    def add(self, name=""):
        material = CMaterial(name)
        return super().add(material)
    
class CColorList(lists.CItemList):
    def add(self, name="", diffuse_rgb=(1,1,1), specular_rgb=(1,1,1), alpha=1.0):
        color = CColor(name, name, diffuse_rgb, specular_rgb, alpha)
        return super().add(color)
    
class CModifierList():
    def __init__(self, parent):
        self.parent = parent
    def add(self, name, type):
        modifier = self.parent._object.modifiers.new(name, type) 
        return modifier
    def addBoolean(self, name, operation=None, element=None, solver="CARVE"):
        modifier = self.add(name, 'BOOLEAN')
        if operation != None:
            modifier.operation = operation
        if element != None:
            modifier.object = element._object
        if solver != None:
            modifier.solver = solver
        return modifier            
    def apply(self, name):
        bpy.context.scene.objects.active = self.parent._object
        return bpy.ops.object.modifier_apply(modifier = name)
    def remove(self, name):
        self._object.modifiers.remove(name)
         
class CGeometry():
    def __init__(self, element):
        self.element = element
    def _build(self):
        pass
       
########################################################################################
        
class CElement():    
    def __init__(self, name = 'Element', parent = None, cloneFrom = None):
        print("elements.CElement.__init__")
        
        self.name = name
        self.parent = parent
        self.type = 'Element'
        
        #instantiate Mesh
        if cloneFrom != None:
            if isinstance(cloneFrom, bpy.types.Mesh):
                self._mesh = cloneFrom
            if isinstance(cloneFrom, CElement):
                print("*** clone a CElement")
                self._mesh =  cloneFrom._mesh 
            if isinstance(cloneFrom, bpy.types.Object):
                self._mesh = cloneFrom.data
            else:
                self._mesh = self._createMesh()     
        else:
            self._mesh = self._createMesh()
        
        #instantiate Object
        if (cloneFrom != None) and isinstance(cloneFrom, bpy.types.Object):
            self._object = cloneFrom            
        else:
            self._object = bpy.data.objects.new(self.name, self._mesh)
        
            scene = bpy.context.scene    
            scene.objects.link(self._object) 

        self.setAngle(0,0,0)
        self.locate(0,0,0)
        self.vertices = CVertexList(self)
        self.edges = CEdgesList(self)
        self.faces = CFacesList(self)
        
        self.modifiers = CModifierList(self)
        self.materials = CMaterialList(self)
        
        self.setObjectMode()
        
    #def __del__(self):
    #    pass
    # should this inherite from Object class to avoid memory leaks?    
            
    def _createMesh(self):
        return bpy.data.meshes.new(self.name+".MESH") 
        
    def free(self):
        scene = bpy.context.scene    
        scene.objects.unlink(self._object) 
        del self._object
        del self._mesh
        del self
        
    #override in child classes
    def _createElement(self, name):
        return CElement(name)
        
    def duplicate(self):
        element = _createElement(self.name+'.Copy')

        # Copy data block from the old object into the new object
        element._object.data = self.data.copy()
        element._object.scale = self.scale
        element._object.location = self.location

        self._setData()
        return element        
    
    def _setData(self):
        self._bmesh = bmesh.from_edit_mesh(self._mesh)
        self.vertices.data = self._bmesh.verts   
        self.edges.data = self._bmesh.edges    
        self.faces.data = self._bmesh.faces 
        
    def clear(self):
        self.setEditMode()
        self.vertices.clear()
        self.faces.clear()
        self.edges.clear()
        self.setObjectMode()
        
    @property
    def mode(self):
        return self._object.mode
    
    @mode.setter
    def mode(self, mode):
        if mode == 'EDIT':
            self.setEditMode()
        if mode == 'OBJECT':
            self.setObjectMode()
    
    def setEditMode(self):
        print("CElement.setEditMode")
        if self._object.mode != 'EDIT':
            activeObject = bpy.context.scene.objects.active
            bpy.context.scene.objects.active = self._object
            bpy.ops.object.mode_set(mode='EDIT')  
            bpy.context.scene.objects.active = activeObject
            self._setData()
        
    def setObjectMode(self):
        print("CElement.setObjectMode")
        if self._object.mode != 'OBJECT':
            activeObject = bpy.context.scene.objects.active
            bpy.context.scene.objects.active = self._object
            bpy.ops.object.mode_set(mode='OBJECT')  
            bpy.context.scene.objects.active = activeObject
            
    def setParent(self, element):
        self.parent = element
        self._object.parent = element._object  
        
    def setAngle(self,x,y,z):
        self._object.rotation_euler = [math.radians(x),math.radians(y),math.radians(z)] 
        
    def rotate(self,x,y,z):
        angle = self._object.rotation_euler
        self._object.rotation_euler = [angle[0]+math.radians(x),angle[1]+math.radians(y),angle[2]+math.radians(z)]     
        
    def locate(self,pOrX=0,y=0,z=0):
        if isinstance(pOrX, tuple) and len(pOrX)==3:
            self._object.location = pOrX
        if isinstance(pOrX, float) or isinstance(pOrX, int):
            self._object.location = (pOrX,y,z)  
    
    def getLocation(self):
        return self._object.location.to_tuple()
        
    def translate(self,pOrX=0,y=0,z=0):
        if isinstance(pOrX, Vector):
            pOrX = tuple(pOrX)
        if self._object.mode == 'OBJECT':    
            location = self.getLocation()
            if isinstance(pOrX, tuple) and len(pOrX)==3:
                self._object.location = (location[0]+pOrX[0],location[1]+pOrX[1],location[2]+pOrX[2]) 
            if isinstance(pOrX, float) or isinstance(pOrX, int):
                self._object.location = (location[0]+pOrX,location[1]+y,location[2]+z)     
        if self._object.mode == 'EDIT':    
            for i,v in enumerate(self.vertices):
                v = self.vertices.get(i)
                if isinstance(pOrX, tuple) and len(pOrX)==3:
                    v = (v[0]+pOrX[0],v[1]+pOrX[1],v[2]+pOrX[2]) 
                if isinstance(pOrX, float) or isinstance(pOrX, int):
                    v = (v[0]+pOrX,v[1]+y,v[2]+z) 
                self.verticesices.set(i,v)
        
    def translateFrom(self,element,pOrX=0,y=0,z=0):
        location = element.getLocation()
        if isinstance(pOrX, tuple) and len(pOrX)==3:
            self._object.location = (location[0]+pOrX[0],location[1]+pOrX[1],location[2]+pOrX[2]) 
        if isinstance(pOrX, float) or isinstance(pOrX, int):
            self._object.location = (location[0]+pOrX,location[1]+y,location[2]+z) 
    
    def translateMesh(self,pOrX=0,y=0,z=0):
        self.setEditMode()
        self.translate(pOrX,y,z)
        self.setObjectMode()
        
    def update(self):
        self._mesh.update()
        
    def activate(self, select=True):
        bpy.context.scene.objects.active = self._object
        if select:
            self.select()
        else:
            self.deselect()

    def select(self):
        self._object.select = True

    def deselect(self):
        self._object.select = False

    def join(self, elements):
        #deselect all objects, or they will be included in the join ;-)
        bpy.ops.object.select_all(action='DESELECT')
        self.activate(True)
        if isinstance(elements, list):
            for element in elements:
                element.select()
        else:
            elements.select()
        bpy.ops.object.join()

    def addColor(self,color,name=""):
        for i in range(0, self.materials.count()):
            if self.materials.get(i).diffuse_color == color:
                return self.materials.get(i)
        if name == "":
            name = self.name+'Color'+str(self.materials.count())        
        colorMaterial = self.materials.add(name)
        colorMaterial.diffuse_color = color
        return colorMaterial
    
    def removeColor(self, name):
        self.materials.remove(name)
    
    def cutWith(self, element):
        self.modifiers.addBoolean('Bool_Mod', 'DIFFERENCE', element, 'CARVE')
        self.modifiers.apply('Bool_Mod')
    
    def loadFromFile(self, directory, filename, doLink = False):
        bpy.ops.wm.link_append(directory, filename, doLink)
        del self._object
        self._object = bpy.data.objects[data['filename']]  
        return self

    def repeat(obj, count=2, type='FIXED_COUNT'):
        array_mod = obj.modifiers.new('Repeater', 'ARRAY')
        array_mod.fit_type = type
        if type == 'FIXED_COUNT':
            array_mod.count = count

class CEmpty(CElement):
    def _createMesh(self):
        return None
    
def test():
    element = CElement()
    element.setEditMode()
    element.faces.add([(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0)])
    element.edges.add([(-1,0,-1), (1,0,-1)])
    element.faces.add([-4,-3,-2,-1])
    element.faces.add([0,1,-1,-2])
    element.faces.add([1,2,-1])
    element.faces.add([3,0,-2])
    element.faces.select(0)
    element.faces.extrude(0,0,2)
    print("number of edges=", element.edges.count())
#    print(element.vertices.indexOf((1,-1,0)))
    for v in (element.edges.get(4)):
        print(tuple(v.co))
    element.edges.select(4)
    element.edges.translate((0,0,-1))
    
    element.setObjectMode()
    element.addColor((1,0,0))
    element.rotate(180,0,30)
    element.translate((0,0,1))
    
#    element1 = CElement('Element1', cloneFrom=element)
#    element1.addColor((0,0,1))
#    element.cutWith(element1)
#    element1.setParent(element)
#    element1.update()

#    element.select()
#    element.join(element1)
   
#    import bmesh
#    element._bmesh = bmesh.new()   
#    element._bmesh.from_mesh(element._mesh)
#    element._bmesh.clear()
#    element._bmesh.to_mesh(element._mesh)

if __name__ == '__main__':
    test()




































