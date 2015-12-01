'''test_measuretexture - test the MeasureTexture module
'''

import base64
import os
import shutil
import tempfile
import unittest
import urllib2
import zlib
from StringIO import StringIO

import numpy as np
import scipy.ndimage as scind
from bioformats import load_image
from bioformats.formatreader import load_using_bioformats_url
from scipy.io.matlab import loadmat

import cellprofiler.cpimage as cpi
import cellprofiler.cpmodule as cpm
import cellprofiler.measurements as cpmeas
import cellprofiler.modules.measuretexture as M
import cellprofiler.objects as cpo
import cellprofiler.pipeline as cpp
import cellprofiler.preferences as cpprefs
import cellprofiler.workspace as cpw
from cellprofiler.modules.tests import \
     example_images_directory, maybe_download_example_image, \
     maybe_download_sbs, github_url

INPUT_IMAGE_NAME = 'Cytoplasm'
INPUT_OBJECTS_NAME = 'inputobjects'
class TestMeasureTexture(unittest.TestCase):
        
    def make_workspace(self, image, labels, convert = True, mask = None):
        '''Make a workspace for testing MeasureTexture'''
        module = M.MeasureTexture()
        module.image_groups[0].image_name.value = INPUT_IMAGE_NAME
        module.object_groups[0].object_name.value = INPUT_OBJECTS_NAME
        pipeline = cpp.Pipeline()
        object_set = cpo.ObjectSet()
        image_set_list = cpi.ImageSetList()
        image_set = image_set_list.get_image_set(0)
        workspace = cpw.Workspace(pipeline,
                                  module,
                                  image_set,
                                  object_set,
                                  cpmeas.Measurements(),
                                  image_set_list)
        image_set.add(INPUT_IMAGE_NAME, cpi.Image(image, convert=convert,
                                                  mask = mask))
        objects = cpo.Objects()
        objects.segmented = labels
        object_set.add_objects(objects, INPUT_OBJECTS_NAME)
        return workspace, module
    
    def test_01_01_load_matlab(self):
        data = ('eJzzdQzxcXRSMNUzUPB1DNFNy8xJ1VEIyEksScsvyrVSCHAO9/TTUX'
                'AuSk0sSU1RyM+zUggpTVXwKs1TMLBUMDS0MjSxMjFTMDIA8kgGDIye'
                'vvwMDAxzmBgYKua8jfDNvm0gEWZ3cpvQrmlO/JY/djhfs9zSLHf94k'
                'bWayprlhrccC0U8Z+dyxqtdbIusv9v5uQs64lTdYpy1C8ENirF/a6d'
                '/935k7KmL8OBj4IMpXZmFfrNG64q7VQpVYxX9tqYzm4awHr84mf2e/'
                'kL+x9ecNx+IVGD4bOY/fuq5CLj2WfiYycKFgfw79pklG/7jG+i/Jfj'
                'GxO/VDUsP7HzWL2Ax7aIt9K7DjOqxaXIP1zt/7yOM/SP2dHz9xbxqS'
                '7lE73Hv/S503/miBfh4Vdy4y/d7//FO+vS9vnLLixq4175NfjBnOwC'
                'Ka6+Cb/tttl/ChJPzM96s5rzt9aOPRIll3+s1a5rvZM8rbkgYn/u7e'
                'dro303ihcdz5nfWbV05v/pXXsn6Hc+FMzaoBB1wvXRi2cbJx1Y2fD+'
                'j3RFV+UUYYvUC8rnP288a1NisV5ERvF75oGe83ySTunPP4qY2i9l8e'
                'MscbC6F3lUevnbzd9+yx5fv05/813O7zt7fs5ftiX4O/fnI29O1HWf'
                'im//7HRQsOj64hPcBnM9Px55LM57L5vV/8QN6YfWNkkXDDdwv/25Mk'
                'n6Y263ePjRwoMaD9lFclI7nGPN1S1fbdTr06nYxp/eyCqr8jDl6cs9'
                '33b9uFzHnvn4xC67WV4yTnznE2vdZN90us5fLnfPOuKEzZO1zjn2K9'
                'buZz9hM2H6dTnPw984Z4v0C/dHVvTy1Ct22zFJzXl8IaXZJnwuu8qe'
                'Kxar3/l32xzeYLay/taOKx8t7/+3vp979HeIu2y8TEOKbIvPobkJnQ'
                'Ypd9xe3t+z6lN1mNwfrwcrtGWPXHpSvOQBx05rJ7mjj28eOL6uhu3k'
                'rvg4RQkD+c799T827PG/avpVo/jlgw0TX9/btHL/rbjKl/sWb17tZm'
                'Uf9ffa+7AX3+VyzN7nX3txPDf8Vz3jKX7jVwD5C2/v')
        fd = StringIO(zlib.decompress(base64.b64decode(data)))
        pipeline = cpp.Pipeline()
        pipeline.load(fd)
        self.assertEqual(len(pipeline.modules()),3)
        module = pipeline.modules()[2]
        #
        # image_name = OrigBlue
        # object_name = Nuclei
        # scale = 3,4,5
        #
        self.assertTrue(isinstance(module,M.MeasureTexture))
        self.assertEqual(module.image_count.value, 1)
        self.assertEqual(module.image_groups[0].image_name.value, "OrigBlue")
        
        self.assertEqual(module.object_count.value, 1)
        self.assertEqual(module.object_groups[0].object_name.value, "Nuclei")
        
        self.assertEqual(module.scale_count.value, 3)
        for scale, expected in zip([x.scale.value 
                                    for x in module.scale_groups],[3,4,5]):
            self.assertEqual(scale, expected)
        self.assertEqual(module.gabor_angles, 4)
    
    def test_01_02_load_v1(self):
        data = ('eJztWk1P2zAYdj9AdEiMcdkkLj5uE0RpB9LgspZ1bJ3oh0bFtNvS1C2eErt'
                'KHNbutJ+1437OjvsJi9uEJl4gaQptihJhhdfx4+fx69dOeHG90j6rnMBDSY'
                'b1Snu/hzUEW5rCetTQjyFhe/CtgRSGupCSY3hqYPjRIrBYgvLRsf1zcARLs'
                'nwE4l2ZWn3Lvv18AcC6fd+wS9Z5tObYGU/h9jliDJO+uQby4JlT/9suF4qB'
                'lY6GLhTNQuaUwq2vkR5tjwbXj+q0a2mooejexvbVsPQOMsxmzwU6j1t4iLR'
                'z/AMJQ3CbfUJX2MSUOHinf7H2mpcygZf74c/O1A8ZwQ85u+x66nn7D2DaPh'
                '/gtyee9tuOjUkXX+GupWgQ60r/WgXv73VIfxtCf9xuGrh/Yruc4+UQfMaHz'
                '4Ciw1sOwW0LvLy00ZDtvxsqKoO6wtTLKPrXhX643bBUDeGJjrj6Z8W9iujv'
                'NUEvt4vy3oE8J2+Yvx8JvNyuUkgog5bpLIAo/DlfPznwxY62RcRZ1ofPgga'
                'Npvcm3LxxFbZOnwp4bldRT7E0Bmt8kcIqNpDKqDGay+9x42VWnASixdmmMG'
                '5uN5lpwfca7SjauD4O/0FEXNw4uat94PCedYpxIO8V7zUO8j5cHlQrrVocn'
                'CzJRRG3LuDcy8UVnPtd7C/lEHxBwHO7RhgiJmYjj464+uP6edV0NyiJtZ8X'
                '5WTqjLK+k6Azyvshrs5ZcOUQnVvAH6/cnrxXmxbTMOEfr8vQvSr+TXUuV6f'
                '9Hkvkuorz3ZVE/65KHCRVp/helQ6XM+/lEJ1B8dr+TqGqKabpZDCWoTvs77'
                'qg/MtnhPuXPJ12xRNHREWe/pLm96A8wCk1UN+gFunOz/91xnzXIsc5To7xg'
                'Q7m519kfNHON6SysXCISRcN7kBHintYcRWmO2i/9cTV0nSnuBT3EHFlcPt6'
                'DPr/x3QfmWzzqzTeFJfikowL++7aAf71yG06yUj99+G1SuNOcSkuCe+7pH4'
                '3p7gUl+JWDzfMTHFinknM147zUh6eoP3pJfDvT9xWkaYNDMrPzxmSPj7kZU'
                'oaVbqTU1bSmf1rzXPgivMMQnjKAk/5Jh7cRYTh3mhg2GwWo7rCsCrVnNqWX'
                'VtxaznvZQhvSeAt3cSrI8W0DMTQkNk3qT4x2xMzeN4KAXxe/2dt6/Fu4db5'
                'BsA/z9P5//smDl82lxnzec8NbIbg8h5N7jh/gdni7Pkt7d0xLqr9P5vhZ1k=')
        fd = StringIO(zlib.decompress(base64.b64decode(data)))
        pipeline = cpp.Pipeline()
        pipeline.load(fd)
        self.assertEqual(len(pipeline.modules()),3)
        module = pipeline.modules()[2]
        #
        # image_name = DNA, Cytoplasm
        # object_name = Nuclei
        # scale = 3,4,5
        #
        self.assertTrue(isinstance(module,M.MeasureTexture))
        self.assertEqual(module.image_count.value, 1)
        self.assertEqual(module.image_groups[0].image_name.value, "OrigBlue")
        
        self.assertEqual(module.object_count.value, 1)
        self.assertEqual(module.object_groups[0].object_name.value, "Nuclei")
        
        self.assertEqual(module.scale_count.value, 3)
        for scale, expected in zip([x.scale.value 
                                    for x in module.scale_groups],[3,4,5]):
            self.assertEqual(scale, expected)
        self.assertEqual(module.gabor_angles.value, 3)
        self.assertTrue(module.wants_gabor)
        
    def test_01_03_load_v2(self):
        data = """CellProfiler Pipeline: http://www.cellprofiler.org
Version:1
SVNRevision:10865

MeasureTexture:[module_num:1|svn_version:\'1\'|variable_revision_number:2|show_window:True|notes:\x5B\x5D]
    Hidden:2
    Hidden:2
    Hidden:2
    Select an image to measure:rawDNA
    Select an image to measure:rawGFP
    Select objects to measure:Cells
    Select objects to measure:Nuclei
    Texture scale to measure:3
    Texture scale to measure:5
    Measure Gabor features?:Yes
    Number of angles to compute for Gabor:6

MeasureTexture:[module_num:2|svn_version:\'1\'|variable_revision_number:2|show_window:True|notes:\x5B\x5D]
    Hidden:2
    Hidden:2
    Hidden:2
    Select an image to measure:rawDNA
    Select an image to measure:rawGFP
    Select objects to measure:Cells
    Select objects to measure:Nuclei
    Texture scale to measure:3
    Texture scale to measure:5
    Measure Gabor features?:No
    Number of angles to compute for Gabor:6
"""
        pipeline = cpp.Pipeline()
        def callback(caller, event):
            self.assertFalse(isinstance(event, cpp.LoadExceptionEvent))
        pipeline.add_listener(callback)
        pipeline.load(StringIO(data))
        self.assertEqual(len(pipeline.modules()),2)
        for i, wants_gabor in enumerate((True, False)):
            module = pipeline.modules()[i]
            self.assertTrue(isinstance(module, M.MeasureTexture))
            self.assertEqual(len(module.image_groups), 2)
            self.assertEqual(module.image_groups[0].image_name, "rawDNA")
            self.assertEqual(module.image_groups[1].image_name, "rawGFP")
            self.assertEqual(len(module.object_groups), 2)
            self.assertEqual(module.object_groups[0].object_name, "Cells")
            self.assertEqual(module.object_groups[1].object_name, "Nuclei")
            self.assertEqual(len(module.scale_groups), 2)
            self.assertEqual(module.scale_groups[0].scale, 3)
            self.assertEqual(len(module.scale_groups[0].angles.get_selections()),1)
            self.assertEqual(module.scale_groups[0].angles.get_selections()[0], M.H_HORIZONTAL)
            self.assertEqual(module.scale_groups[1].scale, 5)
            self.assertEqual(len(module.scale_groups[1].angles.get_selections()),1)
            self.assertEqual(module.scale_groups[1].angles.get_selections()[0], M.H_HORIZONTAL)
            self.assertEqual(module.wants_gabor, wants_gabor)
            self.assertEqual(module.gabor_angles, 6)
        
    def test_01_03_load_v3(self):
        data = """CellProfiler Pipeline: http://www.cellprofiler.org
Version:1
SVNRevision:10865

MeasureTexture:[module_num:1|svn_version:\'1\'|variable_revision_number:3|show_window:True|notes:\x5B\x5D]
    Hidden:2
    Hidden:2
    Hidden:2
    Select an image to measure:rawDNA
    Select an image to measure:rawGFP
    Select objects to measure:Cells
    Select objects to measure:Nuclei
    Texture scale to measure:3
    Angles to measure:Horizontal,Vertical
    Texture scale to measure:5
    Angles to measure:Diagonal,Anti-diagonal
    Measure Gabor features?:Yes
    Number of angles to compute for Gabor:6

MeasureTexture:[module_num:2|svn_version:\'1\'|variable_revision_number:3|show_window:True|notes:\x5B\x5D]
    Hidden:2
    Hidden:2
    Hidden:2
    Select an image to measure:rawDNA
    Select an image to measure:rawGFP
    Select objects to measure:Cells
    Select objects to measure:Nuclei
    Texture scale to measure:3
    Angles to measure:Horizontal,Vertical
    Texture scale to measure:5
    Angles to measure:Diagonal,Anti-diagonal
    Measure Gabor features?:No
    Number of angles to compute for Gabor:6
"""
        pipeline = cpp.Pipeline()
        def callback(caller, event):
            self.assertFalse(isinstance(event, cpp.LoadExceptionEvent))
        pipeline.add_listener(callback)
        pipeline.load(StringIO(data))
        self.assertEqual(len(pipeline.modules()),2)
        for i, wants_gabor in enumerate((True, False)):
            module = pipeline.modules()[i]
            self.assertTrue(isinstance(module, M.MeasureTexture))
            self.assertEqual(len(module.image_groups), 2)
            self.assertEqual(module.image_groups[0].image_name, "rawDNA")
            self.assertEqual(module.image_groups[1].image_name, "rawGFP")
            self.assertEqual(len(module.object_groups), 2)
            self.assertEqual(module.object_groups[0].object_name, "Cells")
            self.assertEqual(module.object_groups[1].object_name, "Nuclei")
            self.assertEqual(len(module.scale_groups), 2)
            self.assertEqual(module.scale_groups[0].scale, 3)
            angles = module.scale_groups[0].angles.get_selections()
            self.assertEqual(len(angles),2)
            self.assertTrue(M.H_HORIZONTAL in angles)
            self.assertTrue(M.H_VERTICAL in angles)
            
            angles = module.scale_groups[1].angles.get_selections()
            self.assertEqual(len(angles),2)
            self.assertTrue(M.H_DIAGONAL in angles)
            self.assertTrue(M.H_ANTIDIAGONAL in angles)
            
            self.assertEqual(module.scale_groups[1].scale, 5)
            self.assertEqual(module.wants_gabor, wants_gabor)
            self.assertEqual(module.gabor_angles, 6)
            self.assertEqual(module.images_or_objects, M.IO_BOTH)
            
    def test_01_04_load_v4(self):
        data = """CellProfiler Pipeline: http://www.cellprofiler.org
Version:3
DateRevision:20141017202435
GitHash:b261e94
ModuleCount:3
HasImagePlaneDetails:False

MeasureTexture:[module_num:1|svn_version:\'Unknown\'|variable_revision_number:4|show_window:True|notes:\x5B\x5D|batch_state:array(\x5B\x5D, dtype=uint8)|enabled:True|wants_pause:False]
    Hidden:2
    Hidden:2
    Hidden:2
    Select an image to measure:rawDNA
    Select an image to measure:rawGFP
    Select objects to measure:Cells
    Select objects to measure:Nuclei
    Texture scale to measure:3
    Angles to measure:Horizontal,Vertical
    Texture scale to measure:5
    Angles to measure:Diagonal,Anti-diagonal
    Measure Gabor features?:Yes
    Number of angles to compute for Gabor:6
    Measure images or objects?:Images

MeasureTexture:[module_num:2|svn_version:\'Unknown\'|variable_revision_number:4|show_window:True|notes:\x5B\x5D|batch_state:array(\x5B\x5D, dtype=uint8)|enabled:True|wants_pause:False]
    Hidden:2
    Hidden:2
    Hidden:2
    Select an image to measure:rawDNA
    Select an image to measure:rawGFP
    Select objects to measure:Cells
    Select objects to measure:Nuclei
    Texture scale to measure:3
    Angles to measure:Horizontal,Vertical
    Texture scale to measure:5
    Angles to measure:Diagonal,Anti-diagonal
    Measure Gabor features?:No
    Number of angles to compute for Gabor:6
    Measure images or objects?:Objects

MeasureTexture:[module_num:3|svn_version:\'Unknown\'|variable_revision_number:4|show_window:True|notes:\x5B\x5D|batch_state:array(\x5B\x5D, dtype=uint8)|enabled:True|wants_pause:False]
    Hidden:2
    Hidden:2
    Hidden:2
    Select an image to measure:rawDNA
    Select an image to measure:rawGFP
    Select objects to measure:Cells
    Select objects to measure:Nuclei
    Texture scale to measure:3
    Angles to measure:Horizontal,Vertical
    Texture scale to measure:5
    Angles to measure:Diagonal,Anti-diagonal
    Measure Gabor features?:No
    Number of angles to compute for Gabor:6
    Measure images or objects?:Both
"""
        pipeline = cpp.Pipeline()
        def callback(caller, event):
            self.assertFalse(isinstance(event, cpp.LoadExceptionEvent))
        pipeline.add_listener(callback)
        pipeline.load(StringIO(data))
        self.assertEqual(len(pipeline.modules()),3)
        for i, (wants_gabor, io_choice) in enumerate(
            ((True, M.IO_IMAGES),
             (False, M.IO_OBJECTS),
             (False, M.IO_BOTH))):
            module = pipeline.modules()[i]
            self.assertTrue(isinstance(module, M.MeasureTexture))
            self.assertEqual(len(module.image_groups), 2)
            self.assertEqual(module.image_groups[0].image_name, "rawDNA")
            self.assertEqual(module.image_groups[1].image_name, "rawGFP")
            self.assertEqual(len(module.object_groups), 2)
            self.assertEqual(module.object_groups[0].object_name, "Cells")
            self.assertEqual(module.object_groups[1].object_name, "Nuclei")
            self.assertEqual(len(module.scale_groups), 2)
            self.assertEqual(module.scale_groups[0].scale, 3)
            angles = module.scale_groups[0].angles.get_selections()
            self.assertEqual(len(angles),2)
            self.assertTrue(M.H_HORIZONTAL in angles)
            self.assertTrue(M.H_VERTICAL in angles)
            
            angles = module.scale_groups[1].angles.get_selections()
            self.assertEqual(len(angles),2)
            self.assertTrue(M.H_DIAGONAL in angles)
            self.assertTrue(M.H_ANTIDIAGONAL in angles)
            
            self.assertEqual(module.scale_groups[1].scale, 5)
            self.assertEqual(module.wants_gabor, wants_gabor)
            self.assertEqual(module.gabor_angles, 6)
        
    def test_02_02_many_objects(self):
        '''Regression test for IMG-775'''
        np.random.seed(22)
        image=np.random.uniform(size=(100,100))
        i,j = np.mgrid[0:100,0:100]
        labels = (i/10).astype(int) + (j/10).astype(int) * 10 + 1
        workspace, module = self.make_workspace(image, labels)
        self.assertTrue(isinstance(module, M.MeasureTexture))
        module.scale_groups[0].scale.value = 2
        module.scale_groups[0].angles.value = ",".join(M.H_ALL)
        module.run(workspace)
        m = workspace.measurements
        all_measurements = module.get_measurements(
            workspace.pipeline, INPUT_OBJECTS_NAME, M.TEXTURE)
        all_columns = module.get_measurement_columns(workspace.pipeline)
        self.assertTrue(all([oname in (INPUT_OBJECTS_NAME, cpmeas.IMAGE)
                             for oname, feature, coltype in all_columns]))
        all_column_features = [
            feature for oname, feature, coltype in all_columns
            if oname == INPUT_OBJECTS_NAME]
        self.assertTrue(all([any([oname == cpmeas.IMAGE and feature == afeature
                                  for oname, feature, coltype in all_columns])
                             for afeature in all_column_features]))
        for measurement in M.F_HARALICK:
            self.assertTrue(measurement in all_measurements)
            self.assertTrue(
                INPUT_IMAGE_NAME in module.get_measurement_images(
                    workspace.pipeline, INPUT_OBJECTS_NAME, M.TEXTURE, measurement))
            all_scales = module.get_measurement_scales(
                workspace.pipeline, INPUT_OBJECTS_NAME, M.TEXTURE,
                measurement, INPUT_IMAGE_NAME)
            for angle in M.H_ALL:
                mname = '%s_%s_%s_%d_%s'%(
                    M.TEXTURE, measurement, INPUT_IMAGE_NAME, 2, M.H_TO_A[angle])
                self.assertTrue(mname in all_column_features)
                values = m.get_current_measurement(INPUT_OBJECTS_NAME, mname)
                self.assertTrue(np.all(values != 0))
                self.assertTrue("%d_%s" % (2, M.H_TO_A[angle]) in all_scales)
        
    def test_03_01_gabor_null(self):
        '''Test for no score on a uniform image'''
        image = np.ones((10,10))*.5
        labels = np.ones((10,10),int)
        workspace, module = self.make_workspace(image, labels)
        module.scale_groups[0].scale.value = 2
        module.run(workspace)
        mname = '%s_%s_%s_%d'%(M.TEXTURE, M.F_GABOR, INPUT_IMAGE_NAME, 2)
        m = workspace.measurements.get_current_measurement(INPUT_OBJECTS_NAME, 
                                                           mname)
        self.assertEqual(len(m), 1)
        self.assertAlmostEqual(m[0], 0)
    
    def test_03_02_gabor_horizontal(self):
        '''Compare the Gabor score on the horizontal with the one on the diagonal'''
        i,j = np.mgrid[0:10,0:10]
        labels = np.ones((10,10),int)
        himage = np.cos(np.pi*i)*.5 + .5
        dimage = np.cos(np.pi*(i-j)/np.sqrt(2)) * .5 + .5
        def run_me(image, angles):
            workspace, module = self.make_workspace(image, labels)
            module.scale_groups[0].scale.value = 2
            module.gabor_angles.value = angles
            module.run(workspace)
            mname = '%s_%s_%s_%d'%(M.TEXTURE, M.F_GABOR, INPUT_IMAGE_NAME, 2)
            m = workspace.measurements.get_current_measurement(INPUT_OBJECTS_NAME, 
                                                               mname)
            self.assertEqual(len(m), 1)
            return m[0]
        himage_2, himage_4, dimage_2, dimage_4 = [run_me(image, angles)
                                                  for image, angles in
                                                  ((himage, 2),(himage,4),
                                                   (dimage, 2),(dimage,4))]
        self.assertAlmostEqual(himage_2, himage_4)
        self.assertAlmostEqual(dimage_2, 0)
        self.assertNotAlmostEqual(dimage_4,0)
        
    def test_03_02_01_gabor_off(self):
        '''Make sure we can run MeasureTexture without gabor feature'''
        workspace, module = self.make_workspace(np.zeros((10,10)),
                                                np.zeros((10,10),int))
        self.assertTrue(isinstance(module, M.MeasureTexture))
        module.wants_gabor.value = False
        module.run(workspace)
        m = workspace.measurements
        self.assertTrue(isinstance(m, cpmeas.Measurements))
        for object_name in (cpmeas.IMAGE, INPUT_OBJECTS_NAME):
            features = m.get_feature_names(object_name)
            self.assertTrue(all([f.find(M.F_GABOR) == -1 for f in features]))
        
    def test_03_03_measurement_columns(self):
        '''Check that results of get_measurement_columns match the actual column names output'''
        r = np.random.RandomState()
        r.seed(33)
        image = r.uniform(size=(20, 20))
        labels = np.zeros((20, 20), int)
        labels[2:10, 2:10] = 1
        workspace, module = self.make_workspace(image, labels)
        module.run(workspace)
        measurements = workspace.measurements
        for x in module.get_measurement_columns(None):
            assert x[1] in measurements.get_feature_names(x[0]), '%s does not match any measurement output by pipeline'%(str(x))
        for obname in measurements.get_object_names():
            for m in measurements.get_feature_names(obname):
                if m.startswith(M.TEXTURE):
                    assert (obname, m, 'float') in module.get_measurement_columns(None), 'no entry matching %s in get_measurement_columns.'%((obname, m, 'float'))

    def test_03_04_measurement_columns_with_and_without_gabor(self):
        workspace, module = self.make_workspace(np.zeros((10,10)),
                                                np.zeros((10,10),int))
        self.assertTrue(isinstance(module, M.MeasureTexture))
        module.wants_gabor.value = True
        columns = module.get_measurement_columns(None)
        ngabor = len(['x' for c in columns if c[1].find(M.F_GABOR) >= 0])
        self.assertEqual(ngabor, 2)
        module.wants_gabor.value = False
        columns = module.get_measurement_columns(None)
        ngabor = len(['x' for c in columns if c[1].find(M.F_GABOR) >= 0])
        self.assertEqual(ngabor, 0)
        
    def test_03_05_categories(self):
        workspace, module = self.make_workspace(np.zeros((10,10)),
                                                np.zeros((10,10),int))
        self.assertTrue(isinstance(module, M.MeasureTexture))
        for has_category, object_name in ((True, cpmeas.IMAGE),
                                          (True, INPUT_OBJECTS_NAME),
                                          (False, "Foo")):
            categories = module.get_categories(workspace.pipeline, object_name)
            if has_category:
                self.assertEqual(len(categories), 1)
                self.assertEqual(categories[0], M.TEXTURE)
            else:
                self.assertEqual(len(categories), 0)
        module.images_or_objects.value = M.IO_IMAGES
        categories = module.get_categories(workspace.pipeline, cpmeas.IMAGE)
        self.assertEqual(len(categories), 1)
        categories = module.get_categories(
            workspace.pipeline, INPUT_OBJECTS_NAME)
        self.assertEqual(len(categories), 0)
        module.images_or_objects.value = M.IO_OBJECTS
        categories = module.get_categories(workspace.pipeline, cpmeas.IMAGE)
        self.assertEqual(len(categories), 0)
        categories = module.get_categories(
            workspace.pipeline, INPUT_OBJECTS_NAME)
        self.assertEqual(len(categories), 1)
        
    
    def test_03_06_measuremements(self):
        workspace, module = self.make_workspace(np.zeros((10,10)),
                                                np.zeros((10,10),int))
        self.assertTrue(isinstance(module, M.MeasureTexture))
        for wants_gabor in (False, True):
            module.wants_gabor.value = wants_gabor
            for object_name in (cpmeas.IMAGE, INPUT_OBJECTS_NAME):
                features = module.get_measurements(workspace.pipeline,
                                                   object_name, M.TEXTURE)
                self.assertTrue(all([f in M.F_HARALICK + [M.F_GABOR]
                                     for f in features]))
                self.assertTrue(all([f in features for f in M.F_HARALICK]))
                if wants_gabor:
                    self.assertTrue(M.F_GABOR in features)
                else:
                    self.assertFalse(M.F_GABOR in features)
        
    def test_04_01_zeros(self):
        '''Make sure the module can run on an empty labels matrix'''
        workspace, module = self.make_workspace(np.zeros((10,10)),
                                                np.zeros((10,10),int))
        module.run(workspace)
        m = workspace.measurements
        self.assertTrue(isinstance(m, cpmeas.Measurements))
        for f in m.get_feature_names(INPUT_OBJECTS_NAME):
            if f.startswith(M.TEXTURE):
                values = m.get_current_measurement(INPUT_OBJECTS_NAME, f)
                self.assertEqual(len(values),0)
                
    def test_04_02_wrong_size(self):
        '''Regression test for IMG-961: objects & image different size'''
        np.random.seed(42)
        image = np.random.uniform(size=(10,30))
        labels = np.ones((20,20), int)
        workspace, module = self.make_workspace(image, labels)
        module.run(workspace)
        m = workspace.measurements
        workspace, module = self.make_workspace(image[:,:20], labels[:10,:])
        module.run(workspace)
        me = workspace.measurements
        for f in m.get_feature_names(INPUT_OBJECTS_NAME):
            if f.startswith(M.TEXTURE):
                values = m.get_current_measurement(INPUT_OBJECTS_NAME, f)
                expected = me.get_current_measurement(INPUT_OBJECTS_NAME, f)
                self.assertEqual(values, expected)
    
    def test_04_03_mask(self):
        np.random.seed(42)
        image = np.random.uniform(size=(10,30))
        mask = np.zeros(image.shape, bool)
        mask[:,:20] = True
        labels = np.ones((10,30), int)
        workspace, module = self.make_workspace(image, labels, mask = mask)
        module.run(workspace)
        m = workspace.measurements
        workspace, module = self.make_workspace(image[:,:20], labels[:,:20])
        module.run(workspace)
        me = workspace.measurements
        for f in m.get_feature_names(INPUT_OBJECTS_NAME):
            if f.startswith(M.TEXTURE):
                values = m.get_current_measurement(INPUT_OBJECTS_NAME, f)
                expected = me.get_current_measurement(INPUT_OBJECTS_NAME, f)
                self.assertEqual(values, expected)

    def test_04_04_no_image_measurements(self):
        image = np.ones((10,10))*.5
        labels = np.ones((10,10),int)
        workspace, module = self.make_workspace(image, labels)
        assert isinstance(module, M.MeasureTexture)
        module.images_or_objects.value = M.IO_OBJECTS
        module.scale_groups[0].scale.value = 2
        module.run(workspace)
        m = workspace.measurements
        self.assertFalse(
            m.has_feature(
                cpmeas.IMAGE, 
                "Texture_AngularSecondMoment_%s_2_0" % INPUT_IMAGE_NAME))
        self.assertTrue(
            m.has_feature(
                INPUT_OBJECTS_NAME, 
                "Texture_AngularSecondMoment_%s_2_0" % INPUT_IMAGE_NAME))
    
    def test_04_05_no_object_measurements(self):
        image = np.ones((10,10))*.5
        labels = np.ones((10,10),int)
        workspace, module = self.make_workspace(image, labels)
        assert isinstance(module, M.MeasureTexture)
        module.images_or_objects.value = M.IO_IMAGES
        module.scale_groups[0].scale.value = 2
        module.run(workspace)
        m = workspace.measurements
        self.assertTrue(
            m.has_feature(
                cpmeas.IMAGE, 
                "Texture_AngularSecondMoment_%s_2_0" % INPUT_IMAGE_NAME))
        self.assertFalse(
            m.has_feature(
                INPUT_OBJECTS_NAME, 
                "Texture_AngularSecondMoment_%s_2_0" % INPUT_IMAGE_NAME))