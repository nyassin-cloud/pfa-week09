"""Shared geometry: standard library only; coordinates are Y-up."""
import math

def cross(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])

def simplify_path(points,tolerance,closed=False):
    """Remove input jitter without cutting across important outline corners."""
    clean=[]
    for p in points:
        if not clean or math.dist(clean[-1],p)>1e-8: clean.append(tuple(p))
    if closed and len(clean)>2 and math.dist(clean[0],clean[-1])<tolerance: clean.pop()
    def reduce_line(pts):
        if len(pts)<3: return pts
        a,b=pts[0],pts[-1]; dx,dy=b[0]-a[0],b[1]-a[1]; length=dx*dx+dy*dy
        distances=[]
        for p in pts[1:-1]:
            t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/max(length,1e-20)))
            distances.append(math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy))
        index=max(range(len(distances)),key=distances.__getitem__)+1
        if distances[index-1]<=tolerance: return [a,b]
        return reduce_line(pts[:index+1])[:-1]+reduce_line(pts[index:])
    if len(clean)<4: return clean
    if closed:
        split=max(range(1,len(clean)),key=lambda i:math.dist(clean[0],clean[i]))
        return reduce_line(clean[:split+1])[:-1]+reduce_line(clean[split:]+[clean[0]])[:-1]
    return reduce_line(clean)

def triangulate(points):
    """Ear clipping, rejecting crossing/degenerate outlines."""
    n = len(points)
    if n < 3:
        raise ValueError('Draw a larger outline to see your mesh.')
    for i in range(n):
        a, b = points[i], points[(i+1)%n]
        for j in range(i+1, n):
            if j == i+1 or (i == 0 and j == n-1):
                continue
            c, d = points[j], points[(j+1)%n]
            if cross(a,b,c)*cross(a,b,d) <= 0 and cross(c,d,a)*cross(c,d,b) <= 0:
                if max(min(a[0],b[0]),min(c[0],d[0])) <= min(max(a[0],b[0]),max(c[0],d[0])) and max(min(a[1],b[1]),min(c[1],d[1])) <= min(max(a[1],b[1]),max(c[1],d[1])):
                    raise ValueError('Your outline crosses itself. Try a single simple loop.')
    area = sum(points[i][0]*points[(i+1)%n][1] - points[(i+1)%n][0]*points[i][1] for i in range(n))
    ids = list(range(n)) if area > 0 else list(reversed(range(n)))
    faces = []
    while len(ids) > 3:
        for k, b in enumerate(ids):
            a, c = ids[k-1], ids[(k+1)%len(ids)]
            if cross(points[a],points[b],points[c]) <= 1e-8:
                continue
            if any(all(v >= -1e-8 for v in (cross(points[a],points[b],points[t]), cross(points[b],points[c],points[t]), cross(points[c],points[a],points[t]))) for t in ids if t not in (a,b,c)):
                continue
            faces.append((a,b,c))
            ids.pop(k)
            break
        else:
            raise ValueError('This outline is too thin or tangled. Try drawing it again.')
    if abs(cross(*(points[i] for i in ids))) < 1e-8:
        raise ValueError('Draw a shape with a little more area.')
    return faces + [tuple(ids)]

def sample(points, count, closed):
    if len(points)<2: raise ValueError('Draw a longer stroke.')
    lengths=[math.dist(points[i],points[(i+1)%len(points)]) for i in range(len(points) if closed else len(points)-1)]
    total=sum(lengths)
    if total<1e-8: raise ValueError('Draw a larger stroke.')
    result=[]; edge=0; start=0.0
    for i in range(count):
        target=total*i/(count if closed else count-1)
        while edge<len(lengths)-1 and start+lengths[edge]<target:
            start+=lengths[edge]; edge+=1
        a,b=points[edge],points[(edge+1)%len(points)]
        t=(target-start)/max(lengths[edge],1e-12)
        result.append(tuple(a[k]+t*(b[k]-a[k]) for k in range(len(a))))
    return result

