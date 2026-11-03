import math
from pathlib import Path
import tempfile
import unittest
from collections import Counter
from sketch_bloom import geometry as g

class GeometryTests(unittest.TestCase):
    def assert_solid(self,mesh):
        g.validate_mesh(mesh)
        edges=Counter()
        directions=Counter()
        for face in mesh[1]:
            for a,b in zip(face,face[1:]+face[:1]):
                edges[tuple(sorted((a,b)))]+=1; directions[(a,b)]+=1
        self.assertTrue(all(n==2 for n in edges.values()))
        self.assertTrue(all(directions[(a,b)]==directions[(b,a)] for a,b in directions))
        # Signed volume checks outward winding as well as connectivity.
        volume=0
        v=mesh[0]
        for f in mesh[1]:
            for i in range(1,len(f)-1): volume+=g._dot(v[f[0]],g._cross(v[f[i]],v[f[i+1]]))/6
        self.assertGreater(volume,0)
    def test_tube_counts_and_winding(self):
        for count,sides in [(16,6),(96,12)]:
            mesh=g.tube(g.sample([(0,0,0),(0,2,0)],count,False),.12,sides)
            self.assertEqual(len(mesh[1]),(count-1)*sides+2); self.assert_solid(mesh)
    def test_cup_and_density(self):
        low=g.teacup(True); high=g.teacup(False)
        self.assertLess(sum(len(m[1]) for _,m in low),sum(len(m[1]) for _,m in high))
        for _,mesh in low+high: self.assert_solid(mesh)
    def test_concave_fill(self):
        mesh=g.filled_outline([(0,0),(2,0),(2,1),(1,.4),(0,1)],.4,2)
        self.assertEqual(len(mesh[1]),16); self.assert_solid(mesh)
    def test_crossing_rejected(self):
        with self.assertRaises(ValueError): g.filled_outline([(0,0),(1,1),(0,1),(1,0)])
    def test_preset_library(self):
        for name in ['Circle','Square','Heart','Star','Leaf','Flower','Cat','Fish','House']:
            for tolerance in [.045,.003]:
                with self.subTest(name=name,tolerance=tolerance):
                    self.assert_solid(g.filled_outline(g.simplify_path(g.preset_outline(name),tolerance,True)))
        for name in g.ANIMAL_BODIES:
            self.assertTrue(g.animal_outline(name,True))
    def test_obj_offsets(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as folder:
            path=Path(folder)/'cup.obj'; meshes=g.teacup(); g.write_obj(path,meshes)
            lines=path.read_text().splitlines(); vertices=[l for l in lines if l.startswith('v ')]; faces=[l for l in lines if l.startswith('f ')]
            self.assertEqual(len(vertices),sum(len(m[0]) for _,m in meshes))
            self.assertEqual(len(faces),sum(len(m[1]) for _,m in meshes))
            self.assertEqual(len([l for l in lines if l.startswith('o ')]),2)
            for f in faces: self.assertTrue(all(1<=int(i)<=len(vertices) for i in f.split()[1:]))
    def test_invalid_input(self):
        for points in [[],[(0,0,0)],[(0,0,0),(0,0,0)]]:
            with self.assertRaises(ValueError): g.tube(points,.1,6)
        with self.assertRaises(ValueError): g.tube([(0,0,0),(0,1,0)],-1,6)

if __name__=='__main__': unittest.main()

