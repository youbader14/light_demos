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

x,y=[1.5,91.0]
background_color = [0.0, 0.0, 0.0]
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
    pygame.display.gl_set_attribute(
        GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True
    )
    pygame.display.gl_set_attribute(
        pygame.GL_CONTEXT_PROFILE_MASK, GL_CONTEXT_PROFILE_CORE
    )
    pygame.display.gl_set_attribute(
        GL_CONTEXT_PROFILE_COMPATIBILITY, GL_CONTEXT_PROFILE_CORE
    )

    screen = pygame.display.set_mode(
        (screen_width, screen_height),
        DOUBLEBUF | OPENGL,
    )
    pygame.display.set_caption("specular lighting demo")
    #bunny
    bunny = load_textured_obj("models/bunny_textured.obj", "models/dice.png")
    bunny.center_point(glm.vec3(-0.03, 0.07, 0))
    bunny.move(glm.vec3(0.1, -0.5, -3))
    bunny.grow(glm.vec3(5, 5, 5))
    #positional light
    light = load_textured_obj("models/cube.obj", "models/wall.jpg")
    light.center_point(glm.vec3(0, 0, -10))
    light.move(glm.vec3(0, 0, -1))
    light.grow(glm.vec3(0.01, 0.01, 0.01))
    ##added bird
    bird = load_textured_obj("models/bird.obj", "models/wall.jpg")
    bird.center_point(glm.vec3(0, 0, 0))
    bird.move(glm.vec3(-3, 4.5, -10))
    bird.grow(glm.vec3(0.08, 0.08, 0.08))  # Adjust the scale factors to make the bird smaller
    bird.rotate(glm.vec3(x, y, 0.0))  # Rotate the bird forward around the x-axis and face right around the y-axis
    tree1 = load_textured_obj("models/trees9.obj", "models/icon.png")
    tree1.center_point(glm.vec3(0, 0, 0))
    tree1.move(glm.vec3(-5, 0, -10))
    tree1.grow(glm.vec3(0.1, 0.1, 0.1))  # Decrease the size by 10 times

    tree2 = load_textured_obj("models/trees9.obj", "models/icon.png")
    tree2.center_point(glm.vec3(0, 0, 0))
    tree2.move(glm.vec3(5, 0, -10))
    tree2.grow(glm.vec3(0.1, 0.1, 0.1))  # Decrease the size by 10 times

    # Load the vertex and fragment shaders for this program.
    vertex_shader = shaders.compileShader(
        load_shader_source("shaders/normal_perspective.vert"), GL_VERTEX_SHADER
    )
    fragment_shader = shaders.compileShader(
        load_shader_source("shaders/specular_light.frag"), GL_FRAGMENT_SHADER
    )
    shader_lighting = shaders.compileProgram(
        vertex_shader, fragment_shader
    )

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
    camera = glm.lookAt(
        glm.vec3(0, 0, 10), glm.vec3(0, 0, -10), glm.vec3(0, 1, 0)
    )
    perspective = glm.perspective(
        math.radians(30), screen_width / screen_height, 0.1, 100
    )

    # Initialize lighting parameters.
    ambient_color = glm.vec3(1, 1, 1)
    ambient_intensity = 0.1
    point_position = glm.vec3(0, 0, 0)
    renderer.set_uniform(
        "ambientColor", ambient_color * ambient_intensity, glm.vec3
    )
    renderer.set_uniform("pointPosition", point_position, glm.vec3)
    renderer.set_uniform("pointColor", glm.vec3(1, 1, 1), glm.vec3)

    # Loop
    done = False
    frames = 0
    start = time.perf_counter()

    keys_down = set()
    spin = False
    bird_speed = 0.001
    bird_direction = 1

   

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                keys_down.add(event.dict["key"])
            elif event.type == pygame.KEYUP:
                keys_down.remove(event.dict["key"])

        if pygame.K_UP in keys_down:
            bird.move(glm.vec3(0, 0.1, 0))
            bird.rotate(glm.vec3(-0.001, 0, 0))
        elif pygame.K_DOWN in keys_down:
            bird.move(glm.vec3(0, -0.1, 0))
            bird.rotate(glm.vec3(0.001, 0, 0))
        if pygame.K_RIGHT in keys_down:
            bird.move(glm.vec3(0.1, 0, 0))
            bird.rotate(glm.vec3(0, 0.001, 0))
        elif pygame.K_LEFT in keys_down:
            bird.move(glm.vec3(-0.1, 0, 0))
            bird.rotate(glm.vec3(0, -0.001, 0))
        elif pygame.K_a in keys_down:
            bird.move(glm.vec3(-0.001, 0, 0))
            bird.rotate(glm.vec3(0, 0, -0.001))
        elif pygame.K_d in keys_down:
            bird.move(glm.vec3(0.001, 0, 0))
            bird.rotate(glm.vec3(0, 0, 0.001))
        elif pygame.K_w in keys_down:
            bird.rotate(glm.vec3(0.001, 0, 0))  # Rotate the bird slightly along the x-axis (look up)
        if pygame.K_i in keys_down:
            bunny.rotate(glm.vec3(-0.001, 0, 0))
        elif pygame.K_k in keys_down:
            bunny.rotate(glm.vec3(0.001, 0, 0))
        if pygame.K_l in keys_down:
            bunny.rotate(glm.vec3(0, 0.001, 0))
        elif pygame.K_j in keys_down:
            bunny.rotate(glm.vec3(0, -0.001, 0))
        elif pygame.K_z in keys_down:
            light.move(glm.vec3(-0.1, 0, 0))
            renderer.set_uniform("pointPosition", light.position, glm.vec3)
        elif pygame.K_x in keys_down:
            light.move(glm.vec3(0.1, 0, 0))
            renderer.set_uniform("pointPosition", light.position, glm.vec3)
        elif pygame.K_SPACE in keys_down:
            spin = not spin
        bird.move(glm.vec3(bird_speed * bird_direction, 0, 0))

        if bird.position.x > 3:
            x=1.5
            y=91.0
            bird_direction = -1
            bird.rotate(glm.vec3(x, y, 0.0))  # Rotate the bird forward around the x-axis and face right around the y-axis

        elif bird.position.x < -3:
            x=-1.5
            y=0.0
            bird_direction = 1
            bird.rotate(glm.vec3(-1.5, 0.0, 0.0))  # Rotate the bird forward around the x-axis and face right around the y-axis

        if light.position.x < 0:
            # Calculate the light intensity based on the position
            light_intensity = max(0, 1.0 + light.position.x)

            # Update the background color towards dark blue
            background_color[0] = light_intensity * 0.529  # Red component
            background_color[1] = light_intensity * 0.808  # Green component
            background_color[2] = light_intensity * 0.922  # Blue component

        # Set the background color
        glClearColor(*background_color, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Clear color and depth buffers

        # Draw the bunny with lighting.
        renderer.use_program(shader_lighting)
        renderer.set_uniform("pointPosition", point_position, glm.vec3)
        renderer.render(perspective, camera, [bunny])
        # Draw the bird with lighting.
        renderer.use_program(shader_lighting)
        renderer.set_uniform("pointPosition", point_position, glm.vec3)
        renderer.render(perspective, camera, [bird])

        # Draw the trees without lighting.
        renderer.use_program(shader_lighting)
        renderer.render(perspective, camera, [tree1, tree2])
        # Draw the light source without lighting itself.
        renderer.use_program(shader_no_lighting)
        renderer.render(perspective, camera, [light])

        pygame.display.flip()
        end = time.perf_counter()
        frames += 1
        # print(f"{frames/(end - start)} FPS")
    pygame.quit()
