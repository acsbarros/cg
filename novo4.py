import glfw
from OpenGL.GL import *
import numpy as np
import sys
import ctypes
import math

# Vertex shader source code com suporte a matriz de modelo, view e projeção
vertex_shader_source = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;

out vec3 ourColor;

void main()
{
    gl_Position = projection * view * model * vec4(aPos, 1.0);
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

class Transformations:
    """Classe para gerenciar as transformações do triângulo"""
    def __init__(self):
        self.translation_x = 0.0
        self.translation_y = 0.0
        self.translation_z = 0.0  # Adicionado para movimento em profundidade
        self.rotation_angle = 0.0
        self.scale_x = 1.0
        self.scale_y = 1.0
    
    def get_model_matrix(self):
        """Retorna a matriz de modelo combinando translação, rotação e escala"""
        # Matriz de translação (agora com Z)
        translation = np.array([
            [1, 0, 0, self.translation_x],
            [0, 1, 0, self.translation_y],
            [0, 0, 1, self.translation_z],  # Movimento em Z agora é visível na perspectiva
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        # Matriz de rotação
        rad = math.radians(self.rotation_angle)
        cos_r = math.cos(rad)
        sin_r = math.sin(rad)
        rotation = np.array([
            [cos_r, -sin_r, 0, 0],
            [sin_r,  cos_r, 0, 0],
            [0,      0,     1, 0],
            [0,      0,     0, 1]
        ], dtype=np.float32)
        
        # Matriz de escala
        scale = np.array([
            [self.scale_x, 0, 0, 0],
            [0, self.scale_y, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        # Combinar transformações
        model = translation @ rotation @ scale
        return model
    
    def reset(self):
        """Reseta todas as transformações"""
        self.translation_x = 0.0
        self.translation_y = 0.0
        self.translation_z = 0.0
        self.rotation_angle = 0.0
        self.scale_x = 1.0
        self.scale_y = 1.0

def compile_shader(source, shader_type):
    """Compila um shader e retorna seu ID"""
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    
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
    
    success = glGetProgramiv(shader_program, GL_LINK_STATUS)
    if not success:
        info_log = glGetProgramInfoLog(shader_program)
        print(f"Erro ao linkar shader program:\n{info_log}")
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)
        glDeleteProgram(shader_program)
        return None
    
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)
    
    return shader_program

def get_projection_matrix_perspective(fov=45.0, aspect_ratio=1.0, near=0.1, far=100.0):
    """Cria uma matriz de projeção em perspectiva"""
    fov_rad = math.radians(fov)
    f = 1.0 / math.tan(fov_rad / 2.0)
    
    projection = np.array([
        [f / aspect_ratio, 0.0, 0.0, 0.0],
        [0.0, f, 0.0, 0.0],
        [0.0, 0.0, (far + near) / (near - far), (2.0 * far * near) / (near - far)],
        [0.0, 0.0, -1.0, 0.0]
    ], dtype=np.float32)
    
    return projection

def get_view_matrix(eye_pos=np.array([0.0, 0.0, 3.0]), 
                    target_pos=np.array([0.0, 0.0, 0.0]), 
                    up=np.array([0.0, 1.0, 0.0])):
    """Cria uma matriz de view (look-at)"""
    forward = eye_pos - target_pos
    forward = forward / np.linalg.norm(forward)
    
    right = np.cross(up, forward)
    right = right / np.linalg.norm(right)
    
    up_camera = np.cross(forward, right)
    up_camera = up_camera / np.linalg.norm(up_camera)
    
    view_matrix = np.array([
        [right[0], right[1], right[2], -np.dot(right, eye_pos)],
        [up_camera[0], up_camera[1], up_camera[2], -np.dot(up_camera, eye_pos)],
        [forward[0], forward[1], forward[2], -np.dot(forward, eye_pos)],
        [0, 0, 0, 1]
    ], dtype=np.float32)
    
    return view_matrix

def framebuffer_size_callback(window, width, height):
    """Callback chamado quando a janela é redimensionada"""
    glViewport(0, 0, width, height)
    
    current_program = glGetIntegerv(GL_CURRENT_PROGRAM)
    if current_program:
        aspect_ratio = width / height if height > 0 else 1.0
        projection = get_projection_matrix_perspective(45.0, aspect_ratio, 0.1, 100.0)
        
        projection_loc = glGetUniformLocation(current_program, "projection")
        glUniformMatrix4fv(projection_loc, 1, GL_TRUE, projection)

def key_callback(window, key, scancode, action, mods):
    """Callback para teclado - controla as transformações"""
    if action == glfw.PRESS or action == glfw.REPEAT:
        transforms = glfw.get_window_user_pointer(window)
        if transforms is None:
            return
        
        # Translação (setas para X,Y; Z com I/K)
        if key == glfw.KEY_RIGHT:
            transforms.translation_x += 0.1
            print(f"Translação X: {transforms.translation_x:.2f}")
        elif key == glfw.KEY_LEFT:
            transforms.translation_x -= 0.1
            print(f"Translação X: {transforms.translation_x:.2f}")
        elif key == glfw.KEY_UP:
            transforms.translation_y += 0.1
            print(f"Translação Y: {transforms.translation_y:.2f}")
        elif key == glfw.KEY_DOWN:
            transforms.translation_y -= 0.1
            print(f"Translação Y: {transforms.translation_y:.2f}")
        elif key == glfw.KEY_I:  # Movimento em profundidade
            transforms.translation_z -= 0.1  # Mais perto
            print(f"Translação Z: {transforms.translation_z:.2f}")
        elif key == glfw.KEY_K:  # Movimento em profundidade
            transforms.translation_z += 0.1  # Mais longe
            print(f"Translação Z: {transforms.translation_z:.2f}")
        
        # Rotação
        elif key == glfw.KEY_Q:
            transforms.rotation_angle -= 15.0
            print(f"Rotação: {transforms.rotation_angle:.1f}°")
        elif key == glfw.KEY_E:
            transforms.rotation_angle += 15.0
            print(f"Rotação: {transforms.rotation_angle:.1f}°")
        
        # Escala
        elif key == glfw.KEY_W:
            transforms.scale_x += 0.1
            print(f"Escala X: {transforms.scale_x:.2f}")
        elif key == glfw.KEY_S:
            transforms.scale_x -= 0.1
            if transforms.scale_x < 0.1:
                transforms.scale_x = 0.1
            print(f"Escala X: {transforms.scale_x:.2f}")
        elif key == glfw.KEY_A:
            transforms.scale_y += 0.1
            print(f"Escala Y: {transforms.scale_y:.2f}")
        elif key == glfw.KEY_D:
            transforms.scale_y -= 0.1
            if transforms.scale_y < 0.1:
                transforms.scale_y = 0.1
            print(f"Escala Y: {transforms.scale_y:.2f}")
        
        # Reset
        elif key == glfw.KEY_R:
            transforms.reset()
            print("\n--- TRANSFORMAÇÕES RESETADAS ---")
            print("-------------------------------\n")
        
        # Sair
        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)

def print_controls():
    """Imprime os controles no console"""
    print("\n" + "="*60)
    print("CONTROLES DE TRANSFORMAÇÕES GEOMÉTRICAS")
    print("="*60)
    print("Translação:")
    print("  ← →   - Mover para esquerda/direita")
    print("  ↑ ↓   - Mover para cima/baixo")
    print("  I     - Mover para frente (aproximar)")
    print("  K     - Mover para trás (afastar)")
    print("\nRotação:")
    print("  Q     - Rotacionar anti-horário")
    print("  E     - Rotacionar horário")
    print("\nEscala:")
    print("  W     - Aumentar escala em X")
    print("  S     - Diminuir escala em X")
    print("  A     - Aumentar escala em Y")
    print("  D     - Diminuir escala em Y")
    print("\nOutros:")
    print("  R     - Resetar todas as transformações")
    print("  ESC   - Sair")
    print("="*60 + "\n")

def main():
    # Inicializar GLFW
    if not glfw.init():
        sys.exit("Falha ao inicializar GLFW")
    
    # Configurar a janela
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    
    # Criar janela
    window = glfw.create_window(800, 600, "Projeção em Perspectiva - UNILAB", None, None)
    if not window:
        glfw.terminate()
        sys.exit("Falha ao criar janela")
    
    glfw.make_context_current(window)
    
    # Criar objeto de transformações
    transforms = Transformations()
    
    # Criar e compilar shaders
    shader_program = create_shader_program()
    if not shader_program:
        glfw.terminate()
        sys.exit("Falha ao criar shader program")
    
    # Armazenar dados na janela
    glfw.set_window_user_pointer(window, transforms)
    
    # Configurar callbacks
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_key_callback(window, key_callback)
    
    # Definir dados do triângulo
    vertices = np.array([
        # Posições        # Cores
        -0.5, -0.5, 0.0,  1.0, 0.0, 0.0,  # Vértice 1 - Vermelho
         0.5, -0.5, 0.0,  0.0, 1.0, 0.0,  # Vértice 2 - Verde
         0.0,  0.5, 0.0,  0.0, 0.0, 1.0   # Vértice 3 - Azul
    ], dtype=np.float32)
    
    # Criar VAO e VBO
    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)
    
    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    
    # Configurar atributos
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(GLfloat), ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(GLfloat), ctypes.c_void_p(3 * sizeof(GLfloat)))
    glEnableVertexAttribArray(1)
    
    glBindVertexArray(0)
    
    # Configurações de renderização
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glPointSize(8.0)
    glLineWidth(2.0)
    
    # Configurar projeção inicial (perspectiva)
    width, height = glfw.get_framebuffer_size(window)
    aspect_ratio = width / height if height > 0 else 1.0
    projection = get_projection_matrix_perspective(45.0, aspect_ratio, 0.1, 100.0)
    
    glUseProgram(shader_program)
    projection_loc = glGetUniformLocation(shader_program, "projection")
    glUniformMatrix4fv(projection_loc, 1, GL_TRUE, projection)
    
    # Configurar view matrix (câmera)
    view = get_view_matrix(eye_pos=np.array([0.0, 0.0, 3.0]), 
                          target_pos=np.array([0.0, 0.0, 0.0]), 
                          up=np.array([0.0, 1.0, 0.0]))
    view_loc = glGetUniformLocation(shader_program, "view")
    glUniformMatrix4fv(view_loc, 1, GL_TRUE, view)
    
    # Obter localização da matriz model
    model_loc = glGetUniformLocation(shader_program, "model")
    
    # Imprimir controles
    print_controls()
    
    # Loop principal
    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Aplicar matriz de modelo
        model_matrix = transforms.get_model_matrix()
        glUniformMatrix4fv(model_loc, 1, GL_TRUE, model_matrix)
        
        # Desenhar
        glBindVertexArray(VAO)
        glDrawArrays(GL_LINE_LOOP, 0, 3)
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