def add_cap(vertices,faces,ring,style):
    if style=='Open': return
    if style in ('N-gons','Quads • subdivided'):
        faces.append(list(ring)); return
    center=len(vertices)
    vertices.append(tuple(sum(vertices[i][k] for i in ring)/len(ring) for k in (0,1,2)))
    if style=='Quad fan • convex':
        if len(ring)%2: raise ValueError('Quad fans need an even boundary count.')
        for i in range(0,len(ring),2): faces.append([center,ring[i],ring[(i+1)%len(ring)],ring[(i+2)%len(ring)]])
    else:
        for i in range(len(ring)): faces.append([center,ring[i],ring[(i+1)%len(ring)]])

def split_quads(vertices,faces):
    result=list(vertices); edge_points={}; output=[]
    def midpoint(a,b):
        key=tuple(sorted((a,b)))
        if key not in edge_points:
            edge_points[key]=len(result)
            result.append(tuple((vertices[a][k]+vertices[b][k])/2 for k in (0,1,2)))
        return edge_points[key]
    for face in faces:
        center=len(result)
        result.append(tuple(sum(vertices[i][k] for i in face)/len(face) for k in (0,1,2)))
        for j,index in enumerate(face):
            output.append([index,midpoint(index,face[(j+1)%len(face)]),center,midpoint(face[j-1],index)])
    return result,output

def cup_geometry(radius,height,wall,base,sides,vertical_segments):
    if wall>=radius or base>=height: raise ValueError('Cup wall must be smaller than radius, and base smaller than height.')
    profile=[(0,0),(radius,0)]
    profile.extend([(radius,height*i/vertical_segments) for i in range(1,vertical_segments+1)])
    profile.append((radius-wall,height))
    profile.extend([(radius-wall,height-(height-base)*i/vertical_segments) for i in range(1,vertical_segments+1)])
    profile.append((0,base))
    vertices=[]; rings=[]; faces=[]
    for r,y in profile:
        if r<1e-10:
            rings.append([len(vertices)]); vertices.append((0,y,0))
        else:
            ring=[]
            for j in range(sides):
                a=j*math.pi*2/sides; ring.append(len(vertices)); vertices.append((r*math.cos(a),y,r*math.sin(a)))
            rings.append(ring)
    for a,b in zip(rings,rings[1:]):
        if len(a)==1 and len(b)==1: continue
        for j in range(sides):
            k=(j+1)%sides
            if len(a)==1: faces.append([a[0],b[j],b[k]])
            elif len(b)==1: faces.append([a[j],b[0],a[k]])
            else: faces.append([a[j],b[j],b[k],a[k]])
    return vertices,faces

