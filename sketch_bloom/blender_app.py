"""Blender integration. Run launch_blender.py from Blender's Text Editor."""
import math
import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, StringProperty, PointerProperty
from bpy_extras import view3d_utils
from mathutils import Vector
from . import geometry as geo


def to_blender(p): return (p[0],-p[2],p[1])
def to_shared(p): return (p[0],p[2],-p[1])


def create_mesh(name, geometry):
    geo.validate_mesh(geometry)
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata([to_blender(v) for v in geometry[0]],[],geometry[1]); mesh.update()
    obj=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(obj)
    obj['sketch_bloom']=True
    return obj


def select_only(objects):
    for obj in bpy.context.selected_objects: obj.select_set(False)
    for obj in objects: obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]


def settings(context): return context.scene.sketch_bloom

def report_count(operator,objects):
    operator.report({'INFO'},'Actual mesh faces: {:,}'.format(sum(len(o.data.polygons) for o in objects if o.type=='MESH')))


class BloomSettings(bpy.types.PropertyGroup):
    low: BoolProperty(name='Low Poly mode',default=True,description='New geometry: 16 path samples, 6 tube sides, 16 cup sides; no subdivision')
    output: EnumProperty(name='Output',items=[(x,x,'') for x in ['Tube','Filled','Curve']])
    preset: EnumProperty(name='Shape',items=[(x,x,'') for x in ['Circle','Square','Heart','Star','Leaf','Flower','Cat','Fish','House']])
    samples: IntProperty(name='Path samples',default=96,min=8,max=512)
    sides: IntProperty(name='Tube sides',default=12,min=3,max=64)
    radius: FloatProperty(name='Tube radius',default=.12,min=.001,max=100)
    depth: FloatProperty(name='Fill depth',default=.4,min=.001,max=100)
    size: FloatProperty(name='Preset size',default=2,min=.01,max=100)
    surface: BoolProperty(name='Draw on active mesh',description='Capture the active mesh when drawing starts; Tube/Curve only')
    ratio: FloatProperty(name='Decimate fraction',default=.25,min=.01,max=1,description='Approximate fraction retained on a COPY of an existing mesh; not quad retopology')


class BLOOM_OT_preset(bpy.types.Operator):
    bl_idname='sketch_bloom.preset'; bl_label='Create Filled Preset'; bl_options={'REGISTER','UNDO'}
    def execute(self,context):
        try:
            s=settings(context); outline=geo.preset_outline(s.preset)
            # Simplify outline in Low Poly mode; corners remain where tolerance requires.
            outline=geo.simplify_path(outline,.045 if s.low else .003,True)
            obj=create_mesh('Bloom'+s.preset,geo.filled_outline([((x-.5)*s.size,(y-.5)*s.size) for x,y in outline],s.depth))
            obj.location=context.scene.cursor.location; select_only([obj]); report_count(self,[obj]); return {'FINISHED'}
        except Exception as e: self.report({'ERROR'},str(e)); return {'CANCELLED'}


class BLOOM_OT_cup(bpy.types.Operator):
    bl_idname='sketch_bloom.cup'; bl_label='Create Teacup Parts'; bl_options={'REGISTER','UNDO'}
    def execute(self,context):
        objects=[create_mesh(name,g) for name,g in geo.teacup(settings(context).low)]
        for obj in objects: obj.location=context.scene.cursor.location
        select_only(objects); report_count(self,objects); return {'FINISHED'}


