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

class Camera:
    """Classe para gerenciar a câmera em primeira pessoa"""
    def __init__(self, position=np.array([3.0, 3.0, 5.0]), yaw=-135.0, pitch=35.0):
        self.position = position
        self.world_up = np.array([0.0, 1.0, 0.0])
        self.yaw = yaw  # Ângulo em torno do eixo Y (em graus)
        self.pitch = pitch  # Ângulo em torno do eixo X (em graus)
        self.sensitivity = 0.1
        self.speed = 5.0
        
        self.front = np.array([0.0, 0.0, -1.0])
        self.right = np.array([1.0, 0.0, 0.0])
        self.up = np.array([0.0, 1.0, 0.0])
        
        self.update_camera_vectors()
    
    def update_camera_vectors(self):
        """Atualiza os vetores da câmera baseados nos ângulos yaw e pitch"""
        # Calcular o vetor front
        front_x = math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        front_y = math.sin(math.radians(self.pitch))
        front_z = math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        self.front = np.array([front_x, front_y, front_z])
        self.front = self.front / np.linalg.norm(self.front)
        
        # Calcular vetor right
        self.right = np.cross(self.front, self.world_up)
        self.right = self.right / np.linalg.norm(self.right)
        
        # Calcular vetor up
        self.up = np.cross(self.right, self.front)
        self.up = self.up / np.linalg.norm(self.up)
    
    def get_view_matrix(self):
        """Retorna a matriz de view (look-at) para a câmera"""
        target = self.position + self.front
        return get_view_matrix(self.position, target, self.up)
    
    def process_keyboard(self, keys, delta_time):
        """Processa entrada do teclado para movimento da câmera"""
        velocity = self.speed * delta_time
        
        if keys[glfw.KEY_W]:
            self.position += self.front * velocity
        if keys[glfw.KEY_S]:
            self.position -= self.front * velocity
        if keys[glfw.KEY_A]:
            self.position -= self.right * velocity
        if keys[glfw.KEY_D]:
            self.position += self.right * velocity
        if keys[glfw.KEY_SPACE]:
            self.position += self.world_up * velocity
        if keys[glfw.KEY_LEFT_SHIFT]:
            self.position -= self.world_up * velocity
    
    def process_mouse(self, x_offset, y_offset):
        """Processa entrada do mouse para rotação da câmera"""
        self.yaw += x_offset * self.sensitivity
        self.pitch += y_offset * self.sensitivity
        
        # Limitar pitch para evitar gimbal lock
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0
        
        self.update_camera_vectors()

