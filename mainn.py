import glfw
from OpenGL.GL import *
import numpy as np
import time  
glfw.init()
glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
window = glfw.create_window(800, 600, "Linhas", None, None)
glfw.make_context_current(window)
VERTEX_CODE = """
        attribute vec2 position;
        void main(){
            gl_Position = vec4(position,0.0,1.0);
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
# (-1,0),(0,1),(0,0)
vertices = np.zeros(2, [("position", np.float32, 2)])
#vertices['position'] = [(-0.5,-0.5),(0.5,-0.5),(0,0.5)]
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
glEnableVertexAttribArray(loc)
glVertexAttribPointer(loc, 2, GL_FLOAT, False, stride, offset)
glfw.show_window(window)

# Variáveis para medição detalhada
frame_count = 0
total_time = 0.0
min_time = float('inf')
max_time = 0.0
draw_times = []  # Para armazenar os tempos


def algoritmo_drawlineeqreta(x1, y1, x2, y2):

  
    


def algoritmo_drawline(x1, y1, x2, y2):
    # Converter para coordenadas normalizadas (-1 a 1)
    def normalizar(x, y):
        x_norm = (x / 800) * 2 - 1
        y_norm = (y / 600) * 2 - 1
        return x_norm, y_norm

    x1, y1 = normalizar(x1, y1)
    x2, y2 = normalizar(x2, y2)

    # Atualizar os vértices com as coordenadas normalizadas
    vertices['position'] = [(x1, y1), (x2, y2)]
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)

while not glfw.window_should_close(window):
    glfw.poll_events()
    glClear(GL_COLOR_BUFFER_BIT)
    glClearColor(1.0, 1.0, 1.0, 1.0)  
    glUniform4f(loc_color, R, G, B, 1.0)
    glLineWidth(5.0)
    # Medição com alta precisão
    start_time = time.perf_counter_ns()  # Nanosegundos

    algoritmo_drawline(0, 0, 500, 500)  # Exemplo de chamada do algoritmo de desenho de linha
    glDrawArrays(GL_LINE_LOOP, 0, len(vertices))

    end_time = time.perf_counter_ns()
    draw_time = (end_time - start_time) / 1000  # Converter para microssegundos

    # Atualizar estatísticas
    total_time += draw_time
    frame_count += 1
    draw_times.append(draw_time)

    if draw_time < min_time:
        min_time = draw_time
    if draw_time > max_time:
        max_time = draw_time

      # Exibir a cada 30 frames
    if frame_count % 30 == 0:
        avg_time = total_time / frame_count
        print(f"\nFrame {frame_count}:")
        print(f"  Último tempo: {draw_time:.2f} µs ({draw_time/1000:.4f} ms)")
        print(f"  Média:       {avg_time:.2f} µs ({avg_time/1000:.4f} ms)")
        print(f"  Mínimo:      {min_time:.2f} µs")
        print(f"  Máximo:      {max_time:.2f} µs")

    glfw.swap_buffers(window)
glfw.terminate()