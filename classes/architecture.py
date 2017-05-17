import bpy
import bmesh
import lists
import elements
from bpy.types import WindowManager

class ImplementationError(Exception):
    def __init__(self):
        super().__init__()
    def __str__(self):
        return sys._getframe(1).f_code.co_name+" not implemented"

class CElement(elements.CElement):
    def __init__(self, name = 'Element', parent = None, cloneFrom = None, location=(0,0,0), angle=(0,0,0)):
        print('architecture.CElement.__init__')
        super().__init__(name=name, parent=parent, cloneFrom=cloneFrom)

        self.locate(location)
        self.setAngle(angle[0], angle[1], angle[2])
        self.select()
        bpy.context.window_manager.elements.add(self)
            
    def __del__(self):
        print('architecture.CElement.__del__')
        bpy.context.window_manager.elements.remove(self)
        super().__del__()
    
    def update(self): 
        print("architecture.CElement.update")
        self._clearMesh()
        self.setEditMode()
        self._buildMesh()
        self.setObjectMode()
        self._applyModifiers()
        self._applyMaterials()
        
    def _clearMesh(self):
        print("architecture.CElement._clearMesh")
        bm = bmesh.new()
        bm.from_mesh(self._mesh)
        bm.clear()
        bm.to_mesh(self._mesh)
        del bm
        
    def _buildMesh(self):
        raise ImplementationError()
        
    def _applyModifiers(self):
        pass
        
    def _applyMaterials(self):
        pass

    @property
    def _type(self):
        return 'Architecture.'+type(self).__name__

class CElementRepository(lists.CItemList):
    def sanitize(self):
        print("CElementRepository.sanitize")
        print("bpy.data.objects=",bpy.data.objects)
        for element in self:
            print(element)
#            if element._object not in bpy.data.objects:
#                self.remove(element)
   
    def isOfType(self, element, type):
        index = self.find(element)
        if index>=0:
            return self[index]._type == type
        else:
            return False
     
    def findByObject(self,object):
        for item in self:
            if item._object == object:
                return item
        return None 
    
    def findByname(self,name):
        for item in self:
            if item.name == name:
                return item
        return None 
    
    def listOfType(self, wanted_type):
        self.sanitize()
        list = []
        for item in self:
            if type(item) is wanted_type:
                list.append(item)
        return list
        
def getElementRepository():
    return bpy.context.window_manager.elements

def getElementByObject(obj):
    return bpy.context.window_manager.elements.findByObject(element._object)

def setup():
    print('*** architecture.setup')
    WindowManager.elements = CElementRepository()
    
def teardown():
    del WindowManager.elements
    
if __name__ == '__main__':
    setup()
    element = CElement()
    element = getElementByObject(element._object)
    element._clearMesh()
    teardown()