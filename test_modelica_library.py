# -*- coding: utf-8 -*-

import os
import re
import unittest
import sys


sys.path.append("C:\\Program Files (x86)\\Dymola 2017 FD01\\Modelica\\Library\\python_interface\\dymola.egg")

from dymola.dymola_interface import DymolaInterface


class TestBuildingSystemsModels(unittest.TestCase):
    """
    Class remains empty when initialised but is filled by the for loop in the 
    main mdule.
    
    This is necessary to get stand alone checks for each element of a list (in 
    our case each model)
    """
    pass
    

def get_all_models_of_Modelica_lib(curPckDP,lst):
    """
    curPckDP = current Package Directory Path (string)
    lst = list of all models (list)
    
    Recursively, gets all models in a library - as long as they are mentioned 
    in a package.order file
    """
    
    if not os.path.exists(os.path.join(curPckDP,'package.order')):
        return
    
    with open(os.path.join(curPckDP,'package.order')) as file:
        lContent = file.read().splitlines();
        
    for elem in lContent:

        #path for filesystem
        pCurEl = os.path.join(curPckDP,elem)

        #if it is dir/pck -> go one step further,
        #if not, it is a mo file -> add to list
        if os.path.isdir(pCurEl):
            get_all_models_of_Modelica_lib(pCurEl,lst)

        else:
            lst.append(pCurEl)
            
    return lst

    
def checkModel(dymola, model):
    """
    Applies Dymolas checkModel() method to a model.
    """    
    success = dymola.checkModel(model)    
    return success

def create_test(dymola,model):
    """
    Necessary way in order to get a dynamic list of all tests. 
    """
    def do_test(self):
        """
        Different Tests, that should be fulfilled by all models.
        Could be extended
        """
        success = checkModel(dymola, model)
        
        self.assertEqual(success, True)
    return do_test


def run_unittests(modelica_library, dymola_pedantic_mode ='false'):
    import xmlrunner   
   
    models = get_all_models_of_Modelica_lib(modelica_library,[])      
    models = [model.replace('\\','.') for model in models]
    
    dymola = DymolaInterface()
    dymola.ExecuteCommand("Advanced.PedanticModelica = %s" %dymola_pedantic_mode)
    dymola.openModel(os.path.join(modelica_library,'package.mo'))    
    
    for model in models:
        test_method = create_test(dymola, model)
        test_method.__name__ = 'test_%s' % model.replace('.','_')
                
        setattr(TestBuildingSystemsModels, test_method.__name__, test_method)  
          
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
    
    dymola.close()


if __name__ == '__main__':
    modelica_library = 'test_library'
    run_unittests(modelica_library)