class BLOOM_OT_draw(bpy.types.Operator):
    bl_idname='sketch_bloom.draw'; bl_label='Draw Stroke'; bl_options={'REGISTER','UNDO'}
    @classmethod
    def poll(cls,context): return context.area is not None and context.area.type=='VIEW_3D' and context.mode=='OBJECT'
    def invoke(self,context,event):
        self.points=[]; self.dragging=False; self.region=None
        self.target=context.active_object if settings(context).surface else None
        if settings(context).surface and (not self.target or self.target.type!='MESH' or settings(context).output=='Filled'):
            self.report({'ERROR'},'Surface drawing requires an active mesh and Tube or Curve output.'); return {'CANCELLED'}
        self.plane_point=context.scene.cursor.location.copy()
        self.plane_normal=context.space_data.region_3d.view_rotation @ Vector((0,0,1))
        context.window_manager.modal_handler_add(self)
        context.area.header_text_set('Bloom: drag left mouse in viewport; release to create. Esc cancels.')
        return {'RUNNING_MODAL'}
    def point(self,context,event):
        r=self.region; coord=(event.mouse_x-r.x,event.mouse_y-r.y)
        origin=view3d_utils.region_2d_to_origin_3d(r,context.space_data.region_3d,coord)
        direction=view3d_utils.region_2d_to_vector_3d(r,context.space_data.region_3d,coord)
        if self.target:
            inverse=self.target.matrix_world.inverted()
            hit,p,normal,_=self.target.ray_cast(inverse@origin,(inverse.to_3x3()@direction).normalized(),depsgraph=context.evaluated_depsgraph_get())
            if not hit: return None
            world_normal=(inverse.transposed().to_3x3()@normal).normalized()
            return self.target.matrix_world@p+world_normal*.02
        denominator=direction.dot(self.plane_normal)
        if abs(denominator)<1e-8: return None
        distance=(self.plane_point-origin).dot(self.plane_normal)/denominator
        return origin+direction*distance if distance>0 else None
    def modal(self,context,event):
        if event.type in {'ESC','RIGHTMOUSE'}:
            context.area.header_text_set(None); context.area.tag_redraw(); return {'CANCELLED'}
        if event.type=='LEFTMOUSE' and event.value=='PRESS':
            self.region=next((r for r in context.area.regions if r.type=='WINDOW' and r.x<=event.mouse_x<r.x+r.width and r.y<=event.mouse_y<r.y+r.height),None)
            if self.region is None: return {'RUNNING_MODAL'}
            self.dragging=True
        if self.dragging and event.type in {'LEFTMOUSE','MOUSEMOVE'}:
            p=self.point(context,event)
            if p is None:
                # Prevent bridging across missed surface rays.
                if self.target and self.points:
                    self.dragging=False; context.area.header_text_set(None)
                    self.report({'WARNING'},'Stroke cancelled after leaving the surface.'); return {'CANCELLED'}
            elif not self.points or (p-self.points[-1]).length>.015: self.points.append(p)
        if event.type=='LEFTMOUSE' and event.value=='RELEASE' and self.dragging:
            context.area.header_text_set(None)
            try:
                s=settings(context)
                if len(self.points)<2: raise ValueError('Drag a longer stroke.')
                shared=[to_shared(p) for p in self.points]
                if s.output=='Curve':
                    curve=bpy.data.curves.new('BloomCurve','CURVE'); curve.dimensions='3D'
                    spline=curve.splines.new('POLY'); spline.points.add(len(shared)-1)
                    for dest,p in zip(spline.points,self.points): dest.co=(*p,1)
                    obj=bpy.data.objects.new('BloomCurve',curve); context.collection.objects.link(obj)
                elif s.output=='Tube':
                    obj=create_mesh('BloomStroke',geo.tube(geo.sample(shared,16 if s.low else s.samples,False),s.radius,6 if s.low else s.sides))
                else:
                    # Flatten onto the initial camera plane; shared fill stays host independent.
                    u=context.space_data.region_3d.view_rotation@Vector((1,0,0)); v=self.plane_normal.cross(u)
                    outline=[((p-self.plane_point).dot(u),(p-self.plane_point).dot(v)) for p in self.points]
                    outline=geo.simplify_path(outline,.04 if s.low else .005,True)
                    vertices,faces=geo.filled_outline(outline,s.depth)
                    world=[self.plane_point+u*x+v*y+self.plane_normal*z for x,y,z in vertices]
                    obj=create_mesh('BloomFill',([to_shared(p) for p in world],faces))
                select_only([obj]); report_count(self,[obj]); return {'FINISHED'}
            except Exception as e: self.report({'ERROR'},str(e)); return {'CANCELLED'}
        return {'RUNNING_MODAL'}


class BLOOM_OT_copy(bpy.types.Operator):
    bl_idname='sketch_bloom.copy'; bl_label='Process Selected Mesh Copy'; bl_options={'REGISTER','UNDO'}
    action: EnumProperty(items=[(x,x,'') for x in ['DECIMATE','SUBDIVIDE']])
    def execute(self,context):
        source=context.active_object
        if source is None or source.type!='MESH' or context.mode!='OBJECT':
            self.report({'ERROR'},'Select a mesh in Object Mode.'); return {'CANCELLED'}
        if self.action=='SUBDIVIDE' and len(source.data.polygons)*16>500000:
            self.report({'ERROR'},'Mesh too large for this subdivision action.'); return {'CANCELLED'}
        obj=source.copy(); obj.data=source.data.copy(); context.collection.objects.link(obj); obj.name='Bloom'+self.action
        try:
            select_only([obj]); mod=obj.modifiers.new('BloomCopy', 'DECIMATE' if self.action=='DECIMATE' else 'SUBSURF')
            if self.action=='DECIMATE': mod.ratio=settings(context).ratio
            else: mod.levels=1
            bpy.ops.object.modifier_apply(modifier=mod.name)
            report_count(self,[obj]); return {'FINISHED'}
        except Exception as e:
            bpy.data.objects.remove(obj,do_unlink=True); select_only([source]); self.report({'ERROR'},str(e)); return {'CANCELLED'}


