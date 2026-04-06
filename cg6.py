import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
from scipy.spatial import Delaunay
import time

# Vertex Shader
vertex_shader_source = """
        attribute vec2 position;
        void main(){
            gl_Position = vec4(position,0.0,1.0);
        }
        """

# Fragment Shader
fragment_shader_source = """
        uniform vec4 color;
        void main(){
            gl_FragColor = color;
        }
        """

def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        raise RuntimeError(glGetShaderInfoLog(shader))
    return shader

def create_shader_program():
    vertex_shader = compile_shader(vertex_shader_source, GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment_shader_source, GL_FRAGMENT_SHADER)
    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)
    if not glGetProgramiv(program, GL_LINK_STATUS):
        raise RuntimeError(glGetProgramInfoLog(program))
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)
    return program

def initialize_glfw():
    if not glfw.init():
        return None
    window = glfw.create_window(800, 600, "Delaunay Triangulation", None, None)
    if not window:
        glfw.terminate()
        return None
    glfw.make_context_current(window)
    return window

def create_vbo(data):
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
    return vbo

def create_ibo(data):
    ibo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
    return ibo

def main():
    window = initialize_glfw()
    if not window:
        print("Failed to initialize GLFW")
        return

    shader_program = create_shader_program()
    glUseProgram(shader_program)

    points = np.random.rand(40, 2).astype(np.float32)
    delaunay = Delaunay(points)

    # Flatten points for VBO
    flat_points = points.flatten()

    indices = []
    for simplex in delaunay.simplices:
        indices.extend([simplex[0], simplex[1], simplex[1], simplex[2], simplex[2], simplex[0]])

    indices = np.array(indices, dtype=np.uint32)

    # Create VBO for vertices
    vbo = create_vbo(flat_points)
    # Create IBO for indices
    ibo = create_ibo(indices)

    position = glGetAttribLocation(shader_program, 'position')
    loc_color = glGetUniformLocation(shader_program, "color")
    glEnableVertexAttribArray(position)
    glVertexAttribPointer(position, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

    glClearColor(1, 1, 1, 1.0)
    glUniform4f(loc_color, 1, 0, 0, 1.0)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT)

        # Bind VBO and IBO
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo)
        glVertexAttribPointer(position, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        
        glDrawElements(GL_LINES, len(indices), GL_UNSIGNED_INT, ctypes.c_void_p(0))

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()