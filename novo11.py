import glfw
from OpenGL.GL import *
import numpy as np
import sys
import ctypes
import math
from PIL import Image

# Vertex shader para o cubo com iluminação
vertex_shader_cube = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;
layout (location = 2) in vec3 aNormal;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;

out vec2 TexCoord;
out vec3 FragPos;
out vec3 Normal;

void main()
{
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    TexCoord = aTexCoord;
    FragPos = vec3(model * vec4(aPos, 1.0));
    Normal = mat3(transpose(inverse(model))) * aNormal;
}
"""

# Fragment shader para o cubo com iluminação
fragment_shader_cube = """
#version 330 core
in vec2 TexCoord;
in vec3 FragPos;
in vec3 Normal;

out vec4 FragColor;

uniform sampler2D ourTexture;
uniform int useTexture;
uniform int useLighting;

uniform vec3 lightPos1;
uniform vec3 lightPos2;
uniform vec3 lightColor1;
uniform vec3 lightColor2;
uniform vec3 ambientColor;
uniform vec3 viewPos;

void main()
{
    vec4 texColor;
    if (useTexture == 1)
        texColor = texture(ourTexture, TexCoord);
    else
        texColor = vec4(0.8, 0.8, 0.8, 1.0);
    
    if (useLighting == 0) {
        FragColor = texColor;
        return;
    }
    
    vec3 norm = normalize(Normal);
    
    // Componente ambiente
    float ambientStrength = 0.3;
    vec3 ambient = ambientStrength * ambientColor;
    
    // Luz 1
    vec3 lightDir1 = normalize(lightPos1 - FragPos);
    float diff1 = max(dot(norm, lightDir1), 0.0);
    vec3 diffuse1 = diff1 * lightColor1;
    
    // Luz 2
    vec3 lightDir2 = normalize(lightPos2 - FragPos);
    float diff2 = max(dot(norm, lightDir2), 0.0);
    vec3 diffuse2 = diff2 * lightColor2;
    
    // Componente especular
    float specularStrength = 0.5;
    vec3 viewDir = normalize(viewPos - FragPos);
    
    vec3 reflectDir1 = reflect(-lightDir1, norm);
    float spec1 = pow(max(dot(viewDir, reflectDir1), 0.0), 32);
    vec3 specular1 = specularStrength * spec1 * lightColor1;
    
    vec3 reflectDir2 = reflect(-lightDir2, norm);
    float spec2 = pow(max(dot(viewDir, reflectDir2), 0.0), 32);
    vec3 specular2 = specularStrength * spec2 * lightColor2;
    
    vec3 result = (ambient + diffuse1 + diffuse2 + specular1 + specular2) * texColor.rgb;
    
    FragColor = vec4(result, 1.0);
}
"""

# Vertex shader simples para as esferas (luzes)
vertex_shader_sphere = """
#version 330 core
layout (location = 0) in vec3 aPos;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;

void main()
{
    gl_Position = projection * view * model * vec4(aPos, 1.0);
}
"""

# Fragment shader para as esferas (cores sólidas)
fragment_shader_sphere = """
#version 330 core
uniform vec3 sphereColor;
out vec4 FragColor;

