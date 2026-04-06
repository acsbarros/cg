import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import sys
import math

# ==================== VERTEX SHADER PARA OBJETOS ====================
VERTEX_SHADER_SOURCE = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec3 aColor;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 FragPos;
out vec3 Normal;
out vec3 Color;

void main() {
    FragPos = vec3(model * vec4(aPos, 1.0));
    Normal = mat3(transpose(inverse(model))) * aNormal;
    Color = aColor;
    gl_Position = projection * view * vec4(FragPos, 1.0);
}
"""

# ==================== FRAGMENT SHADER PARA OBJETOS ====================
FRAGMENT_SHADER_SOURCE = """
#version 330 core
in vec3 FragPos;
in vec3 Normal;
in vec3 Color;

out vec4 FragColor;

struct Light {
    vec3 position;
    vec3 color;
    float intensity;
    float ambientStrength;
    float specularStrength;
};

struct Material {
    float shininess;
    float reflectivity;
};

uniform Light light1;
uniform Light light2;
uniform Light light3;
uniform Material material;
uniform vec3 viewPos;
uniform float time;

void main() {
    vec3 norm = normalize(Normal);
    vec3 result = vec3(0.0);
    
    // Luz 1
    vec3 lightDir1 = normalize(light1.position - FragPos);
    float diff1 = max(dot(norm, lightDir1), 0.0);
    vec3 diffuse1 = light1.color * diff1 * light1.intensity;
    vec3 ambient1 = light1.color * light1.ambientStrength;
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir1 = reflect(-lightDir1, norm);
    float spec1 = pow(max(dot(viewDir, reflectDir1), 0.0), material.shininess);
    vec3 specular1 = light1.color * spec1 * light1.specularStrength * light1.intensity;
    result += (ambient1 + diffuse1 + specular1) * Color;
    
    // Luz 2
    vec3 lightDir2 = normalize(light2.position - FragPos);
    float diff2 = max(dot(norm, lightDir2), 0.0);
    vec3 diffuse2 = light2.color * diff2 * light2.intensity;
    vec3 ambient2 = light2.color * light2.ambientStrength;
    vec3 reflectDir2 = reflect(-lightDir2, norm);
    float spec2 = pow(max(dot(viewDir, reflectDir2), 0.0), material.shininess);
    vec3 specular2 = light2.color * spec2 * light2.specularStrength * light2.intensity;
    result += (ambient2 + diffuse2 + specular2) * Color;
    
    // Luz 3
    vec3 lightDir3 = normalize(light3.position - FragPos);
    float diff3 = max(dot(norm, lightDir3), 0.0);
    vec3 diffuse3 = light3.color * diff3 * light3.intensity;
    vec3 ambient3 = light3.color * light3.ambientStrength;
    vec3 reflectDir3 = reflect(-lightDir3, norm);
    float spec3 = pow(max(dot(viewDir, reflectDir3), 0.0), material.shininess);
    vec3 specular3 = light3.color * spec3 * light3.specularStrength * light3.intensity;
    result += (ambient3 + diffuse3 + specular3) * Color;
    
    float pulse = sin(time * 3.0) * 0.2 + 0.8;
    result *= pulse;
    
    FragColor = vec4(result, 1.0);
}
"""

# ==================== VERTEX SHADER SIMPLES PARA LUZES ====================
LIGHT_VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec3 aPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec3 lightColor;

out vec3 Color;

void main() {
    Color = lightColor;
    gl_Position = projection * view * model * vec4(aPos, 1.0);
}
"""

# ==================== FRAGMENT SHADER SIMPLES PARA LUZES ====================
LIGHT_FRAGMENT_SHADER = """
#version 330 core
in vec3 Color;
out vec4 FragColor;

void main() {
    FragColor = vec4(Color, 0.9);
}
"""

