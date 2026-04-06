import glfw
from OpenGL.GL import *
import glm
import numpy as np
import ctypes
import time
from PIL import Image, ImageDraw, ImageFont

# Vertex Shader
vertex_shader_source = """
#version 410 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;
out vec3 vColor;
uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;
void main(){
    gl_Position = projection * view * model * vec4(position, 1.0);
    vColor = color;
}
"""

# Fragment Shader
fragment_shader_source = """
#version 410 core
in vec3 vColor;
out vec4 fragColor;
void main(){
    fragColor = vec4(vColor, 1.0);
}
"""

# Variáveis para cálculo do FPS
last_time = time.time()
frame_count = 0

# Função para calcular FPS
def calculate_fps():
    global last_time, frame_count
    current_time = time.time()
    frame_count += 1
    delta = current_time - last_time
    if delta >= 1.0:  # Se passou 1 segundo
        fps = frame_count / delta
        print(f"FPS: {fps:.2f}")
        frame_count = 0
        last_time = current_time

# Função para gerar uma textura de texto (usando Pillow)
def create_fps_texture(fps_text):
    # Cria uma imagem de 256x256 com o texto do FPS
    img = Image.new("RGB", (256, 256), color=(150, 120, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((10, 10), fps_text, font=font, fill=(0, 0, 0))

    # Converte a imagem para um formato que o OpenGL entenda
    img_data = img.tobytes()

    # Criar a textura no OpenGL
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 256, 256, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    glGenerateMipmap(GL_TEXTURE_2D)

    return texture_id

def cursor_callback(window, xpos, ypos):
    print('mouse cursor moving: (%d, %d)'%(xpos, ypos))

def button_callback(window, button, action, mod): 
    if button==glfw.MOUSE_BUTTON_LEFT:
        if action==glfw.PRESS:
            print('press left btn: (%d, %d)'%glfw.get_cursor_pos(window))
        elif action==glfw.RELEASE:
            print('release left btn: (%d, %d)'%glfw.get_cursor_pos(window))
    if button==glfw.MOUSE_BUTTON_RIGHT:#right
        if action==glfw.PRESS:
            print('press right btn: (%d, %d)'%glfw.get_cursor_pos(window))
        elif action==glfw.RELEASE:
            print('release right btn: (%d, %d)'%glfw.get_cursor_pos(window))

def scroll_callback(window, xoffset, yoffset): 
    print('mouse wheel scroll: %d, %d'%(xoffset, yoffset))

def key_event(window,key,scancode,action,mods):
    global t_zz,t_yy,t_xx

    print('[key event] key=',key)
    if key == 265: t_zz += 0.01 #cima
    if key == 264: t_zz -= 0.01 #baixo
    
    if key == 262: t_xx += 0.01 #cima
    if key == 263: t_xx -= 0.01 #baixo

    if key == 87: t_yy+= 0.01 #cima
    if key == 83: t_yy -= 0.01 #baixo
        
    #if key:
        
        #if action==glfw.PRESS: print('press %c'%(chr(key)))   
        #elif action==glfw.RELEASE: print('release %c'%(chr(key)))
        #elif action==glfw.REPEAT: print('repeat %c'%(chr(key)))
        #elif key==glfw.KEY_SPACE and action==glfw.PRESS:
           # print('press space: (%d, %d)'%glfw.get_cursor_pos(window))



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
t_zz = 3
t_yy = 1
t_xx = 0

def main():
    if not glfw.init():
        return
    
    # Set OpenGL version to 4.1 core profile
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)  # Necessary for macOS
    
    window = glfw.create_window(800, 600, "Cubo Colorido", None, None)
    glfw.set_key_callback(window,key_event)
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
    
    plane_vertices = np.array([
        # Posição        # Cor
        -1.0,  0.0, -1.0, 0.0, 0.0, 0.0,
         1.0,  0.0, -1.0, 0.0, 0.0, 0.0,
         1.0,  0.0,  1.0, 0.0, 0.0, 0.0,
        -1.0,  0.0,  1.0, 0.0, 0.0, 0.0,
    ], dtype=np.float32)
    
    plane_indices = np.array([
        0, 1, 2,
        2, 3, 0
    ], dtype=np.uint32)
    
    vertices = np.array([
        -0.5, -0.5, -0.5,  1.0, 0.0, 0.0,  # 0
         0.5, -0.5, -0.5,  0.0, 1.0, 0.0,  # 1
         0.5,  0.5, -0.5,  0.0, 0.0, 1.0,  # 2
        -0.5,  0.5, -0.5,  1.0, 1.0, 0.0,  # 3
        -0.5, -0.5,  0.5,  1.0, 0.0, 1.0,  # 4
         0.5, -0.5,  0.5,  0.0, 1.0, 1.0,  # 5
         0.5,  0.5,  0.5,  1.0, 1.0, 1.0,  # 6
        -0.5,  0.5,  0.5,  0.0, 0.0, 0.0   # 7
    ], dtype=np.float32)
    
    indices = np.array([
        0, 1, 2, 2, 3, 0,  # Face de trás
        4, 5, 6, 6, 7, 4,  # Face da frente
        0, 1, 5, 5, 4, 0,  # Face de baixo
        2, 3, 7, 7, 6, 2,  # Face de cima
        0, 3, 7, 7, 4, 0,  # Face da esquerda
        1, 2, 6, 6, 5, 1   # Face da direita
    ], dtype=np.uint32)
    
    
    shader_program = create_shader_program(vertex_shader_source, fragment_shader_source)
    
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
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * plane_vertices.itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * plane_vertices.itemsize, ctypes.c_void_p(3 * plane_vertices.itemsize))
    glEnableVertexAttribArray(1)
    
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    
    # Enable depth test
    glEnable(GL_DEPTH_TEST)
    
    # Set up projection matrix
    projection = glm.perspective(glm.radians(45.0), 800 / 600, 0.1, 100.0)
    
    glViewport(0, 0, 800, 600)
    glClearColor(1.0, 1.0, 1.0, 1.0)
    
    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
         # Calcular FPS
        calculate_fps()
        
        # Criar textura do FPS e exibir na tela
        fps_texture = create_fps_texture("casa")
        glBindTexture(GL_TEXTURE_2D, fps_texture)
        
        
        glUseProgram(shader_program)
        # model
        model = glm.mat4(1.0)
        model_loc = glGetUniformLocation(shader_program, "model")
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(model))
        # view
        view = glm.lookAt(glm.vec3(t_xx,t_yy, t_zz), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
        view_loc = glGetUniformLocation(shader_program, "view")
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view))

        # projection
        projection_loc = glGetUniformLocation(shader_program, "projection")
        glUniformMatrix4fv(projection_loc, 1, GL_FALSE, glm.value_ptr(projection))
        
        # Set up model matrix for plane
        # model_plane = glm.translate(glm.mat4(1.0), glm.vec3(0.0, -0.5, 0.0))
        # glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(model))
       
        # Draw plane
        glBindVertexArray(VAO_plane)
        glDrawElements(GL_TRIANGLES, len(plane_indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
         # TRIANGLES
        glfw.swap_buffers(window)
        glfw.poll_events()
        
    glDeleteVertexArrays(1, [VAO_plane])
    glDeleteBuffers(1, [VBO_plane])
    glDeleteBuffers(1, [EBO_plane])
    
    glfw.terminate()

if __name__ == "__main__":
    main()
