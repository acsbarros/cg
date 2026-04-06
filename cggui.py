import glfw
from OpenGL.GL import *
import imgui
from imgui.integrations.glfw import GlfwRenderer
import numpy as np
import glm

# Shaders
vertex_shader_source = """
#version 410 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;
out vec3 vColor;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
void main() {
    gl_Position = projection * view * model * vec4(position, 1.0);
    vColor = color;
}
"""

fragment_shader_source = """
#version 410 core
in vec3 vColor;
out vec4 fragColor;
void main() {
    fragColor = vec4(vColor, 1.0);
}
"""

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
    return program

def create_cube():
    # Definição dos vértices e cores do cubo (posição + cor)
    vertices = np.array([
        # Frente
        -0.5, -0.5,  0.5, 1.0, 0.0, 0.0,  # Vermelho
         0.5, -0.5,  0.5, 0.0, 1.0, 0.0,  # Verde
         0.5,  0.5,  0.5, 0.0, 0.0, 1.0,  # Azul
        -0.5,  0.5,  0.5, 1.0, 1.0, 0.0,  # Amarelo
        # Trás
        -0.5, -0.5, -0.5, 1.0, 0.0, 1.0,  # Magenta
         0.5, -0.5, -0.5, 0.0, 1.0, 1.0,  # Ciano
         0.5,  0.5, -0.5, 1.0, 0.5, 0.5,  # Cinza claro
        -0.5,  0.5, -0.5, 0.5, 0.5, 0.5   # Cinza escuro
    ], dtype=np.float32)

    # Índices para formar as faces do cubo com triângulos
    indices = np.array([
        # Frente
        0, 1, 2, 2, 3, 0,
        # Trás
        4, 5, 6, 6, 7, 4,
        # Esquerda
        0, 3, 7, 7, 4, 0,
        # Direita
        1, 2, 6, 6, 5, 1,
        # Topo
        3, 2, 6, 6, 7, 3,
        # Fundo
        0, 1, 5, 5, 4, 0
    ], dtype=np.uint32)

    # Criar VAO, VBO, e EBO para o cubo
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    EBO = glGenBuffers(1)

    # Bind VAO
    glBindVertexArray(VAO)

    # Bind e definir dados do VBO
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # Bind e definir dados do EBO
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    # Atributos de posição (location = 0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * vertices.itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # Atributos de cor (location = 1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * vertices.itemsize, ctypes.c_void_p(3 * vertices.itemsize))
    glEnableVertexAttribArray(1)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    return VAO, len(indices)

def main():
    # Inicializar GLFW
    if not glfw.init():
        return

    # Configurar a janela
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

    window = glfw.create_window(800, 600, "GLFW + ImGui + Cubo 3D", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    # Inicializar ImGui
    imgui.create_context()
    impl = GlfwRenderer(window)

    # Criar o shader program para o cubo
    shader_program = create_shader_program(vertex_shader_source, fragment_shader_source)

    # Criar o cubo
    cube_VAO, cube_indices_len = create_cube()

    # Variáveis para o controle do botão
    show_button_clicked = False

    # Configurar a viewport
    glViewport(0, 0, 800, 600)
    glEnable(GL_DEPTH_TEST)

    # Matriz de projeção
    projection = np.identity(4, dtype=np.float32)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        # Limpar a tela e o buffer de profundidade
        glClearColor(0.2, 0.2, 0.2, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Renderizar o cubo 3D
        glUseProgram(shader_program)

        # Matriz de modelo (
                # Matriz de modelo (identidade para começar)
        model = np.identity(4, dtype=np.float32)

        # Matriz de view (câmera posicionada em Z = 3, olhando para a origem)
        view = np.array(glm.lookAt(glm.vec3(0.0, 0.0, 3.0), glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0, 1.0, 0.0)), dtype=np.float32)

        # Matriz de projeção (perspectiva)
        projection = np.array(glm.perspective(glm.radians(45.0), 800/600, 0.1, 100.0), dtype=np.float32)

        # Enviar matrizes para o shader
        model_loc = glGetUniformLocation(shader_program, "model")
        view_loc = glGetUniformLocation(shader_program, "view")
        projection_loc = glGetUniformLocation(shader_program, "projection")

        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
        glUniformMatrix4fv(projection_loc, 1, GL_FALSE, projection)

        # Vincular o VAO do cubo
        glBindVertexArray(cube_VAO)
        
        # Renderizar o cubo
        glDrawElements(GL_TRIANGLES, cube_indices_len, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)
        glUseProgram(0)

        # Renderizar a interface ImGui
        imgui.new_frame()

        # Criar uma janela simples do ImGui
        imgui.begin("Minha Janela ImGui")

        # Exibir um botão
        if imgui.button("Clique Aqui!"):
            show_button_clicked = True

        # Exibir uma label que muda de acordo com o clique no botão
        if show_button_clicked:
            imgui.text("Você clicou no botão!")
        else:
            imgui.text("Clique no botão acima.")

        imgui.end()

        # Renderizar o conteúdo do ImGui
        imgui.render()
        impl.render(imgui.get_draw_data())

        # Trocar buffers
        glfw.swap_buffers(window)

    # Limpar ImGui e GLFW
    impl.shutdown()
    glfw.terminate()

if __name__ == "__main__":
    main()

