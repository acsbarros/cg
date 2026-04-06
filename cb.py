import glfw
from OpenGL.GL import *
import imgui
from imgui.integrations.glfw import GlfwRenderer
import glm
import numpy as np

# Vertex Shader para o cubo (Atualizado)
vertex_shader_source = """
#version 410 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;
layout(location = 2) in vec3 normal;

out vec3 fragPos;
out vec3 vColor;
out vec3 Normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    fragPos = vec3(model * vec4(position, 1.0)); // Posição do fragmento no espaço do mundo
    vColor = color; // Cor do vértice
    Normal = mat3(transpose(inverse(model))) * normal; // Normal transformada
    gl_Position = projection * view * model * vec4(position, 1.0);
}
"""

# Fragment Shader para o cubo (Atualizado)
fragment_shader_source = """
#version 410 core
in vec3 fragPos;
in vec3 vColor;
in vec3 Normal;

out vec4 fragColor;

struct Material {
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
    float shininess;
};

struct Spotlight {
    vec3 position;
    vec3 direction;
    float cutOff;
    float outerCutOff;
    
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;

    float constant;
    float linear;
    float quadratic;
};

uniform vec3 viewPos;
uniform Material material;
uniform Spotlight light;

void main()
{
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(light.position - fragPos);

    // Spotlight cutoff
    float theta = dot(lightDir, normalize(-light.direction));
    float epsilon = light.cutOff - light.outerCutOff;
    float intensity = clamp((theta - light.outerCutOff) / epsilon, 0.0, 1.0);

    // Difusa
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = light.diffuse * diff * vColor;

    // Especular
    vec3 viewDir = normalize(viewPos - fragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    vec3 specular = light.specular * spec * material.specular;

    // Ambiente
    vec3 ambient = light.ambient * material.ambient;

    // Atenuação
    float distance = length(light.position - fragPos);
    float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * (distance * distance));

    vec3 result = ambient + (diffuse + specular) * intensity;
    result *= attenuation;

    fragColor = vec4(result, 1.0);
}
"""

# Função para compilar shaders, criar programa e setar uniformes (continuado abaixo)
...
# Função para compilar shaders e criar programa
def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
        raise RuntimeError(glGetShaderInfoLog(shader))
    return shader

def create_shader_program(vertex_source, fragment_source):
    vertex_shader = compile_shader(vertex_source, GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment_source, GL_FRAGMENT_SHADER)
    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)
    if glGetProgramiv(program, GL_LINK_STATUS) != GL_TRUE:
        raise RuntimeError(glGetProgramInfoLog(program))
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)
    return program