void main()
{
    FragColor = vec4(sphereColor, 1.0);
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

def create_shader_program(vertex_source, fragment_source):
    """Cria e linka o programa de shader"""
    vertex_shader = compile_shader(vertex_source, GL_VERTEX_SHADER)
    if not vertex_shader:
        return None
    
    fragment_shader = compile_shader(fragment_source, GL_FRAGMENT_SHADER)
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
    """Carrega uma textura de um arquivo de imagem"""
    try:
        print(f"Carregando textura: {image_path}")
        image = Image.open(image_path)
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
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

def create_texture_checker():
    """Cria uma textura de xadrez"""
    size = 512
    texture_data = np.zeros((size, size, 3), dtype=np.uint8)
    
    square_size = 64
    for i in range(size):
        for j in range(size):
            if ((i // square_size) + (j // square_size)) % 2 == 0:
                texture_data[i, j] = [255, 255, 255]
            else:
                texture_data[i, j] = [100, 100, 100]
    
    texture_data = texture_data[::-1, :, :]
    
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, size, size, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
    glGenerateMipmap(GL_TEXTURE_2D)
    
    return texture

def create_sphere_vertices(radius=0.15, sectors=32, stacks=32):
    """Cria vértices para uma esfera"""
    vertices = []
    indices = []
    
    for i in range(stacks + 1):
        stack_angle = math.pi / 2 - i * math.pi / stacks
        xy = radius * math.cos(stack_angle)
        z = radius * math.sin(stack_angle)
        
        for j in range(sectors + 1):
            sector_angle = j * 2 * math.pi / sectors
            x = xy * math.cos(sector_angle)
            y = xy * math.sin(sector_angle)
            
            vertices.extend([x, y, z])
    
    for i in range(stacks):
        k1 = i * (sectors + 1)
        k2 = (i + 1) * (sectors + 1)
        
        for j in range(sectors):
            if i != 0:
                indices.extend([k1 + j, k1 + j + 1, k2 + j])
            if i != stacks - 1:
                indices.extend([k1 + j + 1, k2 + j + 1, k2 + j])
    
    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)

def create_cube_with_normals():
    """Cria os vértices com normais e coordenadas de textura"""
    vertices = []
    
    # Face frontal (Z = 0.5) - Normal (0,0,1)
    normal = [0, 0, 1]
    vertices.extend([
        -0.5, -0.5,  0.5,  0.0, 0.0,  normal[0], normal[1], normal[2],
         0.5, -0.5,  0.5,  1.0, 0.0,  normal[0], normal[1], normal[2],
         0.5,  0.5,  0.5,  1.0, 1.0,  normal[0], normal[1], normal[2],
        -0.5,  0.5,  0.5,  0.0, 1.0,  normal[0], normal[1], normal[2],
    ])
    
    # Face traseira (Z = -0.5) - Normal (0,0,-1)
    normal = [0, 0, -1]
    vertices.extend([
        -0.5, -0.5, -0.5,  0.0, 0.0,  normal[0], normal[1], normal[2],
         0.5, -0.5, -0.5,  1.0, 0.0,  normal[0], normal[1], normal[2],
         0.5,  0.5, -0.5,  1.0, 1.0,  normal[0], normal[1], normal[2],
        -0.5,  0.5, -0.5,  0.0, 1.0,  normal[0], normal[1], normal[2],
    ])
    
    # Face direita (X = 0.5) - Normal (1,0,0)
    normal = [1, 0, 0]
    vertices.extend([
         0.5, -0.5, -0.5,  0.0, 0.0,  normal[0], normal[1], normal[2],
         0.5,  0.5, -0.5,  1.0, 0.0,  normal[0], normal[1], normal[2],
         0.5,  0.5,  0.5,  1.0, 1.0,  normal[0], normal[1], normal[2],
         0.5, -0.5,  0.5,  0.0, 1.0,  normal[0], normal[1], normal[2],
    ])
    
    # Face esquerda (X = -0.5) - Normal (-1,0,0)
    normal = [-1, 0, 0]
    vertices.extend([
        -0.5, -0.5,  0.5,  0.0, 0.0,  normal[0], normal[1], normal[2],
        -0.5,  0.5,  0.5,  1.0, 0.0,  normal[0], normal[1], normal[2],
        -0.5,  0.5, -0.5,  1.0, 1.0,  normal[0], normal[1], normal[2],
        -0.5, -0.5, -0.5,  0.0, 1.0,  normal[0], normal[1], normal[2],
    ])
    
    # Face superior (Y = 0.5) - Normal (0,1,0)
    normal = [0, 1, 0]
    vertices.extend([
        -0.5,  0.5,  0.5,  0.0, 0.0,  normal[0], normal[1], normal[2],
         0.5,  0.5,  0.5,  1.0, 0.0,  normal[0], normal[1], normal[2],
         0.5,  0.5, -0.5,  1.0, 1.0,  normal[0], normal[1], normal[2],
        -0.5,  0.5, -0.5,  0.0, 1.0,  normal[0], normal[1], normal[2],
    ])
    
    # Face inferior (Y = -0.5) - Normal (0,-1,0)
    normal = [0, -1, 0]
    vertices.extend([
        -0.5, -0.5, -0.5,  0.0, 0.0,  normal[0], normal[1], normal[2],
         0.5, -0.5, -0.5,  1.0, 0.0,  normal[0], normal[1], normal[2],
         0.5, -0.5,  0.5,  1.0, 1.0,  normal[0], normal[1], normal[2],
        -0.5, -0.5,  0.5,  0.0, 1.0,  normal[0], normal[1], normal[2],
    ])
    
    vertices = np.array(vertices, dtype=np.float32)
    
    indices = np.array([
        0, 1, 2,  2, 3, 0,
        4, 5, 6,  6, 7, 4,
        8, 9, 10,  10, 11, 8,
        12, 13, 14,  14, 15, 12,
        16, 17, 18,  18, 19, 16,
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
    
    # Atualizar projeção para ambos os shaders
    aspect_ratio = width / height if height > 0 else 1.0
    projection = get_projection_matrix_perspective(45.0, aspect_ratio, 0.1, 100.0)
    
    global shader_cube, shader_sphere
    if shader_cube:
        glUseProgram(shader_cube)
        projection_loc = glGetUniformLocation(shader_cube, "projection")
        glUniformMatrix4fv(projection_loc, 1, GL_TRUE, projection)
    
    if shader_sphere:
        glUseProgram(shader_sphere)
        projection_loc = glGetUniformLocation(shader_sphere, "projection")
        glUniformMatrix4fv(projection_loc, 1, GL_TRUE, projection)

def key_callback(window, key, scancode, action, mods):
    """Callback para teclado"""
    global render_mode, current_texture, use_texture, use_lighting, shader_cube
    
    if action == glfw.PRESS:
        camera = glfw.get_window_user_pointer(window)
        if camera is None:
            return
        
        if key == glfw.KEY_R:
            camera.reset()
        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        elif key == glfw.KEY_F:
            render_mode = not render_mode
            if render_mode:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                print("Modo: PREENCHIDO")
            else:
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                print("Modo: WIREFRAME")
        elif key == glfw.KEY_T:
            current_texture = (current_texture + 1) % 3
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
                use_texture = False
                print("Textura: DESLIGADA (cor sólida)")
            
            if shader_cube:
                glUseProgram(shader_cube)
                use_texture_loc = glGetUniformLocation(shader_cube, "useTexture")
                glUniform1i(use_texture_loc, 1 if use_texture else 0)
        
        elif key == glfw.KEY_L:
            use_lighting = not use_lighting
            if use_lighting:
                print("Iluminação: LIGADA")
            else:
                print("Iluminação: DESLIGADA")
            
            if shader_cube:
                glUseProgram(shader_cube)
                use_lighting_loc = glGetUniformLocation(shader_cube, "useLighting")
                glUniform1i(use_lighting_loc, 1 if use_lighting else 0)

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
    print("CUBO 3D COM ILUMINAÇÃO - DUAS FONTES DE LUZ")
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
    print("  T        - Alternar textura (Própria imagem / Xadrez / Sem textura)")
    print("  L        - Ligar/Desligar iluminação")
    print("\nFONTES DE LUZ:")
    print("  Luz 1: Vermelha - Posição: (-2.0, 1.5, 2.0)")
    print("  Luz 2: Azul     - Posição: ( 2.0, 1.5, 2.0)")
    print("  Esferas coloridas indicam as posições das luzes!")
    print("\nDICA: Aproxime-se das esferas para ver os pontos de luz!")
    print("="*70 + "\n")

def main():
    # ===== CONFIGURE AQUI O CAMINHO DA SUA IMAGEM =====
    IMAGEM_PATH = "ss.jpg"
    # ==================================================
    
    # Variáveis globais
    global render_mode, current_texture, use_texture, use_lighting, textures
    global shader_cube, shader_sphere
    global first_mouse, last_x, last_y
    
    render_mode = True
    current_texture = 0
    use_texture = True
    use_lighting = True
    
    # Posições das luzes
    light_pos1 = np.array([-2.0, 1.5, 2.0], dtype=np.float32)
    light_pos2 = np.array([2.0, 1.5, 2.0], dtype=np.float32)
    light_color1 = np.array([1.0, 0.2, 0.2], dtype=np.float32)
    light_color2 = np.array([0.2, 0.2, 1.0], dtype=np.float32)
    ambient_color = np.array([0.3, 0.3, 0.3], dtype=np.float32)
    
    # Inicializar GLFW
    if not glfw.init():
        sys.exit("Falha ao inicializar GLFW")
    
    # Configurar a janela
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.DEPTH_BITS, 24)
    
    # Criar janela
    window = glfw.create_window(1024, 768, "Cubo 3D com Iluminação - UNILAB", None, None)
    if not window:
        glfw.terminate()
        sys.exit("Falha ao criar janela")
    
    glfw.make_context_current(window)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    
    # Criar câmera
    camera = Camera(position=np.array([0.0, 0.0, 5.0]), yaw=-90.0, pitch=0.0)
    
    # Criar shader programs
    shader_cube = create_shader_program(vertex_shader_cube, fragment_shader_cube)
    shader_sphere = create_shader_program(vertex_shader_sphere, fragment_shader_sphere)
    
    if not shader_cube or not shader_sphere:
        glfw.terminate()
        sys.exit("Falha ao criar shader programs")
    
    glfw.set_window_user_pointer(window, camera)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_key_callback(window, key_callback)
    glfw.set_cursor_pos_callback(window, mouse_callback)
    
    first_mouse = True
    last_x = 512
    last_y = 384
    
    # Criar dados
    cube_vertices, cube_indices = create_cube_with_normals()
    sphere_vertices, sphere_indices = create_sphere_vertices(radius=0.2, sectors=32, stacks=32)
    
    # Carregar texturas
    textures = []
    tex_user = load_texture_from_file(IMAGEM_PATH)
    if not tex_user:
        tex_user = create_texture_checker()
    textures.append(tex_user)
    textures.append(create_texture_checker())
    
    # Configurar VAO para o cubo
    cube_VAO = glGenVertexArrays(1)
    glBindVertexArray(cube_VAO)
    
    cube_VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, cube_VBO)
    glBufferData(GL_ARRAY_BUFFER, cube_vertices.nbytes, cube_vertices, GL_STATIC_DRAW)
    
    cube_EBO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, cube_EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, cube_indices.nbytes, cube_indices, GL_STATIC_DRAW)
    
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), ctypes.c_void_p(3 * sizeof(GLfloat)))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), ctypes.c_void_p(5 * sizeof(GLfloat)))
    glEnableVertexAttribArray(2)
    
    # Configurar VAO para as esferas
    sphere_VAO = glGenVertexArrays(1)
    glBindVertexArray(sphere_VAO)
    
    sphere_VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, sphere_VBO)
    glBufferData(GL_ARRAY_BUFFER, sphere_vertices.nbytes, sphere_vertices, GL_STATIC_DRAW)
    
    sphere_EBO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, sphere_EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, sphere_indices.nbytes, sphere_indices, GL_STATIC_DRAW)
    
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    
    glBindVertexArray(0)
    
    # Configurações de renderização
    glClearColor(0.05, 0.05, 0.05, 1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    
    # Configurar projeção
    width, height = glfw.get_framebuffer_size(window)
    aspect_ratio = width / height if height > 0 else 1.0
    projection = get_projection_matrix_perspective(45.0, aspect_ratio, 0.1, 100.0)
    
    # Configurar shader do cubo
    glUseProgram(shader_cube)
    glUniformMatrix4fv(glGetUniformLocation(shader_cube, "projection"), 1, GL_TRUE, projection)
    glUniform3fv(glGetUniformLocation(shader_cube, "lightPos1"), 1, light_pos1)
    glUniform3fv(glGetUniformLocation(shader_cube, "lightPos2"), 1, light_pos2)
    glUniform3fv(glGetUniformLocation(shader_cube, "lightColor1"), 1, light_color1)
    glUniform3fv(glGetUniformLocation(shader_cube, "lightColor2"), 1, light_color2)
    glUniform3fv(glGetUniformLocation(shader_cube, "ambientColor"), 1, ambient_color)
    glUniform1i(glGetUniformLocation(shader_cube, "useTexture"), 1)
    glUniform1i(glGetUniformLocation(shader_cube, "useLighting"), 1)
    
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, textures[0])
    glUniform1i(glGetUniformLocation(shader_cube, "ourTexture"), 0)
    
    # Configurar shader das esferas
    glUseProgram(shader_sphere)
    glUniformMatrix4fv(glGetUniformLocation(shader_sphere, "projection"), 1, GL_TRUE, projection)
    
    print_controls()
    
    last_time = glfw.get_time()
    keys_pressed = {}
    
    # Matrizes para as esferas
    sphere_model1 = np.eye(4, dtype=np.float32)
    sphere_model1[0:3, 3] = light_pos1
    
    sphere_model2 = np.eye(4, dtype=np.float32)
    sphere_model2[0:3, 3] = light_pos2
    
    # Loop principal
    while not glfw.window_should_close(window):
        current_time = glfw.get_time()
        delta_time = current_time - last_time
        last_time = current_time
        
        glfw.poll_events()
        
        for key in [glfw.KEY_W, glfw.KEY_S, glfw.KEY_A, glfw.KEY_D, glfw.KEY_SPACE, glfw.KEY_LEFT_SHIFT]:
            keys_pressed[key] = glfw.get_key(window, key) == glfw.PRESS
        
        camera.process_keyboard(keys_pressed, delta_time)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        view_matrix = camera.get_view_matrix()
        
        # Desenhar cubo
        glUseProgram(shader_cube)
        glUniformMatrix4fv(glGetUniformLocation(shader_cube, "view"), 1, GL_TRUE, view_matrix)
        glUniform3fv(glGetUniformLocation(shader_cube, "viewPos"), 1, camera.position)
        
        model_matrix = np.eye(4, dtype=np.float32)
        glUniformMatrix4fv(glGetUniformLocation(shader_cube, "model"), 1, GL_TRUE, model_matrix)
        
        glBindVertexArray(cube_VAO)
        glDrawElements(GL_TRIANGLES, len(cube_indices), GL_UNSIGNED_INT, None)
        
        # Desenhar esfera da luz 1 (Vermelha)
        glUseProgram(shader_sphere)
        glUniformMatrix4fv(glGetUniformLocation(shader_sphere, "view"), 1, GL_TRUE, view_matrix)
        glUniformMatrix4fv(glGetUniformLocation(shader_sphere, "model"), 1, GL_TRUE, sphere_model1)
        glUniform3f(glGetUniformLocation(shader_sphere, "sphereColor"), 1.0, 0.2, 0.2)
        
        glBindVertexArray(sphere_VAO)
        glDrawElements(GL_TRIANGLES, len(sphere_indices), GL_UNSIGNED_INT, None)
        
        # Desenhar esfera da luz 2 (Azul)
        glUniformMatrix4fv(glGetUniformLocation(shader_sphere, "model"), 1, GL_TRUE, sphere_model2)
        glUniform3f(glGetUniformLocation(shader_sphere, "sphereColor"), 0.2, 0.2, 1.0)
        glDrawElements(GL_TRIANGLES, len(sphere_indices), GL_UNSIGNED_INT, None)
        
        glfw.swap_buffers(window)
    
    # Limpar recursos
    glDeleteVertexArrays(1, [cube_VAO])
    glDeleteBuffers(1, [cube_VBO])
    glDeleteBuffers(1, [cube_EBO])
    glDeleteVertexArrays(1, [sphere_VAO])
    glDeleteBuffers(1, [sphere_VBO])
    glDeleteBuffers(1, [sphere_EBO])
    for tex in textures:
        glDeleteTextures(1, [tex])
    glDeleteProgram(shader_cube)
    glDeleteProgram(shader_sphere)
    glfw.terminate()

if __name__ == "__main__":
    main()