def preset_outline(name):
    """Simple closed silhouettes, rather than inferred 3D animal models."""
    profiles = {
        'Triangle': [(0,-1),(1,1),(-1,1)],
        'Square': [(-1,-1),(1,-1),(1,1),(-1,1)],
        'Rectangle': [(-1,-.6),(1,-.6),(1,.6),(-1,.6)],
        'Diamond': [(0,-1),(.65,0),(0,1),(-.65,0)],
        'Trapezoid': [(-.6,-1),(.6,-1),(1,1),(-1,1)],
        'Cross': [(-.3,-1),(.3,-1),(.3,-.3),(1,-.3),(1,.3),(.3,.3),(.3,1),(-.3,1),(-.3,.3),(-1,.3),(-1,-.3),(-.3,-.3)],
        'Arrow': [(-1,-.3),(.25,-.3),(.25,-.85),(1,0),(.25,.85),(.25,.3),(-1,.3)],
        'Lightning bolt': [(.1,-1),(-.8,.2),(-.15,.2),(-.4,1),(.85,-.3),(.2,-.3)],
        'Cat': [(-.85,-1),(-.35,-.65),(.35,-.65),(.85,-1),(.8,-.15),(1,.35),(.7,.85),(0,1),(-.7,.85),(-1,.35),(-.8,-.15)],
        'Dog': [(-.4,-.7),(.4,-.7),(.65,-1),(1,-.75),(.95,.3),(.6,.5),(.5,.15),(.55,.7),(.3,1),(-.3,1),(-.55,.7),(-.5,.15),(-.6,.5),(-.95,.3),(-1,-.75),(-.65,-1)],
        'Bunny': [(-.7,-1),(-.35,-.95),(-.2,-.3),(.2,-.3),(.35,-.95),(.7,-1),(.7,-.5),(.5,0),(.85,.4),(.7,.85),(0,1),(-.7,.85),(-.85,.4),(-.5,0),(-.7,-.5)],
        'Bear': [(-.8,-.25),(-1,-.65),(-.9,-.95),(-.55,-1),(-.3,-.7),(.3,-.7),(.55,-1),(.9,-.95),(1,-.65),(.8,-.25),(.95,.4),(.65,.85),(0,1),(-.65,.85),(-.95,.4)],
        'Fox': [(-1,-1),(-.25,-.6),(.25,-.6),(1,-1),(.85,.25),(0,1),(-.85,.25)],
        'Fish': [(-1,-.7),(-.45,-.25),(0,-.6),(.6,-.5),(1,0),(.6,.5),(0,.6),(-.45,.25),(-1,.7),(-.8,0)],
        'Bird': [(-1,.5),(-.4,.25),(-.8,-.6),(-.15,-.2),(.3,-.75),(.65,-.7),(.8,-.35),(1,-.2),(.7,-.05),(.5,.55),(0,.8),(-.5,.65)],
        'Whale': [(-1,-.6),(-.55,-.2),(-.25,-.6),(.4,-.8),(.85,-.55),(1,0),(.85,.55),(.4,.75),(-.2,.65),(-.55,.2),(-1,.5),(-.8,0)],
        'Turtle': [(-.8,-.35),(-1,-.65),(-.75,-.8),(-.5,-.55),(-.2,-.75),(.3,-.7),(.55,-.5),(.8,-.65),(1,-.5),(.85,-.15),(1,.05),(.85,.3),(.55,.25),(.4,.65),(.65,.8),(.4,1),(.1,.75),(-.4,.65),(-.65,.85),(-.9,.65),(-.7,.35),(-.9,0)],
        'Shoe': [(-1,-.6),(-.55,-.6),(-.45,-.1),(-.05,.1),(.6,.25),(1,.55),(.95,.85),(-1,.85)],
        'Sneaker': [(-1,-.3),(-.6,-.55),(-.25,-.15),(.05,-.35),(.45,.15),(.9,.35),(1,.6),(.95,.85),(-1,.85)],
        'Boot': [(-.9,-1),(-.15,-1),(-.15,.2),(.55,.3),(.95,.55),(1,.85),(-.9,.85)],
        'House': [(-1,-.1),(0,-1),(1,-.1),(.75,-.1),(.75,1),(-.75,1),(-.75,-.1)],
        'Crown': [(-1,-.8),(-.5,-.15),(0,-1),(.5,-.15),(1,-.8),(.75,.8),(-.75,.8)],
        'Cup': [(-.8,-.8),(.45,-.8),(.45,-.55),(.9,-.55),(1,-.2),(.95,.3),(.45,.5),(.3,.85),(-.55,.85)],
        'Bottle': [(-.3,-1),(.3,-1),(.3,-.55),(.65,-.25),(.65,.85),(.45,1),(-.45,1),(-.65,.85),(-.65,-.25),(-.3,-.55)],
        'Vase': [(-.5,-1),(.5,-1),(.35,-.4),(.8,.3),(.7,.75),(.4,1),(-.4,1),(-.7,.75),(-.8,.3),(-.35,-.4)],
        'Bag': [(-.8,-.4),(-.5,-.4),(-.5,-.8),(-.3,-1),(.3,-1),(.5,-.8),(.5,-.4),(.8,-.4),(1,1),(-1,1)],
        'T-shirt': [(-.45,-.8),(-.2,-.6),(.2,-.6),(.45,-.8),(1,-.4),(.7,.1),(.45,-.05),(.45,1),(-.45,1),(-.45,-.05),(-.7,.1),(-1,-.4)],
        'Dress': [(-.45,-1),(-.15,-.8),(.15,-.8),(.45,-1),(.6,-.55),(.3,-.2),(.25,.1),(.9,1),(-.9,1),(-.25,.1),(-.3,-.2),(-.6,-.55)],
        'Rocket': [(0,-1),(.4,-.5),(.4,.2),(.85,.7),(.85,1),(.25,.7),(-.25,.7),(-.85,1),(-.85,.7),(-.4,.2),(-.4,-.5)],
        'Car': [(-1,0),(-.65,-.1),(-.35,-.65),(.35,-.65),(.65,-.1),(.95,.05),(1,.55),(.65,.55),(.55,.85),(.3,.85),(.2,.55),(-.35,.55),(-.45,.85),(-.7,.85),(-.8,.55),(-1,.55)],
        'Bow': [(-1,-.7),(-.2,-.15),(.2,-.15),(1,-.7),(.8,0),(1,.7),(.2,.15),(-.2,.15),(-1,.7),(-.8,0)],
        'Tulip': [(-.8,-1),(-.35,-.6),(0,-1),(.35,-.6),(.8,-1),(.65,-.2),(.15,.15),(.15,.5),(.65,.2),(.45,.7),(.15,.8),(.15,1),(-.15,1),(-.15,.85),(-.45,.75),(-.65,.25),(-.15,.55),(-.15,.15),(-.65,-.2)],
        'Tree': [(-.2,1),(-.2,.35),(-.75,.4),(-1,0),(-.8,-.5),(-.35,-.65),(0,-1),(.4,-.8),(.55,-.5),(.9,-.35),(1,.1),(.7,.4),(.2,.35),(.2,1)],
        'Pine tree': [(0,-1),(.55,-.35),(.3,-.35),(.8,.25),(.45,.25),(1,.8),(.2,.8),(.2,1),(-.2,1),(-.2,.8),(-1,.8),(-.45,.25),(-.8,.25),(-.3,-.35),(-.55,-.35)],
        'Mountain': [(-1,1),(-.3,-1),(.05,-.1),(.4,-.65),(1,1)],
        'Mushroom': [(-1,.1),(-.9,-.5),(-.5,-.9),(0,-1),(.5,-.9),(.9,-.5),(1,.1),(.3,.1),(.45,1),(-.45,1),(-.3,.1)],
    }
    if name in profiles: raw=profiles[name]
    elif name in ('Pentagon','Hexagon','Octagon'):
        count={'Pentagon':5,'Hexagon':6,'Octagon':8}[name]
        raw=[(math.cos(2*math.pi*i/count-math.pi/2),math.sin(2*math.pi*i/count-math.pi/2)) for i in range(count)]
    elif name=='Rounded rectangle':
        raw=[]
        for cx,cy,start in [(.65,-.45,-90),(.65,.45,0),(-.65,.45,90),(-.65,-.45,180)]:
            for i in range(13):
                a=math.radians(start+i*90/12); raw.append((cx+.25*math.cos(a),cy+.25*math.sin(a)))
    elif name=='Cloud':
        # One outline assembled from an upper scalloped edge and a flat base.
        raw=[(-.95,.5),(-1,.15),(-.9,-.2),(-.6,-.3),(-.5,-.65),(-.2,-.85),(.15,-.8),(.35,-.5),(.65,-.55),(.9,-.3),(1,.15),(.9,.5)]
    elif name=='Moon':
        raw=[(math.cos(a),math.sin(a)) for a in [math.radians(65+230*i/64) for i in range(65)]]
        bottom,top=raw[-1],raw[0]
        raw.extend([(bottom[0]-.85*math.sin(math.pi*t),bottom[1]+(top[1]-bottom[1])*t) for t in [i/64 for i in range(1,64)]])
    else:
        raw=[]; count=160
        for i in range(count):
            t=2*math.pi*i/count
            if name=='Heart': x=16*math.sin(t)**3/17; y=-(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))/17
            elif name=='Star':
                # Use exact corners below rather than a wavy star.
                continue
            elif name in ('Flower','Daisy','Sunflower','Sun','Butterfly'):
                petals={'Flower':5,'Daisy':8,'Sunflower':12,'Sun':16,'Butterfly':4}[name]
                r=.72+.25*math.cos(petals*t); x=r*math.cos(t); y=r*math.sin(t)
                if name=='Butterfly': x*=1.15; y*=.85
            elif name=='Leaf': x=.55*math.sin(t); y=math.cos(t)*(1+.15*math.sin(t))
            elif name=='Raindrop': x=.7*math.sin(t)*(1-.45*math.cos(t)); y=-math.cos(t)
            elif name=='Balloon': x=.7*math.cos(t); y=.85*math.sin(t)
            else: x=math.cos(t); y=math.sin(t)*(.65 if name=='Oval' else 1)
            raw.append((x,y))
        if name=='Star': raw=[((1 if i%2==0 else .45)*math.cos(i*math.pi/5-math.pi/2),(1 if i%2==0 else .45)*math.sin(i*math.pi/5-math.pi/2)) for i in range(10)]
    lo=[min(p[k] for p in raw) for k in (0,1)]; hi=[max(p[k] for p in raw) for k in (0,1)]
    scale=.8/max(hi[0]-lo[0],hi[1]-lo[1])
    return [(.5+(x-(lo[0]+hi[0])/2)*scale,.5+(y-(lo[1]+hi[1])/2)*scale) for x,y in raw]

