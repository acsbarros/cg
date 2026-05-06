import glfw
from OpenGL.GL import *
import numpy as np
import sys
import ctypes
import math
from PIL import Image

# Vertex shader source code com suporte a textura
vertex_shader_source = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;

out vec2 TexCoord;

void main()
{
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    TexCoord = aTexCoord;
}
"""

# Fragment shader source code com textura
fragment_shader_source = """
#version 330 core
in vec2 TexCoord;
out vec4 FragColor;

uniform sampler2D ourTexture;

void main()
{
    FragColor = texture(ourTexture, TexCoord);
}
"""

class Camera:
    """Classe para gerenciar a câmera em primeira pessoa"""
    def __init__(self, position=np.array([0.0, 0.0, 5.0]), yaw=-90.0, pitch=0.0):
        self.position = position
        self.world_up = np.array([0.0, 1.0, 0.0])
        self.yaw = yaw
        self.pitch = pitch
        self.sensitivity = 0.1
        self.speed = 5.0
        
        self.front = np.array([0.0, 0.0, -1.0])
        self.right = np.array([1.0, 0.0, 0.0])
        self.up = np.array([0.0, 1.0, 0.0])
        
        self.update_camera_vectors()
    
    def update_camera_vectors(self):
        front_x = math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        front_y = math.sin(math.radians(self.pitch))
        front_z = math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        self.front = np.array([front_x, front_y, front_z])
        self.front = self.front / np.linalg.norm(self.front)
        
        self.right = np.cross(self.front, self.world_up)
        self.right = self.right / np.linalg.norm(self.right)
        
        self.up = np.cross(self.right, self.front)
        self.up = self.up / np.linalg.norm(self.up)
    
    def get_view_matrix(self):
        target = self.position + self.front
        return self.look_at(self.position, target, self.up)
    
    def look_at(self, eye, target, up):
        forward = eye - target
        forward = forward / np.linalg.norm(forward)
        
        right = np.cross(up, forward)
        right = right / np.linalg.norm(right)
        
        up_camera = np.cross(forward, right)
        up_camera = up_camera / np.linalg.norm(up_camera)
        
        view_matrix = np.array([
            [right[0], right[1], right[2], -np.dot(right, eye)],
            [up_camera[0], up_camera[1], up_camera[2], -np.dot(up_camera, eye)],
            [forward[0], forward[1], forward[2], -np.dot(forward, eye)],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        return view_matrix
    
    def process_keyboard(self, keys, delta_time):
        velocity = self.speed * delta_time
        
        if keys.get(glfw.KEY_W, False):
            self.position += self.front * velocity
        if keys.get(glfw.KEY_S, False):
            self.position -= self.front * velocity
        if keys.get(glfw.KEY_A, False):
            self.position -= self.right * velocity
        if keys.get(glfw.KEY_D, False):
            self.position += self.right * velocity
        if keys.get(glfw.KEY_SPACE, False):
            self.position += self.world_up * velocity
        if keys.get(glfw.KEY_LEFT_SHIFT, False):
            self.position -= self.world_up * velocity
    
    def process_mouse(self, x_offset, y_offset):
        self.yaw += x_offset * self.sensitivity
        self.pitch += y_offset * self.sensitivity
        
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0
        
        self.update_camera_vectors()
    
    def reset(self):
        self.position = np.array([0.0, 0.0, 5.0])
        self.yaw = -90.0
        self.pitch = 0.0
        self.update_camera_vectors()
        print("\n--- POSIÇÃO DA CÂMERA RESETADA ---")

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

def load_texture(image_path):
    """Carrega uma textura de um arquivo de imagem"""
    try:
        # Carregar imagem com PIL
        image = Image.open(image_path)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)  # OpenGL espera origem no canto inferior esquerdo
        img_data = np.array(image.convert('RGB'), dtype=np.uint8)
        
        # Gerar textura
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        
        # Configurar parâmetros da textura
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        # Carregar dados da imagem
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)
        
        return texture
    except Exception as e:
        print(f"Erro ao carregar textura: {e}")
        return None

def create_procedural_texture():
    """Cria uma textura procedural simples (padrão xadrez)"""
    size = 512
    texture_data = np.zeros((size, size, 3), dtype=np.uint8)
    
    # Criar padrão xadrez
    square_size = 64
    for i in range(size):
        for j in range(size):
            if ((i // square_size) + (j // square_size)) % 2 == 0:
                texture_data[i, j] = [255, 100, 100]  # Vermelho claro
            else:
                texture_data[i, j] = [100, 100, 255]  # Azul claro
    
    # Gerar textura
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, size, size, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
    glGenerateMipmap(GL_TEXTURE_2D)
    
    print("Textura procedural (xadrez) criada com sucesso!")
    return texture

def create_cube_with_texture():
    """Cria os vértices com coordenadas de textura para um cubo"""
    
    # Vértices do cubo com coordenadas de textura
    # Formato: posição (x,y,z), coordenada textura (u,v)
    vertices = np.array([
        # Face frontal (Z = 0.5)
        -0.5, -0.5,  0.5,  0.0, 0.0,
         0.5, -0.5,  0.5,  1.0, 0.0,
         0.5,  0.5,  0.5,  1.0, 1.0,
        -0.5,  0.5,  0.5,  0.0, 1.0,
        
        # Face traseira (Z = -0.5)
        -0.5, -0.5, -0.5,  0.0, 0.0,
         0.5, -0.5, -0.5,  1.0, 0.0,
         0.5,  0.5, -0.5,  1.0, 1.0,
        -0.5,  0.5, -0.5,  0.0, 1.0,
        
        # Face superior (Y = 0.5)
        -0.5,  0.5, -0.5,  0.0, 0.0,
         0.5,  0.5, -0.5,  1.0, 0.0,
         0.5,  0.5,  0.5,  1.0, 1.0,
        -0.5,  0.5,  0.5,  0.0, 1.0,
        
        # Face inferior (Y = -0.5)
        -0.5, -0.5, -0.5,  0.0, 0.0,
         0.5, -0.5, -0.5,  1.0, 0.0,
         0.5, -0.5,  0.5,  1.0, 1.0,
        -0.5, -0.5,  0.5,  0.0, 1.0,
        
        # Face direita (X = 0.5)
         0.5, -0.5, -0.5,  0.0, 0.0,
         0.5,  0.5, -0.5,  1.0, 0.0,
         0.5,  0.5,  0.5,  1.0, 1.0,
         0.5, -0.5,  0.5,  0.0, 1.0,
        
        # Face esquerda (X = -0.5)
        -0.5, -0.5, -0.5,  0.0, 0.0,
        -0.5,  0.5, -0.5,  1.0, 0.0,
        -0.5,  0.5,  0.5,  1.0, 1.0,
        -0.5, -0.5,  0.5,  0.0, 1.0
    ], dtype=np.float32)
    
    # Índices para desenhar triângulos (cada face com 2 triângulos)
    indices = np.array([
        # Face frontal - 2 triângulos
        0, 1, 2,  2, 3, 0,
        # Face traseira
        4, 5, 6,  6, 7, 4,
        # Face superior
        8, 9, 10,  10, 11, 8,
        # Face inferior
        12, 13, 14,  14, 15, 12,
        # Face direita
        16, 17, 18,  18, 19, 16,
        # Face esquerda
        20, 21, 22,  22, 23, 20
    ], dtype=np.uint32)
    
    return vertices, indices

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
    """Callback para teclado"""
    if action == glfw.PRESS:
        camera = glfw.get_window_user_pointer(window)
        if camera is None:
            return
        
        # Reset da câmera
        if key == glfw.KEY_R:
            camera.reset()
        
        # Sair
        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)

def mouse_callback(window, xpos, ypos):
    """Callback para movimento do mouse"""
    global first_mouse, last_x, last_y
    
    if first_mouse:
        last_x = xpos
        last_y = ypos
        first_mouse = False
    
    x_offset = xpos - last_x
    y_offset = last_y - ypos
    
    last_x = xpos
    last_y = ypos
    
    camera = glfw.get_window_user_pointer(window)
    if camera:
        camera.process_mouse(x_offset, y_offset)

def print_controls():
    """Imprime os controles no console"""
    print("\n" + "="*60)
    print("CÂMERA EM PRIMEIRA PESSOA - CUBO COM TEXTURA")
    print("="*60)
    print("\nMOVIMENTAÇÃO DA CÂMERA:")
    print("  Mouse + botão esquerdo - Olhar ao redor")
    print("  W/A/S/D - Movimentar no plano XZ")
    print("  ESPAÇO   - Subir")
    print("  SHIFT    - Descer")
    print("  R        - Resetar posição da câmera")
    print("  ESC      - Sair")
    print("\nTEXTURA:")
    print("  O cubo está com uma textura de padrão xadrez aplicada")
    print("  Em todas as 6 faces!")
    print("\nOBJETIVO:")
    print("  Explore o cubo texturizado de todos os ângulos!")
    print("="*60 + "\n")

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
    window = glfw.create_window(800, 600, "Câmera em Primeira Pessoa - Cubo com Textura", None, None)
    if not window:
        glfw.terminate()
        sys.exit("Falha ao criar janela")
    
    glfw.make_context_current(window)
    
    # Desabilitar cursor para melhor experiência em primeira pessoa
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    
    # Criar câmera
    camera = Camera(position=np.array([0.0, 0.0, 5.0]), yaw=-90.0, pitch=0.0)
    
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
    
    # Criar dados do cubo com textura
    vertices, indices = create_cube_with_texture()
    
    # Criar textura procedural (padrão xadrez)
    texture = create_procedural_texture()
    if not texture:
        print("Falha ao criar textura")
        glfw.terminate()
        sys.exit(1)
    
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
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    
    # Configurar atributo de coordenada de textura (location = 1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), ctypes.c_void_p(3 * sizeof(GLfloat)))
    glEnableVertexAttribArray(1)
    
    # Desvincular VAO
    glBindVertexArray(0)
    
    # Configurações de renderização
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)  # Habilitar back-face culling para melhor performance
    glCullFace(GL_BACK)
    
    # Configurar projeção inicial
    width, height = glfw.get_framebuffer_size(window)
    aspect_ratio = width / height if height > 0 else 1.0
    projection = get_projection_matrix_perspective(45.0, aspect_ratio, 0.1, 100.0)
    
    glUseProgram(shader_program)
    projection_loc = glGetUniformLocation(shader_program, "projection")
    glUniformMatrix4fv(projection_loc, 1, GL_TRUE, projection)
    
    # Matriz identidade para o modelo (cubo fixo na origem)
    model_matrix = np.eye(4, dtype=np.float32)
    model_loc = glGetUniformLocation(shader_program, "model")
    glUniformMatrix4fv(model_loc, 1, GL_TRUE, model_matrix)
    
    # Obter localização da matriz view
    view_loc = glGetUniformLocation(shader_program, "view")
    
    # Configurar textura
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, texture)
    texture_loc = glGetUniformLocation(shader_program, "ourTexture")
    glUniform1i(texture_loc, 0)
    
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
        
        # Movimento da câmera
        for key in [glfw.KEY_W, glfw.KEY_S, glfw.KEY_A, glfw.KEY_D, glfw.KEY_SPACE, glfw.KEY_LEFT_SHIFT]:
            keys_pressed[key] = glfw.get_key(window, key) == glfw.PRESS
        
        camera.process_keyboard(keys_pressed, delta_time)
        
        # Limpar buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Atualizar matriz de view
        view_matrix = camera.get_view_matrix()
        glUniformMatrix4fv(view_loc, 1, GL_TRUE, view_matrix)
        
        # Desenhar o cubo texturizado
        glBindVertexArray(VAO)
        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)
        
        glfw.swap_buffers(window)
    
    # Limpar recursos
    glDeleteVertexArrays(1, [VAO])
    glDeleteBuffers(1, [VBO])
    glDeleteBuffers(1, [EBO])
    glDeleteTextures(1, [texture])
    glDeleteProgram(shader_program)
    glfw.terminate()

if __name__ == "__main__":
    main()