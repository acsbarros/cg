
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


    shader_program = create_shader_program(vertex_shader_source, fragment_shader_source)

    # Enable depth test
    glEnable(GL_DEPTH_TEST)

    # Set up projection matrix
    projection = glm.perspective(glm.radians(45.0), 800 / 600, 0.1, 100.0)

    glViewport(0, 0, 800, 600)
    glClearColor(1.0, 1.0, 1.0, 1.0)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

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

        # Draw plane
        glBindVertexArray(VAO_plane)
        glDrawElements(GL_TRIANGLES, len(plane_indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        # TRIANGLES
        glfw.swap_buffers(window)
        glfw.poll_events()
    
    #glDeleteVertexArrays(1, [VAO_plane])
    #glDeleteBuffers(1, [VBO_plane])
    #glDeleteBuffers(1, [EBO_plane])

    glfw.terminate()

if __name__ == "__main__":
    main()