def animal_outline(name,full_body=False,realistic=False):
    if full_body:
        raw=list(ANIMAL_BODIES[name])
        if realistic:
            # Longer torsos and narrower limbs; smooth silhouettes rather than cartoon corners.
            raw=[(x*1.25,y*.9) for x,y in raw]
    else:
        if realistic and name in ('Dog','Fox'):
            raw=[(-1,-.7),(-.6,-1),(-.25,-.7),(.2,-.65),(.4,-.3),(1,-.05),(.95,.25),(.45,.4),(.15,.85),(-.4,1),(-.75,.55),(-.9,0)]
        elif realistic and name=='Cat':
            raw=[(-.85,-1),(-.35,-.65),(.3,-.65),(.8,-1),(.75,-.15),(.95,.2),(.6,.55),(.25,.65),(0,.85),(-.3,.65),(-.65,.55),(-.95,.2),(-.75,-.15)]
        elif name in ('Cat','Dog','Bunny','Bear','Fox'):
            raw=preset_outline(name)
        elif name=='Bird': raw=[(-.7,-.8),(-.1,-1),(.4,-.75),(.5,-.25),(1,0),(.45,.2),(.2,.8),(-.5,1),(-.85,.3)]
        elif name in ('Fish','Whale','Turtle'):
            raw=[(math.cos(i*math.pi/32),math.sin(i*math.pi/32)*(.7 if name!='Turtle' else .9)) for i in range(64)]
        else:
            raw=[(-.8,-1),(-.4,-.9),(-.2,-.35),(.2,-.35),(.4,-.9),(.8,-1),(.55,-.55),(.45,.1),(.65,.5),(.3,1),(-.3,1),(-.65,.5),(-.45,.1),(-.55,-.55)]
    if realistic:
        for unused in range(2):
            smooth=[]
            for a,b in zip(raw,raw[1:]+raw[:1]):
                smooth.extend([(a[0]*.8+b[0]*.2,a[1]*.8+b[1]*.2),(a[0]*.2+b[0]*.8,a[1]*.2+b[1]*.8)])
            raw=smooth
    lo=[min(p[k] for p in raw) for k in (0,1)]; hi=[max(p[k] for p in raw) for k in (0,1)]
    scale=.8/max(hi[0]-lo[0],hi[1]-lo[1])
    return [(.5+(x-(lo[0]+hi[0])/2)*scale,.5+(y-(lo[1]+hi[1])/2)*scale) for x,y in raw]

