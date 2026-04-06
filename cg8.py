import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np

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
    window = glfw.create_window(800, 600, "Draw Triangule", None, None)
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

def update_vbo(vbo, data):
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

def update_ibo(ibo, data):
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

def main():
    window = initialize_glfw()
    if not window:
        print("Failed to initialize GLFW")
        return

    shader_program = create_shader_program()
    glUseProgram(shader_program)

    vertices = [
        0.0,  0.5, 0.0,  # Ponto superior
        -0.5, -0.5, 0.0,  # Ponto inferior esquerdo
        0.5, -0.5, 0.0   # Ponto inferior direito
    ]
    indices = [
        0, 1, 2  # Triângulo único
    ]
    
    vertices = np.array(vertices, dtype=np.float32)
    indices = np.array(indices, dtype=np.uint32)

    position = glGetAttribLocation(shader_program, 'position')
    loc_color = glGetUniformLocation(shader_program, "color")
    glEnableVertexAttribArray(position)

    vbo = glGenBuffers(1)
    ibo = glGenBuffers(1)

    glClearColor(1, 1, 1, 1.0)
    glUniform4f(loc_color, 1, 0, 0, 1.0)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT)
        update_vbo(vbo, np.array(vertices).flatten().astype(np.float32))
        update_ibo(ibo, indices)
        
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glVertexAttribPointer(position, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo)
        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()
    
if __name__ == "__main__":
    main()