def main():
    # Inicializar GLFW
    if not glfw.init():
        return

    # Configurações de janela
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

    window = glfw.create_window(800, 600, "GLFW + ImGui + Cubo com Luz", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    # Inicializar ImGui
    imgui.create_context()
    impl = GlfwRenderer(window)

    # Criar programa de shader
    shader_program = create_shader_program(vertex_shader_source, fragment_shader_source)

    # Vértices, cores e normais do cubo
    vertices = np.array([
        # Posição          # Cor         # Normal
        -0.5, -0.5, -0.5,  1.0, 0.0, 0.0,  0.0,  0.0, -1.0,
         0.5, -0.5, -0.5,  0.0, 1.0, 0.0,  0.0,  0.0, -1.0,
         0.5,  0.5, -0.5,  0.0, 0.0, 1.0,  0.0,  0.0, -1.0,
        -0.5,  0.5, -0.5,  1.0, 1.0, 0.0,  0.0,  0.0, -1.0,
        -0.5, -0.5,  0.5,  1.0, 0.0, 1.0,  0.0,  0.0,  1.0,
         0.5, -0.5,  0.5,  0.0, 1.0, 1.0,  0.0,  0.0,  1.0,
         0.5,  0.5,  0.5,  1.0, 1.0, 1.0,  0.0,  0.0,  1.0,
        -0.5,  0.5,  0.5,  0.0, 0.0, 0.0,  0.0,  0.0,  1.0
    ], dtype=np.float32)

    # Índices para desenhar o cubo
    indices = np.array([
        0, 1, 2, 2, 3, 0,  # Face de trás
        4, 5, 6, 6, 7, 4,  # Face da frente
        0, 1, 5, 5, 4, 0,  # Face de baixo
        2, 3, 7, 7, 6, 2,  # Face de cima
        0, 3, 7, 7, 4, 0,  # Face da esquerda
        1, 2, 6, 6, 5, 1   # Face da direita
    ], dtype=np.uint32)

    # Configurar buffers e VAO
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    EBO = glGenBuffers(1)

    glBindVertexArray(VAO)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    # Posição
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 9 * vertices.itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # Cor
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 9 * vertices.itemsize, ctypes.c_void_p(3 * vertices.itemsize))
    glEnableVertexAttribArray(1)

    # Normal
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 9 * vertices.itemsize, ctypes.c_void_p(6 * vertices.itemsize))
    glEnableVertexAttribArray(2)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    # Variáveis de controle
    input_text = "Digite aqui..."
    show_button_clicked = False

    glEnable(GL_DEPTH_TEST)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        # Limpar a tela
        glClearColor(0.2, 0.2, 0.2, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Usar o shader do cubo
        glUseProgram(shader_program)

        # Definir as matrizes de transformação
        model = glm.rotate(glm.mat4(1.0), glfw.get_time(), glm.vec3(0.5, 1.0, 0.0))
        view = glm.lookAt(glm.vec3(0.0, 0.0, 5.0), glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0, 1.0, 0.0))
        projection = glm.perspective(glm.radians(45.0), 800 / 600, 0.1, 100.0)

        # Passar as matrizes para o shader
        glUniformMatrix4fv(glGetUniformLocation(shader_program, "model"), 1, GL_FALSE, glm.value_ptr(model))
        glUniformMatrix4fv(glGetUniformLocation(shader_program, "view"), 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(glGetUniformLocation(shader_program, "projection"), 1, GL_FALSE, glm.value_ptr(projection))

        # Propriedades do material
        glUniform3fv(glGetUniformLocation(shader_program, "material.ambient"), 1, glm.value_ptr(glm.vec3(1.0, 0.5, 0.31)))
        glUniform3fv(glGetUniformLocation(shader_program, "material.diffuse"), 1, glm.value_ptr(glm.vec3(1.0, 0.5, 0.31)))
        glUniform3fv(glGetUniformLocation(shader_program, "material.specular"), 1, glm.value_ptr(glm.vec3(0.5, 0.5, 0.5)))
        glUniform1f(glGetUniformLocation(shader_program, "material.shininess"), 32.0)

        # Definir a posição da câmera (viewPos)
        view_pos = glm.vec3(0.0, 0.0, 5.0)
        glUniform3fv(glGetUniformLocation(shader_program, "viewPos"), 1, glm.value_ptr(view_pos))

        # Propriedades da luz (Spotlight)
        light_pos = glm.vec3(0.0, 0.0, 3.0)
        light_dir = glm.vec3(0.0, 0.0, -1.0)
        glUniform3fv(glGetUniformLocation(shader_program, "light.position"), 1, glm.value_ptr(light_pos))
        glUniform3fv(glGetUniformLocation(shader_program, "light.direction"), 1, glm.value_ptr(light_dir))
        glUniform1f(glGetUniformLocation(shader_program, "light.cutOff"), glm.cos(glm.radians(12.5)))  # Ângulo interno
        glUniform1f(glGetUniformLocation(shader_program, "light.outerCutOff"), glm.cos(glm.radians(17.5)))  # Ângulo externo

        glUniform3fv(glGetUniformLocation(shader_program, "light.ambient"), 1, glm.value_ptr(glm.vec3(0.1, 0.1, 0.1)))
        glUniform3fv(glGetUniformLocation(shader_program, "light.diffuse"), 1, glm.value_ptr(glm.vec3(0.8, 0.8, 0.8)))
        glUniform3fv(glGetUniformLocation(shader_program, "light.specular"), 1, glm.value_ptr(glm.vec3(1.0, 1.0, 1.0)))

        # Constantes da luz
        glUniform1f(glGetUniformLocation(shader_program, "light.constant"), 1.0)
        glUniform1f(glGetUniformLocation(shader_program, "light.linear"), 0.09)
        glUniform1f(glGetUniformLocation(shader_program, "light.quadratic"), 0.032)

        # Desenhar o cubo
        glBindVertexArray(VAO)
        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

        # Interface ImGui
        imgui.new_frame()

        # Criar janela ImGui
        imgui.begin("Janela de Controle")
        imgui.text("Clique no botão abaixo:")
        if imgui.button("Clique aqui!"):
            show_button_clicked = True

        if show_button_clicked:
            imgui.text("Você clicou no botão!")
        else:
            imgui.text("Clique no botão para uma mensagem.")

        changed, input_text = imgui.input_text("Caixa de Texto", input_text, 256)
        if changed:
            imgui.text(f"Texto atualizado: {input_text}")
            
        imgui.end()

        imgui.render()
        impl.render(imgui.get_draw_data())

        # Trocar buffers
        glfw.swap_buffers(window)

    # Limpar
    impl.shutdown()
    glfw.terminate()

if __name__ == "__main__":
    main()