def _sub(a,b): return tuple(x-y for x,y in zip(a,b))
def _dot(a,b): return sum(x*y for x,y in zip(a,b))
def _cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def _unit(a):
    length=math.sqrt(_dot(a,a))
    if length<1e-10: raise ValueError('Path has a degenerate tangent.')
    return tuple(x/length for x in a)

def tube(points,radius,sides):
    """Parallel-transport-like tube rings; closed caps, zero-based face indices."""
    if radius<=0 or sides<3 or int(sides)!=sides: raise ValueError('Positive radius and at least three integer sides required.')
    pts=[]
    for p in points:
        if len(p)!=3 or not all(math.isfinite(x) for x in p): raise ValueError('Expected finite 3D points.')
        if not pts or math.dist(p,pts[-1])>1e-9: pts.append(tuple(p))
    if len(pts)<2: raise ValueError('Draw a longer stroke.')
    vertices=[]; faces=[]; normal=None
    for i,center in enumerate(pts):
        delta=_sub(pts[min(i+1,len(pts)-1)],pts[max(0,i-1)])
        if _dot(delta,delta)<1e-18: delta=_sub(pts[min(i+1,len(pts)-1)],center)
        tangent=_unit(delta)
        if normal is not None:
            projection=_dot(normal,tangent)
            normal=tuple(normal[k]-tangent[k]*projection for k in range(3))
        if normal is None or _dot(normal,normal)<1e-12:
            normal=_cross(tangent,(0,1,0) if abs(tangent[1])<.9 else (1,0,0))
        normal=_unit(normal); binormal=_unit(_cross(tangent,normal))
        for j in range(sides):
            a=j*math.tau/sides
            vertices.append(tuple(center[k]+radius*(normal[k]*math.cos(a)+binormal[k]*math.sin(a)) for k in range(3)))
    for i in range(len(pts)-1):
        for j in range(sides):
            k=(j+1)%sides
            # Ring basis normal x binormal points along the tangent.
            faces.append([i*sides+j,i*sides+k,(i+1)*sides+k,(i+1)*sides+j])
    faces.extend([list(reversed(range(sides))),[(len(pts)-1)*sides+j for j in range(sides)]])
    return vertices,faces

