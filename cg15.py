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
layout(location = 2) in vec3 normal;

out vec3 vColor;
out vec3 FragPos;
out vec3 Normal;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

void main() {
    gl_Position = projection * view * model * vec4(position, 1.0);
    FragPos = vec3(model * vec4(position, 1.0));
    Normal = mat3(transpose(inverse(model))) * normal;
    vColor = color;
}
"""

# Fragment Shader
fragment_shader_source = """
#version 410 core
in vec3 vColor;
in vec3 FragPos;
in vec3 Normal;

out vec4 fragColor;

uniform vec3 lightPos;
uniform vec3 viewPos;
uniform vec3 lightColor;

void main() {
    // Ambient
    float ambientStrength = 0.5;
    vec3 ambient = ambientStrength * lightColor;
    
    // Diffuse 
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;
    
    // Specular
    float specularStrength = 0.5;
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);  
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = specularStrength * spec * lightColor;  
    
    vec3 result = (ambient + diffuse + specular) * vColor;
    fragColor = vec4(result, 1.0);
}
"""

# Light Shader (only vertex color, no lighting calculations)
light_vertex_shader_source = """
#version 410 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;

out vec3 vColor;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

void main() {
    gl_Position = projection * view * model * vec4(position, 1.0);
    vColor = color;
}
"""

light_fragment_shader_source = """
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

def main():
    if not glfw.init():
        return
    
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
    
    window = glfw.create_window(800, 600, "Lighting", None, None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    
    vertices = np.array([
        -0.5, -0.5, -0.5,  1.0, 0.0, 0.0,  0.0,  0.0, -1.0,
         0.5, -0.5, -0.5,  0.0, 1.0, 0.0,  0.0,  0.0, -1.0,
         0.5,  0.5, -0.5,  0.0, 0.0, 1.0,  0.0,  0.0, -1.0,
        -0.5,  0.5, -0.5,  1.0, 1.0, 0.0,  0.0,  0.0, -1.0,
        -0.5, -0.5,  0.5,  1.0, 0.0, 1.0,  0.0,  0.0,  1.0,
         0.5, -0.5,  0.5,  0.0, 1.0, 1.0,  0.0,  0.0,  1.0,
         0.5,  0.5,  0.5,  1.0, 1.0, 1.0,  0.0,  0.0,  1.0,
        -0.5,  0.5,  0.5,  0.0, 0.0, 0.0,  0.0,  0.0,  1.0,
        -0.5, -0.5, -0.5,  1.0, 0.0, 0.0, -1.0,  0.0,  0.0,
        -0.5,  0.5, -0.5,  1.0, 1.0, 0.0, -1.0,  0.0,  0.0,
        -0.5,  0.5,  0.5,  0.0, 0.0, 0.0, -1.0,  0.0,  0.0,
        -0.5, -0.5,  0.5,  1.0, 0.0, 1.0, -1.0,  0.0,  0.0,
         0.5, -0.5, -0.5,  0.0, 1.0, 0.0,  1.0,  0.0,  0.0,
         0.5,  0.5, -0.5,  0.0, 0.0, 1.0,  1.0,  0.0,  0.0,
         0.5,  0.5,  0.5,  1.0, 1.0, 1.0,  1.0,  0.0,  0.0,
         0.5, -0.5,  0.5,  0.0, 1.0, 1.0,  1.0,  0.0,  0.0,
        -0.5, -0.5, -0.5,  1.0, 0.0, 0.0,  0.0, -1.0,  0.0,
         0.5, -0.5, -0.5,  0.0, 1.0, 0.0,  0.0, -1.0,  0.0,
         0.5, -0.5,  0.5,  0.0, 1.0, 1.0,  0.0, -1.0,  0.0,
        -0.5, -0.5,  0.5,  1.0, 0.0, 1.0,  0.0, -1.0,  0.0,
        -0.5,  0.5, -0.5,  1.0, 1.0, 0.0,  0.0,  1.0,  0.0,
         0.5,  0.5, -0.5,  0.0, 0.0, 1.0,  0.0,  1.0,  0.0,
         0.5,  0.5,  0.5,  1.0, 1.0, 1.0,  0.0,  1.0,  0.0,
        -0.5,  0.5,  0.5,  0.0, 0.0, 0.0,  0.0,  1.0,  0.0
    ], dtype=np.float32)

    indices = np.array([
        0, 1, 2, 2, 3, 0,
        4, 5, 6, 6, 7, 4,
        8, 9, 10, 10, 11, 8,
        12, 13, 14, 14, 15, 12,
        16, 17, 18, 18, 19, 16,
        20, 21, 22, 22, 23, 20
    ], dtype=np.uint32)
    
    light_vertices = np.array([
        0.0, 0.1, 0.0, 1.0, 1.0, 1.0,
        -0.1, -0.1, 0.0, 1.0, 1.0, 1.0,
        0.1, -0.1, 0.0, 1.0, 1.0, 1.0
    ], dtype=np.float32)

    shader_program = create_shader_program(vertex_shader_source, fragment_shader_source)
    light_shader_program = create_shader_program(light_vertex_shader_source, light_fragment_shader_source)

    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)
    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    EBO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 9 * vertices.itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 9 * vertices.itemsize, ctypes.c_void_p(3 * vertices.itemsize))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 9 * vertices.itemsize, ctypes.c_void_p(6 * vertices.itemsize))
    glEnableVertexAttribArray(2)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    
    VAO_light = glGenVertexArrays(1)
    glBindVertexArray(VAO_light)
    VBO_light = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO_light)
    glBufferData(GL_ARRAY_BUFFER, light_vertices.nbytes, light_vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * light_vertices.itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * light_vertices.itemsize, ctypes.c_void_p(3 * light_vertices.itemsize))
    glEnableVertexAttribArray(1)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    glEnable(GL_DEPTH_TEST)

    lightPos = glm.vec3(2.0, 1.0, 2.0)
    lightColor = glm.vec3(1.0, 1.0, 1.0)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(shader_program)
        view = glm.lookAt(glm.vec3(4.0, 3.0, 3.0), glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0, 1.0, 0.0))
        projection = glm.perspective(glm.radians(25.0), 800 / 600, 0.1, 100.0)
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

        #model = glm.mat4(1.0)
        model = glm.translate(glm.mat4(1.0), glm.vec3(0.1, 0.0, 0.0))
        #model = glm.rotate(model, glm.radians(glfw.get_time() * 50), glm.vec3(0.5, 1.0, 0.0))
        modelLoc = glGetUniformLocation(shader_program, "model")
        glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm.value_ptr(model))

        glBindVertexArray(VAO)
        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

        glUseProgram(light_shader_program)
        modelLoc_light = glGetUniformLocation(light_shader_program, "model")
        viewLoc_light = glGetUniformLocation(light_shader_program, "view")
        projectionLoc_light = glGetUniformLocation(light_shader_program, "projection")
        glUniformMatrix4fv(viewLoc_light, 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(projectionLoc_light, 1, GL_FALSE, glm.value_ptr(projection))
        model_light = glm.mat4(1.0)
        model_light = glm.translate(model_light, lightPos)
        model_light = glm.scale(model_light, glm.vec3(0.1))
        glUniformMatrix4fv(modelLoc_light, 1, GL_FALSE, glm.value_ptr(model_light))

        glBindVertexArray(VAO_light)
        glDrawArrays(GL_TRIANGLES, 0, 3)
        glBindVertexArray(0)

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()
