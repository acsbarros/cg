import glfw
from OpenGL.GL import *
import numpy as np
import ctypes

# Constantes
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Inicialização GLFW
glfw.init()
glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Algoritmo Bresenham Original", None, None)
glfw.make_context_current(window)

# Código dos shaders
VERTEX_CODE = """
        attribute vec2 position;
        attribute vec3 color_attr;
        varying vec3 frag_color;
        void main(){
            gl_Position = vec4(position,0.0,1.0);
            frag_color = color_attr;
        }
        """

FRAGMENT_CODE = """
        varying vec3 frag_color;
        void main(){
            gl_FragColor = vec4(frag_color,1.0);
        }
        """

# Compilar shaders
def compilar_shader(codigo, tipo):
    shader = glCreateShader(tipo)
    glShaderSource(shader, codigo)
    glCompileShader(shader)
    
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        error = glGetShaderInfoLog(shader).decode()
        print(f"Erro no shader: {error}")
        raise RuntimeError("Erro de compilação do shader")
    
    return shader

# Criar programa
program = glCreateProgram()
vertex = compilar_shader(VERTEX_CODE, GL_VERTEX_SHADER)
fragment = compilar_shader(FRAGMENT_CODE, GL_FRAGMENT_SHADER)

glAttachShader(program, vertex)
glAttachShader(program, fragment)
glLinkProgram(program)

if not glGetProgramiv(program, GL_LINK_STATUS):
    print(glGetProgramInfoLog(program).decode())
    raise RuntimeError('Erro no linking')

glUseProgram(program)

def bres_line_original(x1, y1, x2, y2):
    
    pontos = []
    
    # Converter para coordenadas normalizadas (-1 a 1)
    def normalizar(x, y):
        x_norm = (x / WINDOW_WIDTH) * 2 - 1
        y_norm = (y / WINDOW_HEIGHT) * 2 - 1
        return x_norm, y_norm
    
    x = x1
    y = y1
    dy = y2 - y1
    dx = x2 - x1
    
    # Tratar caso especial de linha vertical
    if dx == 0:
        if y1 > y2:
            y1, y2 = y2, y1
        for y in range(y1, y2 + 1):
            x_norm, y_norm = normalizar(x1, y)
            pontos.append((x_norm, y_norm))
        return pontos
    
    # Tratar linha com inclinação negativa
    if dx < 0:
        dx = -dx
        dy = -dy
    
    m = dy / dx
    e = m - 0.5
    
    # Garantir que desenhamos da esquerda para direita
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        dy = y2 - y1
        dx = x2 - x1
        m = dy / dx
        e = m - 0.5
        x = x1
        y = y1
    
    # Executar o algoritmo conforme especificado
    for i in range(1, dx + 1):
        # WritePixel(x, y)
        x_norm, y_norm = normalizar(x, y)
        pontos.append((x_norm, y_norm))
        
        # IF (e > 0)
        if e > 0:
            y = y + 1
            e = e - 1
        
        e = e + m
        x = x + 1
        
        # PutPixel(x, ROUND(y), color)
        y_rounded = round(y)
        x_norm, y_norm = normalizar(x, y_rounded)
        pontos.append((x_norm, y_norm))
    
    return pontos

def criar_vertices(pontos, cor):
    """Cria array de vértices com posições e cores"""
    if not pontos:
        return np.zeros(0, [("position", np.float32, 2), ("color", np.float32, 3)])
    
    n = len(pontos)
    vertices = np.zeros(n, [("position", np.float32, 2), ("color", np.float32, 3)])
    vertices['position'] = pontos
    vertices['color'] = cor
    return vertices

# Pontos iniciais (coordenadas em pixels)
x1, y1 = 100, 100
x2, y2 = 700, 500

# Gerar pontos do algoritmo
pontos = bres_line_original(x1, y1, x2, y2)

# Criar vértices com cor (branco para melhor visualização)
vertices = criar_vertices(pontos, (1.0, 1.0, 1.0))

