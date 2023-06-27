import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from Mesh3D_normals import *
from Object3D import *
from OpenGL.arrays import vbo
from numpy import array
from OpenGL.GL import shaders

from RenderProgram import *
import time
import math


def load_obj(filename) -> Object3D:
    with open(filename) as f:
        return Object3D(Mesh3D.load_obj(f))


def load_textured_obj(filename, texture_filename) -> Object3D:
    with open(filename) as f:
        return Object3D(
            Mesh3D.load_textured_obj(f, pygame.image.load(texture_filename))
        )


def load_shader_source(filename):
    with open(filename) as f:
        return f.read()


if __name__ == "__main__":
    pygame.init()
    
    screen_width = 800
    screen_height = 800
    # For Mac people.
    pygame.display.gl_set_attribute(GL_CONTEXT_MAJOR_VERSION, 4)
    pygame.display.gl_set_attribute(GL_CONTEXT_MINOR_VERSION, 1)
    pygame.display.gl_set_attribute(GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, GL_CONTEXT_PROFILE_CORE)
    pygame.display.gl_set_attribute(GL_CONTEXT_PROFILE_COMPATIBILITY, GL_CONTEXT_PROFILE_CORE)
    
    screen = pygame.display.set_mode(
        (screen_width, screen_height),
        DOUBLEBUF | OPENGL,
    )
    pygame.display.set_caption("specular lighting demo")

    bunny = load_textured_obj("models/bunny_textured.obj", "models/bunny_textured.jpg")
    bunny.center_point(glm.vec3(-0.03, 0.07, 0))
    bunny.move(glm.vec3(0.1, -0.5, -3))
    bunny.grow(glm.vec3(5, 5, 5))

    light = load_textured_obj("models/cube.obj", "models/wall.jpg")
    light.center_point(glm.vec3(0, 0, -10))
    light.move(glm.vec3(0, 0, -1))
    light.grow(glm.vec3(0.01, 0.01, 0.01))

    # Load the vertex and fragment shaders for this program.
    vertex_shader = shaders.compileShader(
        load_shader_source("shaders/normal_perspective.vert"), GL_VERTEX_SHADER
    )
    fragment_shader = shaders.compileShader(
        load_shader_source("shaders/specular_light.frag"), GL_FRAGMENT_SHADER
    )
    shader_lighting = shaders.compileProgram(vertex_shader, fragment_shader)

    # Compile a second shader for drawing the "light" cube, which should
    # not light *itself*.
    vertex_shader = shaders.compileShader(
        load_shader_source("shaders/normal_perspective.vert"), GL_VERTEX_SHADER
    )
    fragment_shader = shaders.compileShader(
        load_shader_source("shaders/texture_mapped.frag"), GL_FRAGMENT_SHADER
    )
    shader_no_lighting = shaders.compileProgram(vertex_shader, fragment_shader)
    
    renderer = RenderProgram()
    # Define the scene.
    camera = glm.lookAt(glm.vec3(0, 0, 3), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
    perspective = glm.perspective(
        math.radians(30), screen_width / screen_height, 0.1, 100
    )
    

    # Initialize lighting parameters.
    ambient_color = glm.vec3(1, 1, 1)
    ambient_intensity = 0.1
    point_position = glm.vec3(0, 0, 0)
    renderer.set_uniform("ambientColor", ambient_color * ambient_intensity, glm.vec3)
    renderer.set_uniform("pointPosition", point_position, glm.vec3)
    renderer.set_uniform("pointColor", glm.vec3(1, 1, 1), glm.vec3)

    # Loop
    done = False
    frames = 0
    start = time.perf_counter()

    glEnable(GL_DEPTH_TEST)
    keys_down = set()
    spin = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                keys_down.add(event.dict["key"])
            elif event.type == pygame.KEYUP:
                keys_down.remove(event.dict["key"])

        if pygame.K_UP in keys_down:
            bunny.rotate(glm.vec3(-0.001, 0, 0))
        elif pygame.K_DOWN in keys_down:
            bunny.rotate(glm.vec3(0.001, 0, 0))
        if pygame.K_RIGHT in keys_down:
            bunny.rotate(glm.vec3(0, 0.001, 0))
        elif pygame.K_LEFT in keys_down:
            bunny.rotate(glm.vec3(0, -0.001, 0))
        elif pygame.K_a in keys_down:
           light.move(glm.vec3(-0.001, 0, 0))
           renderer.set_uniform("pointPosition", light.position, glm.vec3)
        elif pygame.K_d in keys_down:
           light.move(glm.vec3(0.001, 0, 0))
           renderer.set_uniform("pointPosition", light.position, glm.vec3)
        elif pygame.K_SPACE in keys_down:
            spin = not spin

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Draw the bunny with lighting.
        renderer.use_program(shader_lighting)
        renderer.set_uniform("pointPosition", light.get_position(), glm.vec3)
        renderer.render(perspective, camera, [bunny])
        
        # Draw the light source without lighting itself.
        renderer.use_program(shader_no_lighting)
        renderer.render(perspective, camera, [light])

        pygame.display.flip()
        end = time.perf_counter()
        frames += 1
        #print(f"{frames/(end - start)} FPS")
    pygame.quit()
