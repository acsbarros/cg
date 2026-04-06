import glfw
from OpenGL.GL import *
import glm
import numpy as np
import ctypes

# Vertex Shader
vertex_shader_source = """
#version 410 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;
layout(location = 2) in vec3 normal; // Adicionei normais

out vec3 vColor;
out vec3 FragPos; // Posição do fragmento
out vec3 Normal;  // Normal do fragmento

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

void main(){
    gl_Position = projection * view * model * vec4(position, 1.0);
    FragPos = vec3(model * vec4(position, 1.0));
    Normal = mat3(transpose(inverse(model))) * normal; // Transformar normais
    vColor = color;
}
"""

# Fragment Shader
fragment_shader_source = """
#version 410 core
in vec3 vColor;
in vec3 FragPos; // Posição do fragmento
in vec3 Normal;  // Normal do fragmento

out vec4 fragColor;

uniform vec3 lightPos;   // Posição da luz
uniform vec3 viewPos;    // Posição da câmera
uniform vec3 lightColor; // Cor da luz

void main(){
    // Propriedades do material
    vec3 ambientColor = vColor * 0.1; // Componente ambiente

    // Componente difusa
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * vColor;

    // Componente especular
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32.0);
    vec3 specular = spec * lightColor;

    vec3 result = ambientColor + diffuse + specular;
    fragColor = vec4(result, 1.0);
}
"""

def cursor_callback(window, xpos, ypos):
    print('mouse cursor moving: (%d, %d)' % (xpos, ypos))

def button_callback(window, button, action, mod):
    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            print('press left btn: (%d, %d)' % glfw.get_cursor_pos(window))
        elif action == glfw.RELEASE:
            print('release left btn: (%d, %d)' % glfw.get_cursor_pos(window))
    if button == glfw.MOUSE_BUTTON_RIGHT:
        if action == glfw.PRESS:
            print('press right btn: (%d, %d)' % glfw.get_cursor_pos(window))
        elif action == glfw.RELEASE:
            print('release right btn: (%d, %d)' % glfw.get_cursor_pos(window))

def scroll_callback(window, xoffset, yoffset):
    print('mouse wheel scroll: %d, %d' % (xoffset, yoffset))

def key_event(window, key, scancode, action, mods):
    if key:
        if action == glfw.PRESS: print('press %c' % (chr(key)))
        elif action == glfw.RELEASE: print('release %c' % (chr(key)))
        elif action == glfw.REPEAT: print('repeat %c' % (chr(key)))
        elif key == glfw.KEY_SPACE and action == glfw.PRESS:
            print('press space: (%d, %d)' % glfw.get_cursor_pos(window))

# Compile shaders and link them into a program
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

