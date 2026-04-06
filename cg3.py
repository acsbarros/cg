import glfw
from OpenGL.GL import *
import numpy as np

import numpy as np
import math

def multiplica_matriz(a,b):
    m_a = a.reshape(4,4)
    m_b = b.reshape(4,4)
    m_c = np.dot(m_a,m_b)
    c = m_c.reshape(1,16)
    return c

glfw.init()
glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
window = glfw.create_window(600, 600, "Linhas", None, None)
glfw.make_context_current(window)
VERTEX_CODE = """
        attribute vec2 position;
        uniform mat4 mat_transformation;
        void main(){
            gl_Position = mat_transformation * vec4(position,0.0,1.0);
        }
        """
FRAGMENT_CODE = """
        uniform vec4 color;
        void main(){
            gl_FragColor = color;
        }
        """
program = glCreateProgram()
vertex = glCreateShader(GL_VERTEX_SHADER)
fragment = glCreateShader(GL_FRAGMENT_SHADER)
glShaderSource(vertex, VERTEX_CODE)
glShaderSource(fragment, FRAGMENT_CODE)
glCompileShader(vertex)
if not glGetShaderiv(vertex, GL_COMPILE_STATUS):
    error = glGetShaderInfoLog(vertex).decode()
    print(error)
    raise RuntimeError("Erro de compilacao do Vertex Shader")
glCompileShader(fragment)
if not glGetShaderiv(fragment, GL_COMPILE_STATUS):
    error = glGetShaderInfoLog(fragment).decode()
    print(error)
    raise RuntimeError("Erro de compilacao do Fragment Shader")
glAttachShader(program, vertex)
glAttachShader(program, fragment)
glLinkProgram(program)
if not glGetProgramiv(program, GL_LINK_STATUS):
    print(glGetProgramInfoLog(program))
    raise RuntimeError('Linking error')
glUseProgram(program)
vertices = np.zeros(3, [("position", np.float32, 2)])
vertices['position'] = [(-0.5,0),(0,0.5),(0.5,0)]
buffer = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, buffer)
buffer = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, buffer)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)
glBindBuffer(GL_ARRAY_BUFFER, buffer)
stride = vertices.strides[0]
offset = ctypes.c_void_p(0)
loc = glGetAttribLocation(program, "position")
loc_color = glGetUniformLocation(program, "color")
R = 1.0
G = 0.0
B = 0.0
# exemplo para matriz de translacao
t_x = 0
t_y = 0
def key_event(window,key,scancode,action,mods):
    global t_x, t_y, s_x, s_y, d, op
    
    print('[key event] key=',key)
    if op == 1:
        if key == 265: t_y += 0.01 #cima
        if key == 264: t_y -= 0.01 #baixo
        if key == 263: t_x -= 0.01 #esquerda
        if key == 262: t_x += 0.01 #direita
    if op == 2:
        if key == 265: s_y += 0.01 #cima
        if key == 264: s_y -= 0.01 #baixo
        if key == 263: s_x -= 0.01 #esquerda
        if key == 262: s_x += 0.01 #direita
    if op ==3:
        if key == 265: d += 0.1 #cima
        if key == 264: d -= 0.1 #baixo     
    if key == 65:
        print('translacao')
        op = 1
    if key == 66:
        print('escala')
        op = 2
    if key == 67:
        print('rotacao x')
        op = 3

glfw.set_key_callback(window,key_event)

glEnableVertexAttribArray(loc)
glVertexAttribPointer(loc, 2, GL_FLOAT, False, stride, offset)
glfw.show_window(window)
t_y = 0
t_x = 0

s_x = 1
s_y = 1

op = 0
d = 0.0
while not glfw.window_should_close(window):
    glfw.poll_events()
    glClear(GL_COLOR_BUFFER_BIT)
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glUniform4f(loc_color, R, G, B, 1.0)
    
    
    cos_d = math.cos(d)
    sin_d = math.sin(d)

    mat_rotation_z = np.array([     cos_d, -sin_d, 0.0, 0.0,
                                    sin_d,  cos_d, 0.0, 0.0,
                                    0.0,      0.0, 1.0, 0.0,
                                    0.0,      0.0, 0.0, 1.0], np.float32)

    mat_rotation_x = np.array([     1.0,   0.0,    0.0, 0.0,
                                    0.0, cos_d, -sin_d, 0.0,
                                    0.0, sin_d,  cos_d, 0.0,
                                    0.0,   0.0,    0.0, 1.0], np.float32)

    mat_rotation_y = np.array([     cos_d,  0.0, sin_d, 0.0,
                                    0.0,    1.0,   0.0, 0.0,
                                    -sin_d, 0.0, cos_d, 0.0,
                                    0.0,    0.0,   0.0, 1.0], np.float32)



    mat_translation = np.array([    1.0, 0.0, 0.0, t_x,
                                    0.0, 1.0, 0.0, t_y,
                                    0.0, 0.0, 1.0, 0.0,
                                    0.0, 0.0, 0.0, 1.0], np.float32)

    mat_scale       = np.array([    s_x, 0.0, 0.0, 0.0,
                                    0.0, s_y, 0.0, 0.0,
                                    0.0, 0.0, 1.0, 0.0,
                                    0.0, 0.0, 0.0, 1.0], np.float32)

    #mat_transform = multiplica_matriz(mat_translation,mat_scale)
    loc = glGetUniformLocation(program, "mat_transformation")
    print('op = {}'.format(op))
    if op == 1:
        glUniformMatrix4fv(loc, 1, GL_TRUE, mat_translation)
    if op == 2:
        glUniformMatrix4fv(loc, 1, GL_TRUE, mat_scale)
    if op == 3:
        glUniformMatrix4fv(loc, 1, GL_TRUE, mat_rotation_z)
    glDrawArrays(GL_TRIANGLES, 0, len(vertices))
    glfw.swap_buffers(window)
glfw.terminate()