def filled_outline(points,depth=.4,layers=1):
    """Extrude a simple XY outline along Z; no holes or crossing contours."""
    if depth<=0 or layers<1: raise ValueError('Positive depth and at least one layer required.')
    loop=simplify_path(points,1e-7,True)
    if len(loop)>2048: raise ValueError('Outline exceeds 2048 points.')
    if sum(loop[i][0]*loop[(i+1)%len(loop)][1]-loop[(i+1)%len(loop)][0]*loop[i][1] for i in range(len(loop)))<0: loop.reverse()
    triangles=triangulate(loop); n=len(loop)
    vertices=[(x,y,depth*(layer/layers-.5)) for layer in range(layers+1) for x,y in loop]
    faces=[list(reversed(t)) for t in triangles]+[[layers*n+i for i in t] for t in triangles]
    for layer in range(layers):
        for i in range(n):
            j=(i+1)%n; faces.append([layer*n+i,layer*n+j,(layer+1)*n+j,(layer+1)*n+i])
    return vertices,faces

def teacup(low=True):
    """Two overlapping solids; joining objects does not fuse their topology."""
    sides,vertical,samples,handle_sides=(16,1,16,6) if low else (96,16,96,12)
    body=cup_geometry(1.5,2.4,.15,.18,sides,vertical)
    points=[(1.5-.12*.35+.8*math.sin(math.pi*i/(samples-1)),1.2+2.4*.28*math.cos(math.pi*i/(samples-1)),0) for i in range(samples)]
    return [('BloomCupBody',body),('BloomCupHandle',tube(points,.12,handle_sides))]

def validate_mesh(geometry):
    vertices,faces=geometry
    if not vertices or not faces: raise ValueError('Expected a nonempty polygon mesh.')
    if any(len(v)!=3 or not all(math.isfinite(x) for x in v) for v in vertices): raise ValueError('Invalid vertex.')
    for face in faces:
        if len(face)<3 or len(set(face))!=len(face) or any(not isinstance(i,int) or i<0 or i>=len(vertices) for i in face): raise ValueError('Invalid face indices.')

def write_obj(path,meshes):
    """Write geometry only: world coordinates supplied by host, Y-up, one-based indices."""
    import os,tempfile
    from pathlib import Path
    meshes=list(meshes)
    if not meshes: raise ValueError('No meshes to export.')
    for _,geometry in meshes: validate_mesh(geometry)
    destination=Path(path)
    # Replace only after a complete successful write.
    fd,temp=tempfile.mkstemp(prefix='.bloom-',suffix='.obj',dir=str(destination.resolve().parent))
    try:
        with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as stream:
            stream.write('# Sketch Bloom Week 09 | geometry only | Y-up | scene units\n')
            offset=1
            for name,(vertices,faces) in meshes:
                safe=''.join(c if c.isalnum() or c in '_-' else '_' for c in str(name)) or 'BloomMesh'
                stream.write('o '+safe+'\n')
                for v in vertices: stream.write('v '+' '.join(format(x,'.9g') for x in v)+'\n')
                for face in faces: stream.write('f '+' '.join(str(i+offset) for i in face)+'\n')
                offset+=len(vertices)
        os.replace(temp,destination)
    finally:
        if os.path.exists(temp): os.unlink(temp)

