import unittest
import os
import shutil
import random
from thermoproblems.answerset import AnswerSet,AnswerSuperSet
import logging
from glob import glob

logger=logging.getLogger(__name__)
class AnswerSetTests(unittest.TestCase):
    def test_answerset_init(self):
        A=AnswerSet(1234567)
        self.assertEqual(A.serial,1234567)
        self.assertEqual(A.dumpname,'answers-01234567.yaml')
        self.assertTrue(A.D=={})
    def test_answerset_register(self):
        A=AnswerSet(999)
        A.register(1,label='$V$',units='m$^3$',value=101.4)
        self.assertEqual(len(A.D[1]),1)
        A.register(1,label='$V1$',units='m$^3$',value=102.4)
        self.assertEqual(len(A.D[1]),2)
        A.register(2,label='X',units=None,value=-909.0)
        self.assertEqual(len(A.D),2)
    def test_answerset_dump(self):
        A=AnswerSet(999)
        A.register(1,label='$V1$',units='m$^3$',value=101.4)
        A.register(1,label='$V2$',units='m$^3$',value=102.4)
        A.register(2,label='X',units=None,value=-909.0)
        A.register(3,label='TF',units=None,value=True)
        A.register(3,label='TF',units=None,value=False)
        A.register(3,label='TF',units=None,value=True)
        A.register(3,label='TF',units=None,value=False)
        A.register(3,label='TF',units=None,value=True)
        A.to_yaml()
        self.assertTrue(os.path.exists('answers-00000999.yaml'))
    def test_answerset_read(self):
        A=AnswerSet.from_yaml('answers-00000999.yaml')
        self.assertEqual(A.serial,999)
        self.assertEqual(len(A.D),3)
        self.assertEqual(len(A.D[3]),5)

class AnswerSuperSetTests(unittest.TestCase):
    def make_superset(self):
        files=[]
        serials=[random.randint(10000000,99999999) for _ in range(10)]
        for s in serials:
            A=AnswerSet(s)
            TF=[random.choice([True,False]) for _ in range(10)]
            for l,t in zip([chr(ord('a')+i) for i in range(10)],TF):
                A.register(1,label=l,value='T' if t else 'F')
            A.register(2,label='XXX',units='monkeys',value=int(random.randint(0,100)))
            A.register(3,label='YYY',units='hippos',value=int(random.randint(0,100)))
            A.register(4,label='energy',units='kJ',value=round(float(random.random()*1000.0),1),formatter='{:.1f}')
            A.register(4,label='entropy',units='kJ/K',value=round(float(random.random()*10.0),4),formatter='{:.4f}')
            A.to_yaml()
            files.append(A.dumpname)
        return files
    
    def test_superset(self):
        oldfiles=glob('answers-*.yaml')
        for f in oldfiles:
            os.remove(f)
        files=self.make_superset()
        self.assertEqual(len(files),10)
        S=AnswerSuperSet(files)
        for f in files:
            os.remove(f)
        self.assertEqual(len(S),10)
        logger.debug(S.to_latex())