class Transformations:
    """Classe para gerenciar as transformações do cubo"""
    def __init__(self):
        self.translation_x = 0.0
        self.translation_y = 0.0
        self.translation_z = 0.0
        self.rotation_angle_x = 0.0  # Rotação em X
        self.rotation_angle_y = 0.0  # Rotação em Y
        self.rotation_angle_z = 0.0  # Rotação em Z
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.scale_z = 1.0
    
    def get_model_matrix(self):
        """Retorna a matriz de modelo combinando translação, rotações e escala"""
        # Matriz de translação
        translation = np.array([
            [1, 0, 0, self.translation_x],
            [0, 1, 0, self.translation_y],
            [0, 0, 1, self.translation_z],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        # Matriz de rotação em X
        rad_x = math.radians(self.rotation_angle_x)
        cos_x = math.cos(rad_x)
        sin_x = math.sin(rad_x)
        rotation_x = np.array([
            [1, 0, 0, 0],
            [0, cos_x, -sin_x, 0],
            [0, sin_x, cos_x, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        # Matriz de rotação em Y
        rad_y = math.radians(self.rotation_angle_y)
        cos_y = math.cos(rad_y)
        sin_y = math.sin(rad_y)
        rotation_y = np.array([
            [cos_y, 0, sin_y, 0],
            [0, 1, 0, 0],
            [-sin_y, 0, cos_y, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        # Matriz de rotação em Z
        rad_z = math.radians(self.rotation_angle_z)
        cos_z = math.cos(rad_z)
        sin_z = math.sin(rad_z)
        rotation_z = np.array([
            [cos_z, -sin_z, 0, 0],
            [sin_z, cos_z, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        # Matriz de escala
        scale = np.array([
            [self.scale_x, 0, 0, 0],
            [0, self.scale_y, 0, 0],
            [0, 0, self.scale_z, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        # Combinar transformações: Translação * RotaçãoZ * RotaçãoY * RotaçãoX * Escala
        model = translation @ rotation_z @ rotation_y @ rotation_x @ scale
        return model
    
    def reset(self):
        """Reseta todas as transformações"""
        self.translation_x = 0.0
        self.translation_y = 0.0
        self.translation_z = 0.0
        self.rotation_angle_x = 0.0
        self.rotation_angle_y = 0.0
        self.rotation_angle_z = 0.0
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.scale_z = 1.0

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

def get_view_matrix(eye_pos, target_pos, up):
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

def create_cube_data():
    """Cria os vértices e índices para um cubo colorido"""
    vertices = np.array([
        # Posições        # Cores (RGB)
        # Frente (Z = 0.5)
        -0.5, -0.5,  0.5,  1.0, 0.0, 0.0,  # 0 - Vermelho
         0.5, -0.5,  0.5,  1.0, 0.0, 0.0,  # 1 - Vermelho
         0.5,  0.5,  0.5,  1.0, 0.0, 0.0,  # 2 - Vermelho
        -0.5,  0.5,  0.5,  1.0, 0.0, 0.0,  # 3 - Vermelho
        
        # Trás (Z = -0.5)
        -0.5, -0.5, -0.5,  0.0, 1.0, 0.0,  # 4 - Verde
         0.5, -0.5, -0.5,  0.0, 1.0, 0.0,  # 5 - Verde
         0.5,  0.5, -0.5,  0.0, 1.0, 0.0,  # 6 - Verde
        -0.5,  0.5, -0.5,  0.0, 1.0, 0.0,  # 7 - Verde
        
        # Cima (Y = 0.5)
        -0.5,  0.5, -0.5,  0.0, 0.0, 1.0,  # 8 - Azul
         0.5,  0.5, -0.5,  0.0, 0.0, 1.0,  # 9 - Azul
         0.5,  0.5,  0.5,  0.0, 0.0, 1.0,  # 10 - Azul
        -0.5,  0.5,  0.5,  0.0, 0.0, 1.0,  # 11 - Azul
        
        # Baixo (Y = -0.5)
        -0.5, -0.5, -0.5,  1.0, 1.0, 0.0,  # 12 - Amarelo
         0.5, -0.5, -0.5,  1.0, 1.0, 0.0,  # 13 - Amarelo
         0.5, -0.5,  0.5,  1.0, 1.0, 0.0,  # 14 - Amarelo
        -0.5, -0.5,  0.5,  1.0, 1.0, 0.0,  # 15 - Amarelo
        
        # Direita (X = 0.5)
         0.5, -0.5, -0.5,  1.0, 0.0, 1.0,  # 16 - Magenta
         0.5,  0.5, -0.5,  1.0, 0.0, 1.0,  # 17 - Magenta
         0.5,  0.5,  0.5,  1.0, 0.0, 1.0,  # 18 - Magenta
         0.5, -0.5,  0.5,  1.0, 0.0, 1.0,  # 19 - Magenta
        
        # Esquerda (X = -0.5)
        -0.5, -0.5, -0.5,  0.0, 1.0, 1.0,  # 20 - Ciano
        -0.5,  0.5, -0.5,  0.0, 1.0, 1.0,  # 21 - Ciano
        -0.5,  0.5,  0.5,  0.0, 1.0, 1.0,  # 22 - Ciano
        -0.5, -0.5,  0.5,  0.0, 1.0, 1.0   # 23 - Ciano
    ], dtype=np.float32)
        
    # Índices para desenhar as arestas do cubo (LINE_LOOP para cada face)
    indices = np.array([
        # Face frontal (Vermelha)
        0, 1, 2, 3,
        # Face traseira (Verde)
        4, 5, 6, 7,
        # Face superior (Azul)
        8, 9, 10, 11,
        # Face inferior (Amarela)
        12, 13, 14, 15,
        # Face direita (Magenta)
        16, 17, 18, 19,
        # Face esquerda (Ciano)
        20, 21, 22, 23
    ], dtype=np.uint32)

    return vertices, indices

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
    """Callback para teclado - controla as transformações do cubo e modos da câmera"""
    if action == glfw.PRESS:
        transforms = glfw.get_window_user_pointer(window)
        if transforms is None:
            return
        
        # Reset das transformações do cubo
        if key == glfw.KEY_R:
            transforms.reset()
            print("\n--- TRANSFORMAÇÕES DO CUBO RESETADAS ---")
            print("----------------------------------------\n")
        
        # Sair
        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)

def mouse_callback(window, xpos, ypos):
    """Callback para movimento do mouse"""
    if not glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT):
        return
    
    # Obter estado do mouse
    global first_mouse, last_x, last_y
    
    if first_mouse:
        last_x = xpos
        last_y = ypos
        first_mouse = False
    
    x_offset = xpos - last_x
    y_offset = last_y - ypos  # Invertido para coordenadas corretas
    
    last_x = xpos
    last_y = ypos
    
    camera = glfw.get_window_user_pointer(window)
    if isinstance(camera, Camera):
        camera.process_mouse(x_offset, y_offset)

def print_controls():
    """Imprime os controles no console"""
    print("\n" + "="*60)
    print("CUBO 3D - CONTROLES DE CÂMERA E TRANSFORMAÇÕES")
    print("="*60)
    print("\nCÂMERA EM PRIMEIRA PESSOA:")
    print("  Mouse esquerdo + mover mouse - Olhar ao redor")
    print("  W/A/S/D - Movimentar no plano XZ")
    print("  ESPAÇO   - Subir")
    print("  SHIFT    - Descer")
    print("\nTRANSFORMAÇÕES DO CUBO:")
    print("  ← →   - Mover cubo esquerda/direita (X)")
    print("  ↑ ↓   - Mover cubo cima/baixo (Y)")
    print("  I/K   - Mover cubo frente/trás (Z)")
    print("  X/Y/Z - Rotacionar cubo nos eixos X, Y, Z")
    print("  W/S   - Escala do cubo em X")
    print("  A/D   - Escala do cubo em Y")
    print("  E/Q   - Escala do cubo em Z")
    print("\nOUTROS:")
    print("  R     - Resetar transformações do cubo")
    print("  ESC   - Sair")
    print("\nDica: A câmera inicia atrás do cubo. Use WASD para se mover ao redor!")
    print("="*60 + "\n")

def process_cube_transformations(window, transforms, key, action):
    """Processa transformações específicas do cubo"""
    if action != glfw.PRESS and action != glfw.REPEAT:
        return
    
    # Translação do cubo
    if key == glfw.KEY_RIGHT:
        transforms.translation_x += 0.1
        print(f"Cubo - Translação X: {transforms.translation_x:.2f}")
    elif key == glfw.KEY_LEFT:
        transforms.translation_x -= 0.1
        print(f"Cubo - Translação X: {transforms.translation_x:.2f}")
    elif key == glfw.KEY_UP:
        transforms.translation_y += 0.1
        print(f"Cubo - Translação Y: {transforms.translation_y:.2f}")
    elif key == glfw.KEY_DOWN:
        transforms.translation_y -= 0.1
        print(f"Cubo - Translação Y: {transforms.translation_y:.2f}")
    elif key == glfw.KEY_I:
        transforms.translation_z -= 0.1
        print(f"Cubo - Translação Z: {transforms.translation_z:.2f}")
    elif key == glfw.KEY_K:
        transforms.translation_z += 0.1
        print(f"Cubo - Translação Z: {transforms.translation_z:.2f}")
    
    # Rotação do cubo
    elif key == glfw.KEY_X:
        transforms.rotation_angle_x += 15.0
        print(f"Cubo - Rotação X: {transforms.rotation_angle_x:.1f}°")
    elif key == glfw.KEY_Y:
        transforms.rotation_angle_y += 15.0
        print(f"Cubo - Rotação Y: {transforms.rotation_angle_y:.1f}°")
    elif key == glfw.KEY_Z:
        transforms.rotation_angle_z += 15.0
        print(f"Cubo - Rotação Z: {transforms.rotation_angle_z:.1f}°")
    
    # Escala do cubo
    elif key == glfw.KEY_W:
        transforms.scale_x += 0.1
        print(f"Cubo - Escala X: {transforms.scale_x:.2f}")
    elif key == glfw.KEY_S:
        transforms.scale_x -= 0.1
        if transforms.scale_x < 0.1:
            transforms.scale_x = 0.1
        print(f"Cubo - Escala X: {transforms.scale_x:.2f}")
    elif key == glfw.KEY_A:
        transforms.scale_y += 0.1
        print(f"Cubo - Escala Y: {transforms.scale_y:.2f}")
    elif key == glfw.KEY_D:
        transforms.scale_y -= 0.1
        if transforms.scale_y < 0.1:
            transforms.scale_y = 0.1
        print(f"Cubo - Escala Y: {transforms.scale_y:.2f}")
    elif key == glfw.KEY_E:
        transforms.scale_z += 0.1
        print(f"Cubo - Escala Z: {transforms.scale_z:.2f}")
    elif key == glfw.KEY_Q:
        transforms.scale_z -= 0.1
        if transforms.scale_z < 0.1:
            transforms.scale_z = 0.1
        print(f"Cubo - Escala Z: {transforms.scale_z:.2f}")

def main():
    # Inicializar GLFW
    if not glfw.init():
        sys.exit("Falha ao inicializar GLFW")
    
    # Configurar a janela
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.DEPTH_BITS, 24)
    
    # Criar janela
    window = glfw.create_window(800, 600, "Cubo 3D - UNILAB (Câmera em Primeira Pessoa)", None, None)
    if not window:
        glfw.terminate()
        sys.exit("Falha ao criar janela")
    
    glfw.make_context_current(window)
    
    # Desabilitar cursor para melhor experiência em primeira pessoa
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    
    # Criar objeto de transformações do cubo
    transforms = Transformations()
    
    # Criar câmera em primeira pessoa (posicionada atrás do cubo)
    camera = Camera(position=np.array([3.0, 3.0, 5.0]), yaw=-135.0, pitch=35.0)
    
    # Criar e compilar shaders
    shader_program = create_shader_program()
    if not shader_program:
        glfw.terminate()
        sys.exit("Falha ao criar shader program")
    
    # Armazenar dados na janela
    glfw.set_window_user_pointer(window, camera)
    
    # Configurar callbacks
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_key_callback(window, key_callback)
    glfw.set_cursor_pos_callback(window, mouse_callback)
    
    # Variáveis globais para mouse
    global first_mouse, last_x, last_y
    first_mouse = True
    last_x = 400
    last_y = 300
    
    # Criar dados do cubo
    vertices, indices = create_cube_data()
    
    # Criar Vertex Array Object (VAO)
    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)
    
    # Criar Vertex Buffer Object (VBO) para vértices
    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    
    # Criar Element Buffer Object (EBO) para índices
    EBO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
    
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
    glEnable(GL_DEPTH_TEST)  # Habilitar teste de profundidade
    glLineWidth(2.0)
    
    # Configurar projeção inicial (perspectiva)
    width, height = glfw.get_framebuffer_size(window)
    aspect_ratio = width / height if height > 0 else 1.0
    projection = get_projection_matrix_perspective(45.0, aspect_ratio, 0.1, 100.0)
    
    glUseProgram(shader_program)
    projection_loc = glGetUniformLocation(shader_program, "projection")
    glUniformMatrix4fv(projection_loc, 1, GL_TRUE, projection)
    
    # Obter localização da matriz model
    model_loc = glGetUniformLocation(shader_program, "model")
    
    # Configurar view matrix inicial
    view_loc = glGetUniformLocation(shader_program, "view")
    
    # Imprimir controles
    print_controls()
    
    # Timer para delta time
    last_time = glfw.get_time()
    
    # Teclas pressionadas para movimento contínuo
    keys_pressed = {}
    
    # Loop principal
    while not glfw.window_should_close(window):
        # Calcular delta time
        current_time = glfw.get_time()
        delta_time = current_time - last_time
        last_time = current_time
        
        # Processar eventos
        glfw.poll_events()
        
        # Verificar teclas para transformações do cubo
        for key in [glfw.KEY_RIGHT, glfw.KEY_LEFT, glfw.KEY_UP, glfw.KEY_DOWN,
                    glfw.KEY_I, glfw.KEY_K, glfw.KEY_X, glfw.KEY_Y, glfw.KEY_Z,
                    glfw.KEY_W, glfw.KEY_S, glfw.KEY_A, glfw.KEY_D, glfw.KEY_E, glfw.KEY_Q,
                    glfw.KEY_R, glfw.KEY_ESCAPE]:
            if glfw.get_key(window, key) == glfw.PRESS:
                if key == glfw.KEY_ESCAPE:
                    glfw.set_window_should_close(window, True)
                elif key == glfw.KEY_R:
                    transforms.reset()
                    print("\n--- TRANSFORMAÇÕES DO CUBO RESETADAS ---")
                    print("----------------------------------------\n")
                else:
                    process_cube_transformations(window, transforms, key, glfw.PRESS)
        
        # Movimento da câmera baseado em teclas pressionadas
        for key in [glfw.KEY_W, glfw.KEY_S, glfw.KEY_A, glfw.KEY_D, glfw.KEY_SPACE, glfw.KEY_LEFT_SHIFT]:
            keys_pressed[key] = glfw.get_key(window, key) == glfw.PRESS
        
        camera.process_keyboard(keys_pressed, delta_time)
        
        # Limpar buffers de cor e profundidade
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Atualizar matriz de view da câmera
        view_matrix = camera.get_view_matrix()
        glUniformMatrix4fv(view_loc, 1, GL_TRUE, view_matrix)
        
        # Aplicar matriz de modelo do cubo
        model_matrix = transforms.get_model_matrix()
        glUniformMatrix4fv(model_loc, 1, GL_TRUE, model_matrix)
        
        # Desenhar o cubo
        glBindVertexArray(VAO)
        
        # Desenhar as faces como linhas (wireframe)
        for i in range(6):  # 6 faces
            glDrawElements(GL_LINE_LOOP, 4, GL_UNSIGNED_INT, ctypes.c_void_p(i * 4 * 4))
        
        glfw.swap_buffers(window)
    
    # Limpar recursos
    glDeleteVertexArrays(1, [VAO])
    glDeleteBuffers(1, [VBO])
    glDeleteBuffers(1, [EBO])
    glDeleteProgram(shader_program)
    glfw.terminate()

if __name__ == "__main__":
    main()