# ==================== DADOS DO CUBO ====================
def create_cube_data():
    """Cria os dados do cubo: vértices, normais e cores"""
    
    vertices = np.array([
        [-0.5, -0.5, -0.5], [ 0.5, -0.5, -0.5], [ 0.5,  0.5, -0.5], [-0.5,  0.5, -0.5],
        [-0.5, -0.5,  0.5], [ 0.5, -0.5,  0.5], [ 0.5,  0.5,  0.5], [-0.5,  0.5,  0.5]
    ], dtype=np.float32)
    
    indices = np.array([
        4, 5, 6,  6, 7, 4,  # Frente
        0, 1, 2,  2, 3, 0,  # Trás
        1, 5, 6,  6, 2, 1,  # Direita
        0, 4, 7,  7, 3, 0,  # Esquerda
        3, 2, 6,  6, 7, 3,  # Topo
        0, 1, 5,  5, 4, 0   # Base
    ], dtype=np.uint32)
    
    face_normals = {
        'front': [0, 0, 1], 'back': [0, 0, -1], 'right': [1, 0, 0],
        'left': [-1, 0, 0], 'top': [0, 1, 0], 'bottom': [0, -1, 0]
    }
    
    face_colors = {
        'front': [1, 0, 0], 'back': [0, 1, 0], 'right': [0, 0, 1],
        'left': [1, 1, 0], 'top': [1, 0, 1], 'bottom': [0, 1, 1]
    }
    
    face_names = ['front', 'front', 'back', 'back', 'right', 'right', 
                  'left', 'left', 'top', 'top', 'bottom', 'bottom']
    
    expanded_vertices, expanded_normals, expanded_colors = [], [], []
    
    for i, idx in enumerate(indices):
        expanded_vertices.append(vertices[idx])
        face_idx = i // 6
        face_name = face_names[face_idx]
        expanded_normals.append(face_normals[face_name])
        expanded_colors.append(face_colors[face_name])
    
    return np.array(expanded_vertices, dtype=np.float32), \
           np.array(expanded_normals, dtype=np.float32), \
           np.array(expanded_colors, dtype=np.float32), \
           len(expanded_vertices)

# ==================== DADOS DA ESFERA (ICOSFERA) ====================
def create_sphere_data(radius=0.2):
    """Cria uma esfera usando um icosaedro subdividido"""
    # Icosaedro base (12 vértices, 20 faces)
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    
    vertices_base = np.array([
        [-1,  phi, 0], [ 1,  phi, 0], [-1, -phi, 0], [ 1, -phi, 0],
        [0, -1,  phi], [0,  1,  phi], [0, -1, -phi], [0,  1, -phi],
        [ phi, 0, -1], [ phi, 0,  1], [-phi, 0, -1], [-phi, 0,  1]
    ], dtype=np.float32)
    
    # Normalizar para esfera unitária
    for i in range(len(vertices_base)):
        norm = np.linalg.norm(vertices_base[i])
        vertices_base[i] = vertices_base[i] / norm
    
    faces = np.array([
        [0, 1, 4], [0, 4, 9], [9, 4, 5], [4, 8, 5], [4, 1, 8],
        [1, 10, 8], [10, 3, 8], [8, 3, 5], [3, 2, 5], [3, 7, 2],
        [3, 10, 7], [10, 6, 7], [6, 11, 7], [6, 0, 11], [6, 1, 0],
        [10, 1, 6], [11, 9, 7], [7, 9, 5], [2, 11, 0], [2, 0, 9]
    ], dtype=np.uint32)
    
    # Subdividir uma vez para mais detalhes
    vertices = vertices_base.copy()
    
    for _ in range(2):  # 2 subdivisões para uma esfera suave
        new_vertices = []
        vertex_map = {}
        new_faces = []
        
        for face in faces:
            mid_points = []
            for i in range(3):
                v1 = vertices[face[i]]
                v2 = vertices[face[(i+1)%3]]
                mid = (v1 + v2) / 2.0
                mid = mid / np.linalg.norm(mid)
                key = tuple(sorted([face[i], face[(i+1)%3]]))
                if key not in vertex_map:
                    idx = len(vertices) + len(new_vertices)
                    vertex_map[key] = idx
                    new_vertices.append(mid)
                mid_points.append(vertex_map[key])
            
            new_faces.append([face[0], mid_points[0], mid_points[2]])
            new_faces.append([face[1], mid_points[1], mid_points[0]])
            new_faces.append([face[2], mid_points[2], mid_points[1]])
            new_faces.append([mid_points[0], mid_points[1], mid_points[2]])
        
        vertices = np.vstack([vertices, new_vertices])
        faces = np.array(new_faces, dtype=np.uint32)
    
    # Gerar vértices finais (expandir índices para triângulos)
    final_vertices = []
    for face in faces:
        for idx in face:
            v = vertices[idx] * radius
            final_vertices.append(v)
    
    return np.array(final_vertices, dtype=np.float32), len(final_vertices)