ANIMAL_BODIES = {
    'Cat': [(-.9,.85),(-.7,.45),(-.65,-.2),(-.9,-.65),(-.85,-1),(-.5,-.8),(-.15,-.9),(.1,-1),(.25,-.6),(.15,-.3),(.4,.1),(.55,.55),(.85,.5),(1,.1),(1,.65),(.75,.9),(.35,1),(.15,.85),(-.15,.85),(-.25,1),(-.7,1)],
    'Dog': [(-1,-.7),(-.65,-.8),(-.45,-.55),(-.2,-.55),(-.15,-.3),(-.35,-.2),(-.35,.1),(.25,.1),(.6,-.05),(.85,-.45),(1,-.4),(.85,.05),(.6,.3),(.65,.9),(.4,.9),(.3,.45),(-.1,.45),(-.2,.9),(-.45,.9),(-.45,.3),(-.65,.15),(-.65,-.15),(-.85,-.2),(-1,-.4)],
    'Bunny': [(-.8,-1),(-.5,-.95),(-.25,-.3),(-.05,-.35),(.15,-1),(.45,-1),(.4,-.55),(.2,-.1),(.45,.1),(.55,.4),(.85,.65),(.9,.9),(.6,1),(-.4,1),(-.6,.85),(-.9,.8),(-1,.6),(-.8,.4),(-.65,.5),(-.5,.2),(-.65,-.1)],
    'Bear': [(-.9,-.5),(-1,-.8),(-.8,-1),(-.55,-.9),(-.25,-.9),(-.05,-1),(.2,-.9),(.2,-.6),(.5,-.3),(.6,.15),(.85,.45),(.65,.65),(.45,.4),(.45,.85),(.25,1),(0,.85),(-.25,1),(-.55,.85),(-.5,.4),(-.75,.65),(-.95,.4),(-.75,.1),(-.65,-.3)],
    'Fox': [(-1,-1),(-.55,-.75),(-.2,-1),(-.1,-.5),(-.3,-.2),(-.15,.2),(.15,.6),(.5,.5),(.7,.05),(.65,-.45),(1,-.2),(1,.5),(.75,.9),(.2,1),(-.2,.85),(-.4,.95),(-.65,.95),(-.55,.55),(-.75,.1),(-.85,-.4)],
    'Fish': [(-1,-.7),(-.45,-.2),(-.1,-.5),(.15,-.9),(.4,-.5),(.75,-.3),(1,0),(.75,.35),(.4,.5),(.1,.9),(-.05,.55),(-.45,.2),(-1,.7),(-.8,0)],
    'Bird': [(-.9,-.4),(-.65,-.8),(-.25,-.8),(-.05,-.55),(.2,-.4),(.45,-.05),(.85,.2),(1,.05),(.9,.5),(.6,.7),(.15,.7),(.15,1),(0,1),(-.05,.7),(-.25,.65),(-.35,.95),(-.5,.95),(-.4,.5),(-.6,.25),(-.65,-.2),(-1,-.25)],
    'Whale': [(-1,-.6),(-.55,-.2),(-.25,-.6),(.4,-.8),(.85,-.55),(1,0),(.85,.55),(.4,.75),(.1,.65),(-.1,1),(-.3,.9),(-.2,.55),(-.55,.2),(-1,.5),(-.8,0)],
    'Turtle': [(-1,-.2),(-.75,-.4),(-.8,-.7),(-.55,-.65),(-.4,-.8),(.05,-.9),(.4,-.7),(.6,-.35),(.75,-.45),(1,-.3),(1,0),(.8,.15),(.55,.1),(.4,.4),(.55,.65),(.3,.7),(.15,.45),(-.3,.45),(-.45,.75),(-.65,.65),(-.55,.3),(-.8,.1)],
    'Butterfly': [(0,-.8),(.15,-.9),(.2,-.65),(.55,-1),(.95,-.85),(1,-.4),(.65,.1),(.85,.5),(.6,.9),(.25,.7),(.1,.3),(0,1),(-.1,.3),(-.25,.7),(-.6,.9),(-.85,.5),(-.65,.1),(-1,-.4),(-.95,-.85),(-.55,-1),(-.2,-.65),(-.15,-.9)],
}