class BLOOM_OT_join(bpy.types.Operator):
    bl_idname='sketch_bloom.join'; bl_label='Join Selected Copies'; bl_options={'REGISTER','UNDO'}
    fuse: BoolProperty(default=False)
    def execute(self,context):
        sources=[o for o in context.selected_objects if o.type=='MESH']
        if len(sources)<2 or context.mode!='OBJECT': self.report({'ERROR'},'Select two or more meshes in Object Mode.'); return {'CANCELLED'}
        copies=[]
        try:
            for source in sources:
                obj=source.copy(); obj.data=source.data.copy(); context.collection.objects.link(obj); copies.append(obj)
            select_only(copies); result=copies[0]
            if self.fuse:
                for other in copies[1:]:
                    mod=result.modifiers.new('BloomUnion','BOOLEAN'); mod.operation='UNION'; mod.solver='EXACT'; mod.object=other
                    bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(other,do_unlink=True)
            else: bpy.ops.object.join()
            result.name='BloomFused' if self.fuse else 'BloomCombined'
            for source in sources: source.hide_set(True)
            select_only([result]); report_count(self,[result]); return {'FINISHED'}
        except Exception as e:
            for obj in copies:
                try: bpy.data.objects.remove(obj,do_unlink=True)
                except ReferenceError: pass
            select_only(sources); self.report({'ERROR'},str(e)); return {'CANCELLED'}


class BLOOM_OT_export(bpy.types.Operator):
    bl_idname='sketch_bloom.export'; bl_label='Export Selected Meshes OBJ'
    filepath: StringProperty(subtype='FILE_PATH',default='sketch_bloom.obj')
    def invoke(self,context,event): context.window_manager.fileselect_add(self); return {'RUNNING_MODAL'}
    def execute(self,context):
        meshes=[]; deps=context.evaluated_depsgraph_get()
        try:
            for obj in context.selected_objects:
                if obj.type!='MESH': continue
                evaluated=obj.evaluated_get(deps); mesh=evaluated.to_mesh()
                try: meshes.append((obj.name,([to_shared(obj.matrix_world@v.co) for v in mesh.vertices],[list(p.vertices) for p in mesh.polygons])))
                finally: evaluated.to_mesh_clear()
            path=self.filepath if self.filepath.lower().endswith('.obj') else self.filepath+'.obj'
            geo.write_obj(path,meshes); self.report({'INFO'},'Exported {} evaluated mesh(es), Y-up'.format(len(meshes))); return {'FINISHED'}
        except Exception as e: self.report({'ERROR'},str(e)); return {'CANCELLED'}


class BLOOM_PT_panel(bpy.types.Panel):
    bl_label='Sketch Bloom • Week 09'; bl_idname='BLOOM_PT_panel'; bl_space_type='VIEW_3D'; bl_region_type='UI'; bl_category='Sketch Bloom'
    def draw(self,context):
        l=self.layout; s=settings(context)
        l.prop(s,'low')
        if s.low: l.label(text='16 samples / 6 sides / no subdivision')
        else: l.prop(s,'samples'); l.prop(s,'sides')
        l.prop(s,'radius'); l.prop(s,'depth'); l.prop(s,'output'); l.prop(s,'surface'); l.operator('sketch_bloom.draw')
        l.label(text='No stroke preview; release to create.')
        l.prop(s,'preset'); l.prop(s,'size'); l.operator('sketch_bloom.preset'); l.operator('sketch_bloom.cup')
        l.label(text='Edit points: Tab into Edit Mode')
        l.operator('sketch_bloom.join',text='Combine copies').fuse=False
        l.operator('sketch_bloom.join',text='Boolean union copies').fuse=True
        l.prop(s,'ratio'); l.operator('sketch_bloom.copy',text='Decimate copy (not retopology)').action='DECIMATE'
        l.operator('sketch_bloom.copy',text='Subdivide copy (+ density)').action='SUBDIVIDE'
        obj=context.active_object
        if obj and obj.type=='MESH':
            l.label(text='Base faces: {:,}'.format(len(obj.data.polygons)))
            evaluated=obj.evaluated_get(context.evaluated_depsgraph_get()); mesh=evaluated.to_mesh()
            try: l.label(text='Evaluated faces: {:,}'.format(len(mesh.polygons)))
            finally: evaluated.to_mesh_clear()
        else: l.label(text='Select mesh for actual face counts')
        l.operator('sketch_bloom.export')


CLASSES=(BloomSettings,BLOOM_OT_preset,BLOOM_OT_cup,BLOOM_OT_draw,BLOOM_OT_copy,BLOOM_OT_join,BLOOM_OT_export,BLOOM_PT_panel)
def register():
    if hasattr(bpy.types.Scene,'sketch_bloom'): unregister()
    for cls in CLASSES: bpy.utils.register_class(cls)
    bpy.types.Scene.sketch_bloom=PointerProperty(type=BloomSettings)
def unregister():
    if hasattr(bpy.types.Scene,'sketch_bloom'): del bpy.types.Scene.sketch_bloom
    for cls in reversed(CLASSES):
        old=getattr(bpy.types,cls.__name__,None)
        if old: bpy.utils.unregister_class(old)