# ==================== CLASSE PRINCIPAL ====================
class OpenGLApp:
    def __init__(self, width=1024, height=768, title="OpenGL com Iluminação - Visualização das Luzes"):
        self.width = width
        self.height = height
        self.title = title
        
        # Variáveis de controle
        self.rotation_angle = 0
        self.camera_distance = 4.0
        self.camera_angle_x = 0.5
        self.camera_angle_y = 0.3
        
        # Tempo para animações
        self.time = 0
        self.last_time = 0
        
        # Inicializar GLFW
        print("🔄 Inicializando GLFW...")
        if not glfw.init():
            print("❌ Falha ao inicializar GLFW")
            sys.exit(1)
        print("✅ GLFW inicializado com sucesso!")
        
        # Configurar versão do OpenGL
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
        
        # Criar janela
        print(f"🪟 Criando janela {width}x{height}...")
        self.window = glfw.create_window(width, height, title, None, None)
        if not self.window:
            print("❌ Falha ao criar janela")
            glfw.terminate()
            sys.exit(1)
        print("✅ Janela criada com sucesso!")
        
        glfw.make_context_current(self.window)
        
        # Configurar callbacks
        glfw.set_key_callback(self.window, self.key_callback)
        glfw.set_framebuffer_size_callback(self.window, self.framebuffer_size_callback)
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        glfw.set_cursor_pos_callback(self.window, self.mouse_callback)
        
        # Verificar versão do OpenGL
        print(f"🎨 OpenGL Version: {glGetString(GL_VERSION).decode()}")
        print(f"🖥️  GPU: {glGetString(GL_RENDERER).decode()}")
        
        # Habilitar depth testing e blending
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Criar shader programs
        print("🔧 Compilando shaders...")
        self.shader_program = self.create_shader_program(VERTEX_SHADER_SOURCE, FRAGMENT_SHADER_SOURCE)
        self.light_shader_program = self.create_shader_program(LIGHT_VERTEX_SHADER, LIGHT_FRAGMENT_SHADER)
        print("✅ Shaders compilados com sucesso!")
        
        # Criar dados do cubo
        print("📦 Gerando dados do cubo...")
        self.vertices, self.normals, self.colors, self.vertex_count = create_cube_data()
        print(f"✅ {self.vertex_count} vértices gerados")
        
        # Criar dados das esferas (luzes)
        print("🔆 Gerando esferas para visualização das luzes...")
        self.sphere_vertices, self.sphere_vertex_count = create_sphere_data(radius=0.15)
        print(f"✅ Esfera com {self.sphere_vertex_count} vértices")
        
        # Configurar buffers
        self.setup_buffers()
        
        # Inicializar tempo
        self.last_time = glfw.get_time()
        
        # Posição inicial do mouse
        self.last_mouse_x = width // 2
        self.last_mouse_y = height // 2
        self.first_mouse = True
        
        print("=" * 60)
        print("✅ Aplicação inicializada com sucesso!")
        print("=" * 60)
        
    def create_shader_program(self, vertex_source, fragment_source):
        """Cria e compila o programa de shaders"""
        try:
            vertex_shader = compileShader(vertex_source, GL_VERTEX_SHADER)
            fragment_shader = compileShader(fragment_source, GL_FRAGMENT_SHADER)
            program = compileProgram(vertex_shader, fragment_shader)
            glDeleteShader(vertex_shader)
            glDeleteShader(fragment_shader)
            return program
        except Exception as e:
            print(f"❌ Erro ao compilar shaders: {e}")
            sys.exit(1)
    
    def setup_buffers(self):
        """Configura os buffers OpenGL"""
        # VAO para o cubo
        self.VAO_cube = glGenVertexArrays(1)
        glBindVertexArray(self.VAO_cube)
        
        # Buffer de vértices do cubo
        self.VBO_cube_vertices = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO_cube_vertices)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), None)
        glEnableVertexAttribArray(0)
        
        # Buffer de normais do cubo
        self.VBO_cube_normals = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO_cube_normals)
        glBufferData(GL_ARRAY_BUFFER, self.normals.nbytes, self.normals, GL_STATIC_DRAW)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), None)
        glEnableVertexAttribArray(1)
        
        # Buffer de cores do cubo
        self.VBO_cube_colors = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO_cube_colors)
        glBufferData(GL_ARRAY_BUFFER, self.colors.nbytes, self.colors, GL_STATIC_DRAW)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), None)
        glEnableVertexAttribArray(2)
        
        glBindVertexArray(0)
        
        # VAO para as esferas (apenas vértices)
        self.VAO_sphere = glGenVertexArrays(1)
        glBindVertexArray(self.VAO_sphere)
        
        self.VBO_sphere_vertices = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO_sphere_vertices)
        glBufferData(GL_ARRAY_BUFFER, self.sphere_vertices.nbytes, self.sphere_vertices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), None)
        glEnableVertexAttribArray(0)
        
        glBindVertexArray(0)
    
    def key_callback(self, window, key, scancode, action, mods):
        """Callback para teclado"""
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, True)
        
        if key == glfw.KEY_W and action == glfw.PRESS:
            self.camera_distance = max(1.0, self.camera_distance - 0.5)
            print(f"📷 Câmera distância: {self.camera_distance:.2f}")
        if key == glfw.KEY_S and action == glfw.PRESS:
            self.camera_distance = min(8.0, self.camera_distance + 0.5)
            print(f"📷 Câmera distância: {self.camera_distance:.2f}")
        
        if key == glfw.KEY_R and action == glfw.PRESS:
            self.camera_distance = 4.0
            self.camera_angle_x = 0.5
            self.camera_angle_y = 0.3
            print("🔄 Câmera resetada!")
    
    def mouse_callback(self, window, xpos, ypos):
        """Callback para movimento do mouse"""
        if self.first_mouse:
            self.last_mouse_x = xpos
            self.last_mouse_y = ypos
            self.first_mouse = False
        
        xoffset = xpos - self.last_mouse_x
        yoffset = self.last_mouse_y - ypos
        
        self.last_mouse_x = xpos
        self.last_mouse_y = ypos
        
        sensitivity = 0.005
        self.camera_angle_x += xoffset * sensitivity
        self.camera_angle_y += yoffset * sensitivity
        self.camera_angle_y = max(-1.5, min(1.5, self.camera_angle_y))
    
    def framebuffer_size_callback(self, window, width, height):
        """Callback para redimensionamento da janela"""
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)
    
    def update_matrices(self):
        """Atualiza as matrizes de transformação"""
        # Matriz de modelo (rotação do objeto)
        model = np.identity(4, dtype=np.float32)
        angle_y = self.rotation_angle
        cos_y = math.cos(angle_y)
        sin_y = math.sin(angle_y)
        rotation_y = np.array([
            [cos_y, 0, sin_y, 0], [0, 1, 0, 0],
            [-sin_y, 0, cos_y, 0], [0, 0, 0, 1]
        ], dtype=np.float32)
        
        angle_x = self.rotation_angle * 0.5
        cos_x = math.cos(angle_x)
        sin_x = math.sin(angle_x)
        rotation_x = np.array([
            [1, 0, 0, 0], [0, cos_x, -sin_x, 0],
            [0, sin_x, cos_x, 0], [0, 0, 0, 1]
        ], dtype=np.float32)
        
        model = rotation_y @ rotation_x
        
        # Matriz de visão (câmera)
        camera_x = self.camera_distance * math.cos(self.camera_angle_x) * math.cos(self.camera_angle_y)
        camera_y = self.camera_distance * math.sin(self.camera_angle_y)
        camera_z = self.camera_distance * math.sin(self.camera_angle_x) * math.cos(self.camera_angle_y)
        camera_pos = np.array([camera_x, camera_y, camera_z], dtype=np.float32)
        camera_target = np.array([0, 0, 0], dtype=np.float32)
        camera_up = np.array([0, 1, 0], dtype=np.float32)
        
        forward = camera_target - camera_pos
        forward = forward / np.linalg.norm(forward)
        right = np.cross(forward, camera_up)
        right = right / np.linalg.norm(right)
        up = np.cross(right, forward)
        
        view = np.identity(4, dtype=np.float32)
        view[0, 0] = right[0]
        view[0, 1] = right[1]
        view[0, 2] = right[2]
        view[1, 0] = up[0]
        view[1, 1] = up[1]
        view[1, 2] = up[2]
        view[2, 0] = -forward[0]
        view[2, 1] = -forward[1]
        view[2, 2] = -forward[2]
        view[3, 0] = -np.dot(right, camera_pos)
        view[3, 1] = -np.dot(up, camera_pos)
        view[3, 2] = np.dot(forward, camera_pos)
        
        # Matriz de projeção
        aspect = self.width / self.height
        fov = 45.0 * math.pi / 180.0
        near = 0.1
        far = 100.0
        
        projection = np.identity(4, dtype=np.float32)
        tan_half_fov = math.tan(fov / 2)
        projection[0, 0] = 1 / (aspect * tan_half_fov)
        projection[1, 1] = 1 / tan_half_fov
        projection[2, 2] = -(far + near) / (far - near)
        projection[2, 3] = -(2 * far * near) / (far - near)
        projection[3, 2] = -1
        
        return model, view, projection, camera_pos
    
    def update_lights(self):
        """Atualiza as posições e propriedades das luzes"""
        current_time = glfw.get_time()
        delta_time = current_time - self.last_time
        self.last_time = current_time
        self.time += delta_time if delta_time < 0.1 else 0.016
        
        # Luz 1: Fixa (Branca)
        light1_pos = np.array([2.0, 3.0, 2.0], dtype=np.float32)
        light1_color = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        light1_intensity = 1.0
        light1_ambient = 0.2
        light1_specular = 0.5
        
        # Luz 2: Rotativa (Vermelha)
        radius = 2.5
        angle = self.time * 1.5
        light2_pos = np.array([
            radius * math.cos(angle),
            1.5 + math.sin(angle * 2) * 0.5,
            radius * math.sin(angle)
        ], dtype=np.float32)
        light2_color = np.array([1.0, 0.3, 0.3], dtype=np.float32)
        light2_intensity = 0.8
        light2_ambient = 0.1
        light2_specular = 0.4
        
        # Luz 3: Pulsante e móvel (Azul)
        light3_pos = np.array([
            -2.0,
            1.0 + math.sin(self.time * 1.5) * 1.0,
            -1.5
        ], dtype=np.float32)
        pulse = abs(math.sin(self.time * 2.0))
        light3_color = np.array([0.3, 0.5, 1.0], dtype=np.float32) * (0.5 + pulse * 0.5)
        light3_intensity = 0.6 + pulse * 0.4
        light3_ambient = 0.15
        light3_specular = 0.6
        
        return (light1_pos, light1_color, light1_intensity, light1_ambient, light1_specular,
                light2_pos, light2_color, light2_intensity, light2_ambient, light2_specular,
                light3_pos, light3_color, light3_intensity, light3_ambient, light3_specular,
                pulse)
    
    def draw_light_sphere(self, position, color, view, projection):
        """Desenha uma esfera representando uma fonte de luz"""
        model = np.identity(4, dtype=np.float32)
        model[0, 3] = position[0]
        model[1, 3] = position[1]
        model[2, 3] = position[2]
        
        glUseProgram(self.light_shader_program)
        
        model_loc = glGetUniformLocation(self.light_shader_program, "model")
        view_loc = glGetUniformLocation(self.light_shader_program, "view")
        proj_loc = glGetUniformLocation(self.light_shader_program, "projection")
        color_loc = glGetUniformLocation(self.light_shader_program, "lightColor")
        
        glUniformMatrix4fv(model_loc, 1, GL_TRUE, model)
        glUniformMatrix4fv(view_loc, 1, GL_TRUE, view)
        glUniformMatrix4fv(proj_loc, 1, GL_TRUE, projection)
        glUniform3fv(color_loc, 1, color)
        
        glBindVertexArray(self.VAO_sphere)
        glDrawArrays(GL_TRIANGLES, 0, self.sphere_vertex_count)
        glBindVertexArray(0)
    
    def render(self):
        """Renderiza a cena"""
        glClearColor(0.05, 0.05, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Atualizar matrizes
        model, view, projection, camera_pos = self.update_matrices()
        
        # ========== DESENHAR CUBO COM ILUMINAÇÃO ==========
        glUseProgram(self.shader_program)
        
        model_loc = glGetUniformLocation(self.shader_program, "model")
        view_loc = glGetUniformLocation(self.shader_program, "view")
        proj_loc = glGetUniformLocation(self.shader_program, "projection")
        
        glUniformMatrix4fv(model_loc, 1, GL_TRUE, model)
        glUniformMatrix4fv(view_loc, 1, GL_TRUE, view)
        glUniformMatrix4fv(proj_loc, 1, GL_TRUE, projection)
        
        glUniform3fv(glGetUniformLocation(self.shader_program, "viewPos"), 1, camera_pos)
        
        # Atualizar luzes
        lights = self.update_lights()
        
        # Luz 1
        glUniform3fv(glGetUniformLocation(self.shader_program, "light1.position"), 1, lights[0])
        glUniform3fv(glGetUniformLocation(self.shader_program, "light1.color"), 1, lights[1])
        glUniform1f(glGetUniformLocation(self.shader_program, "light1.intensity"), lights[2])
        glUniform1f(glGetUniformLocation(self.shader_program, "light1.ambientStrength"), lights[3])
        glUniform1f(glGetUniformLocation(self.shader_program, "light1.specularStrength"), lights[4])
        
        # Luz 2
        glUniform3fv(glGetUniformLocation(self.shader_program, "light2.position"), 1, lights[5])
        glUniform3fv(glGetUniformLocation(self.shader_program, "light2.color"), 1, lights[6])
        glUniform1f(glGetUniformLocation(self.shader_program, "light2.intensity"), lights[7])
        glUniform1f(glGetUniformLocation(self.shader_program, "light2.ambientStrength"), lights[8])
        glUniform1f(glGetUniformLocation(self.shader_program, "light2.specularStrength"), lights[9])
        
        # Luz 3
        glUniform3fv(glGetUniformLocation(self.shader_program, "light3.position"), 1, lights[10])
        glUniform3fv(glGetUniformLocation(self.shader_program, "light3.color"), 1, lights[11])
        glUniform1f(glGetUniformLocation(self.shader_program, "light3.intensity"), lights[12])
        glUniform1f(glGetUniformLocation(self.shader_program, "light3.ambientStrength"), lights[13])
        glUniform1f(glGetUniformLocation(self.shader_program, "light3.specularStrength"), lights[14])
        
        glUniform1f(glGetUniformLocation(self.shader_program, "material.shininess"), 32.0)
        glUniform1f(glGetUniformLocation(self.shader_program, "material.reflectivity"), 0.5)
        glUniform1f(glGetUniformLocation(self.shader_program, "time"), self.time)
        
        glBindVertexArray(self.VAO_cube)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        glBindVertexArray(0)
        
        # ========== DESENHAR ESFERAS PARA VISUALIZAR AS LUZES ==========
        # Luz 1 - Branca (fixa)
        self.draw_light_sphere(lights[0], [1.0, 1.0, 1.0], view, projection)
        
        # Luz 2 - Vermelha (rotativa)
        self.draw_light_sphere(lights[5], [1.0, 0.3, 0.3], view, projection)
        
        # Luz 3 - Azul com intensidade pulsante
        pulse = lights[15] if len(lights) > 15 else 0.5
        blue_intensity = 0.5 + pulse * 0.5
        self.draw_light_sphere(lights[10], [0.3 * blue_intensity, 0.5 * blue_intensity, 1.0], view, projection)
        
        # Atualizar ângulo de rotação
        self.rotation_angle += 0.005
        
        glfw.swap_buffers(self.window)
        glfw.poll_events()
    
    def run(self):
        """Loop principal da aplicação"""
        print("🎮 Loop principal iniciado...")
        print("=" * 60)
        print("✨ VISUALIZAÇÃO DAS LUZES:")
        print("   ⚪ Luz Branca - Fixa (posição estática em 2, 3, 2)")
        print("   🔴 Luz Vermelha - Movimento circular ao redor do cubo")
        print("   🔵 Luz Azul - Movimento vertical com intensidade pulsante")
        print("=" * 60)
        print("🎯 As esferas coloridas mostram EXATAMENTE onde cada luz está!")
        print("=" * 60)
        
        frame_count = 0
        last_print_time = glfw.get_time()
        
        while not glfw.window_should_close(self.window):
            self.render()
            
            frame_count += 1
            current_time = glfw.get_time()
            if current_time - last_print_time >= 2.0:
                # Mostrar posições das luzes a cada 2 segundos
                lights = self.update_lights()
                print(f"📍 Luz Branca: ({lights[0][0]:.2f}, {lights[0][1]:.2f}, {lights[0][2]:.2f})")
                print(f"📍 Luz Vermelha: ({lights[5][0]:.2f}, {lights[5][1]:.2f}, {lights[5][2]:.2f})")
                print(f"📍 Luz Azul: ({lights[10][0]:.2f}, {lights[10][1]:.2f}, {lights[10][2]:.2f})")
                print("-" * 40)
                frame_count = 0
                last_print_time = current_time
        
        # Limpar recursos
        print("🧹 Limpando recursos...")
        glDeleteVertexArrays(1, [self.VAO_cube])
        glDeleteVertexArrays(1, [self.VAO_sphere])
        glDeleteBuffers(1, [self.VBO_cube_vertices, self.VBO_cube_normals, self.VBO_cube_colors])
        glDeleteBuffers(1, [self.VBO_sphere_vertices])
        glDeleteProgram(self.shader_program)
        glDeleteProgram(self.light_shader_program)
        
        glfw.terminate()
        print("=" * 60)
        print("✅ Aplicação finalizada com sucesso!")
        print("=" * 60)

# ==================== PONTO DE ENTRADA ====================
if __name__ == "__main__":
    print("=" * 60)
    print("🎨 Iniciando Aplicação OpenGL com Iluminação")
    print("🔆 VISUALIZAÇÃO DAS FONTES DE LUZ ATIVADA")
    print("=" * 60)
    print("📌 Controles:")
    print("   🖱️  Mouse: Rotacionar a câmera")
    print("   ⌨️  W/S: Aproximar/Afastar")
    print("   ⌨️  R: Resetar câmera")
    print("   ⌨️  ESC: Sair")
    print("=" * 60)
    print("✨ As ESFERAS COLORIDAS mostram a posição EXATA das luzes:")
    print("   ⚪ BRANCA = Luz fixa (2, 3, 2)")
    print("   🔴 VERMELHA = Luz rotativa ao redor do cubo")
    print("   🔵 AZUL = Luz com movimento vertical pulsante")
    print("=" * 60)
    
    try:
        app = OpenGLApp()
        app.run()
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        glfw.terminate()
        sys.exit(1)