# Criar buffer
buffer = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, buffer)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)

# Configurar atributos
stride = vertices.strides[0]
offset_position = ctypes.c_void_p(0)
offset_color = ctypes.c_void_p(vertices.dtype["position"].itemsize * 2)

loc_position = glGetAttribLocation(program, "position")
loc_color = glGetAttribLocation(program, "color_attr")

glEnableVertexAttribArray(loc_position)
glVertexAttribPointer(loc_position, 2, GL_FLOAT, False, stride, offset_position)

glEnableVertexAttribArray(loc_color)
glVertexAttribPointer(loc_color, 3, GL_FLOAT, False, stride, offset_color)

# Callbacks do teclado
def key_callback(window, key, scancode, action, mods):
    global x1, y1, x2, y2, vertices, buffer
    
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_UP:
            y2 -= 10
        elif key == glfw.KEY_DOWN:
            y2 += 10
        elif key == glfw.KEY_LEFT:
            x2 -= 10
        elif key == glfw.KEY_RIGHT:
            x2 += 10
        elif key == glfw.KEY_W:
            y1 -= 10
        elif key == glfw.KEY_S:
            y1 += 10
        elif key == glfw.KEY_A:
            x1 -= 10
        elif key == glfw.KEY_D:
            x1 += 10
        elif key == glfw.KEY_R:
            x1, y1 = 100, 100
            x2, y2 = 700, 500
        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
            return
        
        # Manter dentro dos limites
        x1 = max(10, min(WINDOW_WIDTH-10, x1))
        y1 = max(10, min(WINDOW_HEIGHT-10, y1))
        x2 = max(10, min(WINDOW_WIDTH-10, x2))
        y2 = max(10, min(WINDOW_HEIGHT-10, y2))
        
        # Regenerar pontos
        pontos = bres_line_original(x1, y1, x2, y2)
        vertices = criar_vertices(pontos, (1.0, 1.0, 1.0))
        
        # Atualizar buffer
        glBindBuffer(GL_ARRAY_BUFFER, buffer)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)

glfw.set_key_callback(window, key_callback)

# Mostrar janela
glfw.show_window(window)

# Configurar viewport
glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

# Loop principal
while not glfw.window_should_close(window):
    glfw.poll_events()
    
    glClear(GL_COLOR_BUFFER_BIT)
    glClearColor(0.1, 0.1, 0.1, 1.0)
    
    # Desenhar grade de fundo
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_LINES)
    for i in range(0, WINDOW_WIDTH, 50):
        x_norm = (i / WINDOW_WIDTH) * 2 - 1
        glVertex2f(x_norm, -1)
        glVertex2f(x_norm, 1)
    for i in range(0, WINDOW_HEIGHT, 50):
        y_norm = (i / WINDOW_HEIGHT) * 2 - 1
        glVertex2f(-1, y_norm)
        glVertex2f(1, y_norm)
    glEnd()
    
    # Desenhar a linha
    glDrawArrays(GL_POINTS, 0, len(vertices))
    
    # Desenhar pontos finais destacados
    glPointSize(8.0)
    for x, y, cor in [(x1, y1, (1, 1, 0)), (x2, y2, (1, 1, 0))]:
        x_norm = (x / WINDOW_WIDTH) * 2 - 1
        y_norm = (y / WINDOW_HEIGHT) * 2 - 1
        glColor3f(cor[0], cor[1], cor[2])
        glBegin(GL_POINTS)
        glVertex2f(x_norm, y_norm)
        glEnd()
    glPointSize(1.0)
    
    # Desenhar informações na tela (usando pontos)
    glColor3f(1.0, 1.0, 1.0)
    # Mostrar coordenadas
    info = f"P1:({x1},{y1}) P2:({x2},{y2}) | Setas: move P2 | WASD: move P1 | R: reset | ESC: sair"
    
    glfw.swap_buffers(window)

glfw.terminate()