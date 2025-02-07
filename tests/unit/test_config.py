import unittest
import os
from pygacity.config import Config, ResourceManager

class ConfigTest(unittest.TestCase):
    def test_resource_manager(self):
        rm=ResourceManager()
        for r in ['autoprob-package','data','examples','templates']:
            self.assertTrue(r in rm)
        badresourcename='non-existent-resource'
        self.assertFalse(badresourcename in rm)
    
    def test_config_base(self):
        c=Config()
        self.assertTrue('Resources' in c)
        self.assertEqual(type(c['Resources']),ResourceManager)
        self.assertTrue('base' in c)
        self.assertTrue('user' in c)
        cdict=c['user']
        for cat in ['paths','document']:
            self.assertTrue(cat in cdict)
        document=cdict['document']
        self.assertEqual(type(document),dict)
        dockeys=list(document.keys())
        for comp in ['metadata','type','structure','class','packages']:
            self.assertTrue(comp in dockeys)
        self.assertEqual(len(dockeys),5)
        build=cdict['build']
        self.assertEqual(build['copies'],1)
        self.assertEqual(len(build['serials']),1)
        self.assertEqual(build['solutions'],True)
        self.assertEqual(build['overwrite'],False)
        self.assertEqual(build['output-dir'],'build')
        self.assertEqual(build['output-name'],'tpdoc')

    def test_config_user1(self):
        c=Config('exam_description1.yaml')
        self.assertTrue('Resources' in c)
        cdict=c['user']
        doc=cdict['document']
        struct=doc['structure']
        self.assertTrue(len(struct)==3)
        self.assertTrue(list(struct[0].keys())[0]=='include')
        include1=struct[0]['include']
        self.assertEqual(include1,'head.tex')
        self.assertTrue(list(struct[1].keys())[0]=='items')
        self.assertTrue(list(struct[-1].keys())[0]=='include')
        include2=struct[-1]['include']
        self.assertEqual(include2,'tail.tex')
        items=list(struct[1]['items'])
        self.assertEqual(len(items),4)
        template1=items[0]['template']
        self.assertEqual(template1['source'],'true_false.tex')
        self.assertEqual(template1['config'],'true_false.yaml')
        self.assertEqual(template1['points'],15)
        template2=items[1]['template']
        self.assertEqual(template2['source'],'tank_volume.tex')
        self.assertEqual(template2['points'],15)
        template3=items[2]['template']
        self.assertEqual(template3['source'],'adiabatic_compressor.tex')
        self.assertEqual(template3['points'],35)
        template4=items[3]['template']
        self.assertEqual(template4['source'],'steam_release.tex')
        self.assertEqual(template4['points'],35)
        metadata=doc['metadata']
        self.assertTrue(metadata['Termcode']==202425)
        self.assertTrue(metadata['Termname']=="Winter 2024-2025")
        self.assertTrue('document' in cdict)
        self.assertEqual(doc['type'],'exam')

        build=c.build
        self.assertTrue('serials' in build)
        self.assertTrue(hasattr(c,'ncopies'))
        self.assertEqual(len(build['serials']),c.ncopies)
        self.assertTrue(all([x>=10000000 for x in build['serials']]))
        self.assertTrue(all([x<=99999999 for x in build['serials']]))
        self.assertTrue(os.path.exists('exam-serials.dat'))
        with open('exam-serials.dat','r') as f:
            serial_str=f.read()
        serials=list(map(int,serial_str.split()))
        self.assertTrue(all([x==y for x,y in zip(build['serials'],serials)]))

    def test_config_user2(self):
        c=Config('exam_description2.yaml')
        cdict=c['user']
        build=cdict['build']
        self.assertEqual(len(build['serials']),1)
        self.assertEqual(build['serials'][0],12345678)

    def test_config_user3(self):
        c=Config('exam_description3.yaml')
        cdict=c['user']
        build=cdict['build']
        self.assertEqual(len(build['serials']),18)

    def test_config_user4(self):
        c=Config('exam_description4.yaml')
        self.assertTrue(os.path.exists('serials4.dat'))
        with open('serials4.dat','r') as f:
            serials=list(map(int,f.read().split()))
            self.assertEqual(c.ncopies,len(serials))
        os.remove('serials4.dat')

