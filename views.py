import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import math
from PIL import Image,ImageDraw,ImageFont

# --- SHADERS ---
# Vertex Shader: Recebe a posição e aplica um deslocamento (offset) controlado pelo teclado
# --- SHADERS ---
VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec2 aPos;
uniform vec2 offset;
uniform float scale;
uniform float aspect_ratio;

void main() {
    // Escala o objeto
    vec2 pos = aPos * scale;
    // Corrige a distorção no eixo X baseada na proporção da janela
    pos.x = pos.x / aspect_ratio;
    
    gl_Position = vec4(pos + offset, 0.0, 1.0);
}
"""

# Fragment Shader: Define a cor do objeto
FRAGMENT_SHADER = """
#version 330 core
out vec4 FragColor;
uniform vec3 color;

void main() {
    FragColor = vec4(color, 1.0);
}
"""

# --- ESTADO GLOBAL DA APLICAÇÃO ---
active_viewport = 0  # 0: Triângulo, 1: Texto(CD), 2: Retângulo, 3: Círculo
# Armazena offset X, offset Y, e escala para os 4 objetos
obj_states = [
    {"offset": [0.0, 0.0], "scale": 1.0},
    {"offset": [0.0, 0.0], "scale": 1.0},
    {"offset": [0.0, 0.0], "scale": 1.0},
    {"offset": [0.0, 0.0], "scale": 1.0}
]
# --- CALLBACK DE MOUSE ---
def mouse_button_callback(window, button, action, mods):
    global active_viewport
    
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        # Pega a posição do mouse e o tamanho atual da janela
        xpos, ypos = glfw.get_cursor_pos(window)
        width, height = glfw.get_window_size(window)
        
        meio_x = width / 2.0
        meio_y = height / 2.0
        
        # Verifica em qual quadrante o clique ocorreu
        if xpos < meio_x and ypos < meio_y:
            active_viewport = 0  # Top-Left (Triângulo)
        elif xpos >= meio_x and ypos < meio_y:
            active_viewport = 1  # Top-Right (Texto/Linhas)
        elif xpos < meio_x and ypos >= meio_y:
            active_viewport = 2  # Bottom-Left (Retângulo)
        elif xpos >= meio_x and ypos >= meio_y:
            active_viewport = 3  # Bottom-Right (Círculo)

# --- CALLBACK DE TECLADO ---
def key_callback(window, key, scancode, action, mods):
    global active_viewport
    
    if action == glfw.PRESS or action == glfw.REPEAT:
        # Selecionar Viewport
        if key == glfw.KEY_1: active_viewport = 0 # Top-Left
        elif key == glfw.KEY_2: active_viewport = 1 # Top-Right
        elif key == glfw.KEY_3: active_viewport = 2 # Bottom-Left
        elif key == glfw.KEY_4: active_viewport = 3 # Bottom-Right
        
        # Interagir com o objeto ativo (Mover)
        step = 0.05
        if key == glfw.KEY_UP:    obj_states[active_viewport]["offset"][1] += step
        elif key == glfw.KEY_DOWN:  obj_states[active_viewport]["offset"][1] -= step
        elif key == glfw.KEY_LEFT:  obj_states[active_viewport]["offset"][0] -= step
        elif key == glfw.KEY_RIGHT: obj_states[active_viewport]["offset"][0] += step
        
        # Interagir com o objeto ativo (Escalar)
        elif key == glfw.KEY_W: obj_states[active_viewport]["scale"] += step
        elif key == glfw.KEY_S: obj_states[active_viewport]["scale"] -= step

# --- FUNÇÃO AUXILIAR PARA CRIAR VAOs ---
def create_vao(vertices):
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    
    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * 4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    return vao

def main():
    if not glfw.init():
        return
    
    # Configurar para Core Profile (OpenGL Moderno)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    
    window = glfw.create_window(176, 144, "4 Viewports - OpenGL Moderno", None, None)
    if not window:
        glfw.terminate()
        return
        
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback) # ADICIONE ESTA LINHA AQUI
    
    shader = compileProgram(
        compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
        compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
    )
    glUseProgram(shader)
    
    offset_loc = glGetUniformLocation(shader, "offset")
    scale_loc = glGetUniformLocation(shader, "scale")
    color_loc = glGetUniformLocation(shader, "color")
    aspect_loc = glGetUniformLocation(shader, "aspect_ratio") 

    # --- DEFINIÇÃO DOS VÉRTICES DAS GEOMETRIAS ---
    
    # 1. Triângulo
    tri_verts = np.array([-0.5, -0.5,  0.5, -0.5,  0.0, 0.5], dtype=np.float32)
    vao_tri = create_vao(tri_verts)
    
    # 2. "Texto" (Letras C e D feitas com linhas para representar a disciplina)
    cd_verts = np.array([
        # Letra C
        0.3, 0.5,   -0.3, 0.5,
        -0.3, 0.5,  -0.3, -0.5,
        -0.3, -0.5,  0.3, -0.5,
        # Letra D
        0.5, 0.5,    0.8, 0.5,
        0.8, 0.5,    0.9, 0.2,
        0.9, 0.2,    0.9, -0.2,
        0.9, -0.2,   0.8, -0.5,
        0.8, -0.5,   0.5, -0.5,
        0.5, -0.5,   0.5, 0.5
    ], dtype=np.float32)
    vao_cd = create_vao(cd_verts)
    
    # 3. Retângulo
    rect_verts = np.array([
        -0.6, 0.4,  -0.6, -0.4,  0.6, -0.4,
        -0.6, 0.4,   0.6, -0.4,  0.6, 0.4
    ], dtype=np.float32)
    vao_rect = create_vao(rect_verts)
    
    # 4. Círculo (Aproximado com polígono)
    circle_verts = []
    num_segments = 56
    for i in range(num_segments + 1):
        theta = 2.0 * math.pi * float(i) / float(num_segments)
        circle_verts.extend([0.5 * math.cos(theta), 0.5 * math.sin(theta)])
    circle_verts = np.array(circle_verts, dtype=np.float32)
    vao_circle = create_vao(circle_verts)

    # LOOP DE RENDERIZAÇÃO
    while not glfw.window_should_close(window):
        glfw.poll_events()
        
        width, height = glfw.get_framebuffer_size(window)
        hw, hh = width // 2, height // 2
        
        # Limpar a tela inteira com a cor da borda/fundo global
        glViewport(0, 0, width, height)
        glDisable(GL_SCISSOR_TEST)
        glClearColor(0.2, 0.2, 0.2, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Definições dos 4 Viewports (X, Y, Largura, Altura)
        viewports = [
            (0, hh, hw, hh),   # Top-Left (Triângulo)
            (hw, hh, hw, hh),  # Top-Right (Texto)
            (0, 0, hw, hh),    # Bottom-Left (Retângulo)
            (hw, 0, hw, hh)    # Bottom-Right (Círculo)
        ]
        
        # Renderizar cada viewport
        for i in range(4):
            x, y, w, h = viewports[i]
            
            # (Código existente do Scissor e Viewport...)
            glViewport(x, y, w, h)
            glScissor(x+2, y+2, w-4, h-4)
            glEnable(GL_SCISSOR_TEST)
            
            if i == active_viewport:
                glClearColor(0.9, 0.9, 0.8, 1.0)
            else:
                glClearColor(1.0, 1.0, 1.0, 1.0)
                
            glClear(GL_COLOR_BUFFER_BIT)
            
            # --- ADICIONE O CÁLCULO DA PROPORÇÃO AQUI ---
            aspect_ratio = width / height if height > 0 else 1.0
            
            # Configurar variáveis uniformes do shader
            glUniform2f(offset_loc, obj_states[i]["offset"][0], obj_states[i]["offset"][1])
            glUniform1f(scale_loc, obj_states[i]["scale"])
            glUniform1f(aspect_loc, aspect_ratio) # ENVIE O ASPECT RATIO PARA O SHADER
            # Desenhar as formas específicas
            if i == 0:
                glUniform3f(color_loc, 0.0, 0.5, 0.8) # Azul
                glBindVertexArray(vao_tri)
                glDrawArrays(GL_TRIANGLES, 0, 3)
            elif i == 1:
                glUniform3f(color_loc, 0.0, 0.0, 0.0) # Preto
                glBindVertexArray(vao_cd)
                glDrawArrays(GL_LINES, 0, 18)
            elif i == 2:
                glUniform3f(color_loc, 0.8, 0.2, 0.2) # Vermelho
                glBindVertexArray(vao_rect)
                glDrawArrays(GL_TRIANGLES, 0, 6)
            elif i == 3:
                glUniform3f(color_loc, 0.2, 0.8, 0.2) # Verde
                glBindVertexArray(vao_circle)
                glDrawArrays(GL_TRIANGLE_FAN, 0, num_segments + 1)
                
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()