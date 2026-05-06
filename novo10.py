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
uniform int useTexture;

void main()
{
    if (useTexture == 1)
        FragColor = texture(ourTexture, TexCoord);
    else
        FragColor = vec4(0.8, 0.8, 0.8, 1.0);  // Cor cinza quando sem textura
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

def load_texture_from_file(image_path):
    """
    Carrega uma textura de um arquivo de imagem.
    """
    try:
        print(f"Carregando textura: {image_path}")
        image = Image.open(image_path)
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Inverter verticalmente
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        
        img_data = np.array(image, dtype=np.uint8)
        
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 
                     0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
        
        glGenerateMipmap(GL_TEXTURE_2D)
        
        print(f"Textura carregada com sucesso! Dimensões: {image.width}x{image.height}")
        return texture
        
    except FileNotFoundError:
        print(f"ERRO: Arquivo não encontrado: {image_path}")
        return None
    except Exception as e:
        print(f"ERRO ao carregar textura: {e}")
        return None

def create_texture_2():
    """Cria uma segunda textura (padrão xadrez)"""
    size = 512
    texture_data = np.zeros((size, size, 3), dtype=np.uint8)
    
    # Criar padrão xadrez colorido
    square_size = 64
    for i in range(size):
        for j in range(size):
            if ((i // square_size) + (j // square_size)) % 2 == 0:
                texture_data[i, j] = [255, 100, 100]  # Vermelho claro
            else:
                texture_data[i, j] = [100, 100, 255]  # Azul claro
    
    # Adicionar linhas de grade
    for i in range(0, size, square_size):
        if i > 0:
            texture_data[i:i+4, :] = [255, 255, 255]
            texture_data[:, i:i+4] = [255, 255, 255]
    
    # Inverter verticalmente
    texture_data = texture_data[::-1, :, :]
    
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, size, size, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
    glGenerateMipmap(GL_TEXTURE_2D)
    
    print("Textura 2 (xadrez) criada com sucesso!")
    return texture

def create_texture_3():
    """Cria uma terceira textura (gradiente radial)"""
    size = 512
    texture_data = np.zeros((size, size, 3), dtype=np.uint8)
    
    center_x, center_y = size // 2, size // 2
    max_dist = math.sqrt(center_x**2 + center_y**2)
    
    for i in range(size):
        for j in range(size):
            dist = math.sqrt((i - center_x)**2 + (j - center_y)**2)
            intensity = int((dist / max_dist) * 255)
            
            # Gradiente radial colorido
            texture_data[i, j] = [intensity, 255 - intensity, (intensity + 128) % 256]
    
    # Inverter verticalmente
    texture_data = texture_data[::-1, :, :]
    
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, size, size, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
    glGenerateMipmap(GL_TEXTURE_2D)
    
    print("Textura 3 (gradiente) criada com sucesso!")
    return texture

def create_cube_with_texture_corrected():
    """
    Cria os vértices com coordenadas de textura corrigidas para todas as faces do cubo.
    """
    vertices = []
    
    # Face frontal (Z = 0.5)
    vertices.extend([
        -0.5, -0.5,  0.5,  0.0, 0.0,
         0.5, -0.5,  0.5,  1.0, 0.0,
         0.5,  0.5,  0.5,  1.0, 1.0,
        -0.5,  0.5,  0.5,  0.0, 1.0,
    ])
    
    # Face traseira (Z = -0.5)
    vertices.extend([
        -0.5, -0.5, -0.5,  0.0, 0.0,
         0.5, -0.5, -0.5,  1.0, 0.0,
         0.5,  0.5, -0.5,  1.0, 1.0,
        -0.5,  0.5, -0.5,  0.0, 1.0,
    ])
    
    # Face direita (X = 0.5)
    vertices.extend([
         0.5, -0.5, -0.5,  0.0, 0.0,
         0.5,  0.5, -0.5,  1.0, 0.0,
         0.5,  0.5,  0.5,  1.0, 1.0,
         0.5, -0.5,  0.5,  0.0, 1.0,
    ])
    
    # Face esquerda (X = -0.5)
    vertices.extend([
        -0.5, -0.5,  0.5,  0.0, 0.0,
        -0.5,  0.5,  0.5,  1.0, 0.0,
        -0.5,  0.5, -0.5,  1.0, 1.0,
        -0.5, -0.5, -0.5,  0.0, 1.0,
    ])
    
    # Face superior (Y = 0.5)
    vertices.extend([
        -0.5,  0.5,  0.5,  0.0, 0.0,
         0.5,  0.5,  0.5,  1.0, 0.0,
         0.5,  0.5, -0.5,  1.0, 1.0,
        -0.5,  0.5, -0.5,  0.0, 1.0,
    ])
    
    # Face inferior (Y = -0.5)
    vertices.extend([
        -0.5, -0.5, -0.5,  0.0, 0.0,
         0.5, -0.5, -0.5,  1.0, 0.0,
         0.5, -0.5,  0.5,  1.0, 1.0,
        -0.5, -0.5,  0.5,  0.0, 1.0,
    ])
    
    vertices = np.array(vertices, dtype=np.float32)
    
    indices = np.array([
        # Face frontal
        0, 1, 2,  2, 3, 0,
        # Face traseira
        4, 5, 6,  6, 7, 4,
        # Face direita
        8, 9, 10,  10, 11, 8,
        # Face esquerda
        12, 13, 14,  14, 15, 12,
        # Face superior
        16, 17, 18,  18, 19, 16,
        # Face inferior
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
    global render_mode, current_texture, use_texture
    
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
        
        # Alternar modo wireframe (F)
        elif key == glfw.KEY_F:
            render_mode = not render_mode
            if render_mode:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                print("Modo: PREENCHIDO")
            else:
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                print("Modo: WIREFRAME")
        
        # Alternar textura (T)
        elif key == glfw.KEY_T:
            current_texture = (current_texture + 1) % 4
            if current_texture == 0:
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, textures[0])
                use_texture = True
                print("Textura: PRÓPRIA IMAGEM")
            elif current_texture == 1:
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, textures[1])
                use_texture = True
                print("Textura: XADREZ")
            elif current_texture == 2:
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, textures[2])
                use_texture = True
                print("Textura: GRADIENTE")
            elif current_texture == 3:
                use_texture = False
                print("Textura: DESLIGADA (cor sólida)")
        
        # Atualizar uniforme no shader
        if shader_program:
            glUseProgram(shader_program)
            use_texture_loc = glGetUniformLocation(shader_program, "useTexture")
            glUniform1i(use_texture_loc, 1 if use_texture else 0)

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
    print("\n" + "="*70)
    print("CÂMERA EM PRIMEIRA PESSOA - CUBO COM MÚLTIPLAS TEXTURAS")
    print("="*70)
    print("\nMOVIMENTAÇÃO DA CÂMERA:")
    print("  Mouse + botão esquerdo - Olhar ao redor")
    print("  W/A/S/D - Movimentar no plano XZ")
    print("  ESPAÇO   - Subir")
    print("  SHIFT    - Descer")
    print("  R        - Resetar posição da câmera")
    print("  ESC      - Sair")
    print("\nVISUALIZAÇÃO:")
    print("  F        - Alternar entre modo PREENCHIDO e WIREFRAME")
    print("  T        - Alternar entre as texturas:")
    print("             1ª vez: Própria imagem")
    print("             2ª vez: Padrão xadrez")
    print("             3ª vez: Gradiente radial")
    print("             4ª vez: Sem textura (cor sólida)")
    print("\nDICA: Use o modo wireframe (F) para ver os triângulos que compõem o cubo!")
    print("="*70 + "\n")

def main():
    # ===== CONFIGURE AQUI O CAMINHO DA SUA IMAGEM =====
    IMAGEM_PATH = "ss.jpg"  # <--- COLOQUE O CAMINHO DA SUA IMAGEM AQUI
    # ==================================================
    
    # Variáveis globais
    global render_mode, current_texture, use_texture, textures, shader_program
    global first_mouse, last_x, last_y
    
    render_mode = True  # True = preenchido, False = wireframe
    current_texture = 0
    use_texture = True
    
    # Inicializar GLFW
    if not glfw.init():
        sys.exit("Falha ao inicializar GLFW")
    
    # Configurar a janela
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.DEPTH_BITS, 24)
    
    # Criar janela
    window = glfw.create_window(800, 600, "Cubo com Múltiplas Texturas - Câmera em Primeira Pessoa", None, None)
    if not window:
        glfw.terminate()
        sys.exit("Falha ao criar janela")
    
    glfw.make_context_current(window)
    
    # Desabilitar cursor
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
    
    # Variáveis para mouse
    first_mouse = True
    last_x = 400
    last_y = 300
    
    # Criar dados do cubo
    vertices, indices = create_cube_with_texture_corrected()
    
    # Carregar texturas
    textures = []
    
    # Textura 1: Imagem do usuário
    tex1 = load_texture_from_file(IMAGEM_PATH)
    if not tex1:
        print("Imagem não encontrada, usando textura padrão...")
        tex1 = create_texture_2()
    textures.append(tex1)
    
    # Textura 2: Padrão xadrez
    textures.append(create_texture_2())
    
    # Textura 3: Gradiente radial
    textures.append(create_texture_3())
    
    # Criar VAO, VBO, EBO
    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)
    
    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    
    EBO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
    
    # Configurar atributos
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), ctypes.c_void_p(3 * sizeof(GLfloat)))
    glEnableVertexAttribArray(1)
    
    glBindVertexArray(0)
    
    # Configurações de renderização
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    
    # Configurar projeção
    width, height = glfw.get_framebuffer_size(window)
    aspect_ratio = width / height if height > 0 else 1.0
    projection = get_projection_matrix_perspective(45.0, aspect_ratio, 0.1, 100.0)
    
    glUseProgram(shader_program)
    projection_loc = glGetUniformLocation(shader_program, "projection")
    glUniformMatrix4fv(projection_loc, 1, GL_TRUE, projection)
    
    model_matrix = np.eye(4, dtype=np.float32)
    model_loc = glGetUniformLocation(shader_program, "model")
    glUniformMatrix4fv(model_loc, 1, GL_TRUE, model_matrix)
    
    view_loc = glGetUniformLocation(shader_program, "view")
    
    # Configurar textura inicial
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, textures[0])
    texture_loc = glGetUniformLocation(shader_program, "ourTexture")
    glUniform1i(texture_loc, 0)
    
    # Configurar uniforme de uso de textura
    use_texture_loc = glGetUniformLocation(shader_program, "useTexture")
    glUniform1i(use_texture_loc, 1)
    
    # Imprimir controles
    print_controls()
    
    # Timer
    last_time = glfw.get_time()
    keys_pressed = {}
    
    # Loop principal
    while not glfw.window_should_close(window):
        current_time = glfw.get_time()
        delta_time = current_time - last_time
        last_time = current_time
        
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
        
        # Desenhar o cubo
        glBindVertexArray(VAO)
        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)
        
        glfw.swap_buffers(window)
    
    # Limpar recursos
    glDeleteVertexArrays(1, [VAO])
    glDeleteBuffers(1, [VBO])
    glDeleteBuffers(1, [EBO])
    for tex in textures:
        glDeleteTextures(1, [tex])
    glDeleteProgram(shader_program)
    glfw.terminate()

if __name__ == "__main__":
    main()