def main():
    if not glfw.init():
        return
    
    # Set OpenGL version to 4.1 core profile
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)  # Necessary for macOS
    
    window = glfw.create_window(800, 600, "Cubo Iluminado", None, None)
    glfw.set_key_callback(window, key_event)
    glfw.set_cursor_pos_callback(window, cursor_callback)
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    
    # Print OpenGL and GLSL versions
    opengl_version = glGetString(GL_VERSION)
    print('OpenGL Version:', opengl_version.decode("utf-8"))
    glsl_version = glGetString(GL_SHADING_LANGUAGE_VERSION)
    print('GLSL Version:', glsl_version.decode("utf-8"))
    
    vertices = np.array([
        -0.5, -0.5, -0.5,  1.0, 0.0, 0.0,  0.0,  0.0, -1.0, # 0
         0.5, -0.5, -0.5,  0.0, 1.0, 0.0,  0.0,  0.0, -1.0, # 1
         0.5,  0.5, -0.5,  0.0, 0.0, 1.0,  0.0,  0.0, -1.0, # 2
        -0.5,  0.5, -0.5,  1.0, 1.0, 0.0,  0.0,  0.0, -1.0, # 3
        -0.5, -0.5,  0.5,  1.0, 0.0, 1.0,  0.0,  0.0,  1.0, # 4
         0.5, -0.5,  0.5,  0.0, 1.0, 1.0,  0.0,  0.0,  1.0, # 5
         0.5,  0.5,  0.5,  1.0, 1.0, 1.0,  0.0,  0.0,  1.0, # 6
        -0.5,  0.5,  0.5,  0.0, 0.0, 0.0,  0.0,  0.0,  1.0, # 7
        -0.5, -0.5, -0.5,  1.0, 0.0, 0.0, -1.0,  0.0,  0.0, # 8
        -0.5,  0.5, -0.5,  1.0, 1.0, 0.0, -1.0,  0.0,  0.0, # 9
        -0.5,  0.5,  0.5,  0.0, 0.0, 0.0, -1.0,  0.0,  0.0, # 10
        -0.5, -0.5,  0.5,  1.0, 0.0, 1.0, -1.0,  0.0,  0.0, # 11
         0.5, -0.5, -0.5,  0.0, 1.0, 0.0,  1.0,  0.0,  0.0, # 12
         0.5,  0.5, -0.5,  0.0, 0.0, 1.0,  1.0,  0.0,  0.0, # 13
         0.5,  0.5,  0.5,  1.0, 1.0, 1.0,  1.0,  0.0,  0.0, # 14
         0.5, -0.5,  0.5,  0.0, 1.0, 1.0,  1.0,  0.0,  0.0, # 15
        -0.5, -0.5, -0.5,  1.0, 0.0, 0.0,  0.0, -1.0,  0.0, # 16
         0.5, -0.5, -0.5,  0.0, 1.0, 0.0,  0.0, -1.0,  0.0, # 17
         0.5, -0.5,  0.5,  0.0, 1.0, 1.0,  0.0, -1.0,  0.0, # 18
        -0.5, -0.5,  0.5,  1.0, 0.0, 1.0,  0.0, -1.0,  0.0, # 19
        -0.5,  0.5, -0.5,  1.0, 1.0, 0.0,  0.0,  1.0,  0.0, # 20
         0.5,  0.5, -0.5,  0.0, 0.0, 1.0,  0.0,  1.0,  0.0, # 21
         0.5,  0.5,  0.5,  1.0, 1.0, 1.0,  0.0,  1.0,  0.0, # 22
        -0.5,  0.5,  0.5,  0.0, 0.0, 0.0,  0.0,  1.0,  0.0  # 23
    ], dtype=np.float32)
    
    indices = np.array([
        0, 1, 2, 2, 3, 0,    # Face de trás
        4, 5, 6, 6, 7, 4,    # Face da frente
        8, 9, 10, 10, 11, 8, # Face esquerda
        12, 13, 14, 14, 15, 12, # Face direita
        16, 17, 18, 18, 19, 16, # Face de baixo
        20, 21, 22, 22, 23, 20  # Face de cima
    ], dtype=np.uint32)
    
    plane_vertices = np.array([
        # Posição        # Cor         # Normais
        -1.0,  0.0, -1.0, 0.5, 0.5, 0.5, 0.0, 1.0, 0.0,
         1.0,  0.0, -1.0, 0.5, 0.5, 0.5, 0.0, 1.0, 0.0,
         1.0,  0.0,  1.0, 0.5, 0.5, 0.5, 0.0, 1.0, 0.0,
        -1.0,  0.0,  1.0, 0.5, 0.5, 0.5, 0.0, 1.0, 0.0,
    ], dtype=np.float32)
    
    plane_indices = np.array([
        0, 1, 2,
        2, 3, 0
    ], dtype=np.uint32)
    
    shader_program = create_shader_program(vertex_shader_source, fragment_shader_source)
    
    # Create and bind VAO
    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)
    
    # Create and bind VBO
    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    
    # Create and bind EBO
    EBO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
    
    # Specify the layout of the vertex data
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 9 * vertices.itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 9 * vertices.itemsize, ctypes.c_void_p(3 * vertices.itemsize))
    glEnableVertexAttribArray(1)
    
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 9 * vertices.itemsize, ctypes.c_void_p(6 * vertices.itemsize))
    glEnableVertexAttribArray(2)
    
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    
    # Create and bind VAO for plane
    VAO_plane = glGenVertexArrays(1)
    glBindVertexArray(VAO_plane)
    
    # Create and bind VBO for plane
    VBO_plane = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO_plane)
    glBufferData(GL_ARRAY_BUFFER, plane_vertices.nbytes, plane_vertices, GL_STATIC_DRAW)
    
    # Create and bind EBO for plane
    EBO_plane = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO_plane)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, plane_indices.nbytes, plane_indices, GL_STATIC_DRAW)
    
    # Specify the layout of the vertex data for plane
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 9 * plane_vertices.itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 9 * plane_vertices.itemsize, ctypes.c_void_p(3 * plane_vertices.itemsize))
    glEnableVertexAttribArray(1)
    
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 9 * plane_vertices.itemsize, ctypes.c_void_p(6 * plane_vertices.itemsize))
    glEnableVertexAttribArray(2)
    
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    
    glEnable(GL_DEPTH_TEST)
    
    # Define light properties
    lightPos = glm.vec3(1.2, 1.0, 2.0)
    lightColor = glm.vec3(1.0, 1.0, 1.0)
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        
        # Clear the color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glUseProgram(shader_program)
        
        # Define view and projection matrices
        view = glm.lookAt(glm.vec3(4.0, 3.0, 3.0), glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0, 1.0, 0.0))
        projection = glm.perspective(glm.radians(45.0), 800 / 600, 0.1, 100.0)
        
        # Set uniform variables for the shaders
        viewLoc = glGetUniformLocation(shader_program, "view")
        projectionLoc = glGetUniformLocation(shader_program, "projection")
        lightPosLoc = glGetUniformLocation(shader_program, "lightPos")
        viewPosLoc = glGetUniformLocation(shader_program, "viewPos")
        lightColorLoc = glGetUniformLocation(shader_program, "lightColor")
        
        glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(projectionLoc, 1, GL_FALSE, glm.value_ptr(projection))
        glUniform3fv(lightPosLoc, 1, glm.value_ptr(lightPos))
        glUniform3fv(viewPosLoc, 1, glm.value_ptr(glm.vec3(4.0, 3.0, 3.0)))
        glUniform3fv(lightColorLoc, 1, glm.value_ptr(lightColor))
        
        # Draw the cube
        model = glm.mat4(1.0)
        model = glm.rotate(model, glm.radians(glfw.get_time() * 50), glm.vec3(0.5, 1.0, 0.0))
        modelLoc = glGetUniformLocation(shader_program, "model")
        glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm.value_ptr(model))
        
        glBindVertexArray(VAO)
        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        
        # Draw the plane
        model = glm.mat4(1.0)
        modelLoc = glGetUniformLocation(shader_program, "model")
        glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm.value_ptr(model))
        
        glBindVertexArray(VAO_plane)
        glDrawElements(GL_TRIANGLES, len(plane_indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        
        glfw.swap_buffers(window)
    
    glfw.terminate()

if __name__ == "__main__":
    main()
