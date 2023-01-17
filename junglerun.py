import pygame

# import the scene class
from cubeMap import FlattenCubeMap
from scene import Scene

from lightSource import LightSource

from blender import load_obj_file

from BaseModel import DrawModelFromMesh

from shaders import *

from ShadowMapping import *

from sphereModel import Sphere

from skyBox import *

from environmentMapping import *

class ExeterScene(Scene):
    def __init__(self):
        Scene.__init__(self)
        #Creating the source of light
        self.light = LightSource(self, position=[3., 8., -3.])

        self.shaders='phong'

        # for shadow map rendering
        self.shadows = ShadowMap(light=self.light)
        self.show_shadow_map = ShowTexture(self, self.shadows)

        self.environment = EnvironmentMappingTexture(width=400, height=400)
        # loading base scene
        meshes = load_obj_file('models/scene.obj')
        
        self.scene = [DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([0,-1,0]),scaleMatrix([0.5,0.5,0.5])), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows), name='scene') for mesh in meshes]

        # loading individual objects into the scene
        gorilla = load_obj_file('models/gorilla.obj')
        self.gorilla = DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([0,-3,0]), scaleMatrix([0.5,0.5,0.5])), mesh=gorilla[0], shader=EnvironmentShader(map=self.environment))

        palm = load_obj_file('models/palm.obj')
        self.add_models_list([DrawModelFromMesh(scene=self, M=poseMatrix([-10, 1.3, 0],0,1), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows)) for mesh in palm])

        self.add_models_list([DrawModelFromMesh(scene=self, M=poseMatrix([-12, 1.3, 7],0,1), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows)) for mesh in palm])

        self.add_models_list([DrawModelFromMesh(scene=self, M=poseMatrix([-13, 1.4, 5],0,1), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows)) for mesh in palm])

        self.add_models_list([DrawModelFromMesh(scene=self, M=poseMatrix([-10, 1.4, -2],0,0.9), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows)) for mesh in palm])

        self.add_models_list([DrawModelFromMesh(scene=self, M=poseMatrix([-5, 3, -4],0,1.3), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows)) for mesh in palm])

        self.add_models_list([DrawModelFromMesh(scene=self, M=poseMatrix([-3, 2.5, 3],0,1.1), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows)) for mesh in palm])

        self.add_models_list([DrawModelFromMesh(scene=self, M=poseMatrix([-7, 3.3, 3],0.1,1.2), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows)) for mesh in palm])
        
        rock = load_obj_file('models/rock.obj')
        self.add_models_list([DrawModelFromMesh(scene=self, M=poseMatrix([0, 1.2, -10],0,1), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows)) for mesh in rock])

        self.add_models_list([DrawModelFromMesh(scene=self, M=poseMatrix([3, 1.2, 0],0.2,1), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows)) for mesh in rock])

        self.add_models_list([DrawModelFromMesh(scene=self, M=poseMatrix([0, 1.2, -4],0,1), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows)) for mesh in rock])
        # draw a skybox for the horizon of the jungle
        self.skybox = SkyBox(scene=self)

        self.show_light = DrawModelFromMesh(scene=self, M=poseMatrix(position=self.light.position, scale=0.2), mesh=Sphere(material=Material(Ka=[10,10,10])), shader=FlatShader())

        

        self.sphere = DrawModelFromMesh(scene=self, M=poseMatrix(), mesh=Sphere(), shader=EnvironmentShader(map=self.environment))


        self.flattened_cube = FlattenCubeMap(scene=self, cube=self.environment)
        self.show_texture = ShowTexture(self, Texture('lena.bmp'))


    def draw_shadow_map(self):
        # clearing the scene and the depth buffer in order to handle occlusions
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        #drawing shadows for models
        
        for model in self.models:
            model.draw()

    #drawing reflections for models
    def draw_reflections(self):
        self.skybox.draw()

        for model in self.models:
            model.draw()

        

        
        
        

    def draw(self, framebuffer=False):
        '''
        Draw all models in the scene
        :return: None
        '''

        # clearing the scene and the depth buffer in order to handle occlusions
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # the camera is not updated to allow for a arbitrary viewpoint when using a framebuffer.
        if not framebuffer:
            self.camera.update()

        # first, the skybox is drawn
        self.skybox.draw()

        # the shadows are rendered
        self.shadows.render(self)

        # when rendering the framebuffer the reflective object is ignored
        if not framebuffer:
            self.environment.update(self)

            # if enabled, show flattened cube
            self.flattened_cube.draw()

            # if enabled, show texture
            self.show_texture.draw()

            self.show_shadow_map.draw()

        # then we loop over all models in the list and draw them
        for model in self.scene:
            model.draw()

        for model in self.models:
            model.draw()

        

        self.gorilla.draw()
        
        
        self.show_light.draw()

        # after the objects are drawn, the scene is displayed.
        # double buffering is used to avoid artefacts:
        # two different buffers are used: one to draw and one to display.
        # the two buffers are flipped once the drawing is done.
        if not framebuffer:
            pygame.display.flip()

    def keyboard(self, event):
        '''
        Process additional keyboard events for this demo.
        '''
        Scene.keyboard(self, event)

        if event.key == pygame.K_w:
            self.gorilla.M = np.matmul(self.gorilla.M, translationMatrix([0,1,0]))
        if event.key == pygame.K_a:
            self.gorilla.M = np.matmul(self.gorilla.M, translationMatrix([0,0,1]))
        if event.key == pygame.K_s:
            self.gorilla.M = np.matmul(self.gorilla.M, translationMatrix([0,-1,0]))
        if event.key == pygame.K_d:
            self.gorilla.M = np.matmul(self.gorilla.M, translationMatrix([0,0,-1]))

        if event.key == pygame.K_v:
            self.gorilla.M = np.matmul(self.gorilla.M, rotationMatrixZ(-0.1))
        if event.key == pygame.K_b:
            self.gorilla.M = np.matmul(self.gorilla.M, rotationMatrixZ(0.1))


        # display flattened cube map 
        if event.key == pygame.K_c:
            if self.flattened_cube.visible:
                self.flattened_cube.visible = False
            else:
                print('--> showing cube map')
                self.flattened_cube.visible = True
        # display shadow map
        if event.key == pygame.K_p:
            if self.show_shadow_map.visible:
                self.show_shadow_map.visible = False
            else:
                print('--> showing shadow map')
                self.show_shadow_map.visible = True



if __name__ == '__main__':
    # initialises the scene object
    # scene = Scene(shaders='gouraud')
    scene = ExeterScene()

    # starts drawing the scene
    scene.run()
