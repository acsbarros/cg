import glfw
from OpenGL.GL import *
import numpy as np
import sys
import ctypes

# Vertex shader source code com suporte a matriz de projeção
vertex_shader_source = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;

uniform mat4 projection;

out vec3 ourColor;

void main()
{
    gl_Position = projection * vec4(aPos, 1.0);
    ourColor = aColor;
}
"""

# Fragment shader source code
fragment_shader_source = """
#version 330 core
in vec3 ourColor;
out vec4 FragColor;

void main()
{
    FragColor = vec4(ourColor, 1.0);
}
"""

def compile_shader(source, shader_type):
    """Compila um shader e retorna seu ID"""
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    
    # Verificar erros de compilação
    success = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not success:
        info_log = glGetShaderInfoLog(shader)
        shader_type_name = "VERTEX" if shader_type == GL_VERTEX_SHADER else "FRAGMENT"
        print(f"Erro ao compilar {shader_type_name} shader:\n{info_log}")
        glDeleteShader(shader)
        return None
    
    return shader

def create_shader_program():
    """Cria e linka o programa de shader"""
    vertex_shader = compile_shader(vertex_shader_source, GL_VERTEX_SHADER)
    if not vertex_shader:
        return None
    
    fragment_shader = compile_shader(fragment_shader_source, GL_FRAGMENT_SHADER)
    if not fragment_shader:
        glDeleteShader(vertex_shader)
        return None
    
    shader_program = glCreateProgram()
    glAttachShader(shader_program, vertex_shader)
    glAttachShader(shader_program, fragment_shader)
    glLinkProgram(shader_program)
    
    # Verificar erros de linking
    success = glGetProgramiv(shader_program, GL_LINK_STATUS)
    if not success:
        info_log = glGetProgramInfoLog(shader_program)
        print(f"Erro ao linkar shader program:\n{info_log}")
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)
        glDeleteProgram(shader_program)
        return None
    
    # Limpar shaders
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)
    
    return shader_program

def get_projection_matrix(width, height):
    """
    Cria uma matriz de projeção ortográfica que mantém a proporção do triângulo
    independentemente da proporção da janela.
    """
    if height == 0:
        height = 1
    
    # Matriz de projeção ortográfica
    # Define o sistema de coordenadas: x de -1 a 1, y de -1 a 1
    # Mas ajusta baseado na proporção da tela
    
    aspect_ratio = width / height
    
    if aspect_ratio > 1:
        # Janela mais larga que alta
        left = -aspect_ratio
        right = aspect_ratio
        bottom = -1.0
        top = 1.0
    else:
        # Janela mais alta que larga
        left = -1.0
        right = 1.0
        bottom = -1.0 / aspect_ratio
        top = 1.0 / aspect_ratio
    
    # Criar matriz de projeção ortográfica
    projection = np.array([
        [2.0/(right-left), 0.0, 0.0, -(right+left)/(right-left)],
        [0.0, 2.0/(top-bottom), 0.0, -(top+bottom)/(top-bottom)],
        [0.0, 0.0, -1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ], dtype=np.float32)
    
    return projection

def framebuffer_size_callback(window, width, height):
    """Callback chamado quando a janela é redimensionada"""
    # Atualizar a viewport para a nova resolução
    glViewport(0, 0, width, height)
    
    # Atualizar a matriz de projeção no shader
    projection = get_projection_matrix(width, height)
    
    # Obter o shader program atual e atualizar a uniform
    shader_program = glfw.get_window_user_pointer(window)
    if shader_program:
        glUseProgram(shader_program)
        projection_loc = glGetUniformLocation(shader_program, "projection")
        glUniformMatrix4fv(projection_loc, 1, GL_TRUE, projection)

def main():
    # Inicializar GLFW
    if not glfw.init():
        sys.exit("Falha ao inicializar GLFW")
    
    # Configurar a janela
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.RESIZABLE, GL_TRUE)  # Permitir redimensionamento
    
    # Criar janela
    window = glfw.create_window(800, 600, "OpenGL Moderno - UNILAB (Redimensionável)", None, None)
    if not window:
        glfw.terminate()
        sys.exit("Falha ao criar janela")
    
    glfw.make_context_current(window)
    
    # Criar e compilar shaders
    shader_program = create_shader_program()
    if not shader_program:
        glfw.terminate()
        sys.exit("Falha ao criar shader program")
    
    # Armazenar o shader program na janela para uso no callback
    glfw.set_window_user_pointer(window, shader_program)
    
    # Configurar callback de redimensionamento
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    
    # Definir dados do triângulo
    vertices = np.array([
        # Posições        # Cores
        -0.5, -0.5, 0.0,  1.0, 0.0, 0.0,  # Vértice 1 - Vermelho
         0.5, -0.5, 0.0,  1.0, 0.0, 0.0,  # Vértice 2 - Verde
         0.0,  0.5, 0.0,  1.0, 0.0, 0.0   # Vértice 3 - Azul
    ], dtype=np.float32)
    
    # Criar Vertex Array Object (VAO)
    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)
    
    # Criar Vertex Buffer Object (VBO)
    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    
    # Configurar atributo de posição (location = 0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(GLfloat), ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    
    # Configurar atributo de cor (location = 1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(GLfloat), ctypes.c_void_p(3 * sizeof(GLfloat)))
    glEnableVertexAttribArray(1)
    
    # Desvincular VAO
    glBindVertexArray(0)
    
    # Configurações de renderização
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glPointSize(8.0)
    glLineWidth(2.0)
    
    # Configurar projeção inicial
    width, height = glfw.get_framebuffer_size(window)
    projection = get_projection_matrix(width, height)
    
    glUseProgram(shader_program)
    projection_loc = glGetUniformLocation(shader_program, "projection")
    glUniformMatrix4fv(projection_loc, 1, GL_TRUE, projection)
    
    # Loop principal
    while not glfw.window_should_close(window):
        # Limpar a tela
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Desenhar as arestas
        glBindVertexArray(VAO)
        glDrawArrays(GL_LINE_LOOP, 0, 3)
        
        # Desenhar os vértices
        glDrawArrays(GL_POINTS, 0, 3)
        
        glfw.swap_buffers(window)
        glfw.poll_events()
    
    # Limpar recursos
    glDeleteVertexArrays(1, [VAO])
    glDeleteBuffers(1, [VBO])
    glDeleteProgram(shader_program)
    glfw.terminate()

if __name__ == "__main__":
    main()