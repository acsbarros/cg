# 🎨 Computação Gráfica com OpenGL Moderno (Python)

[![Disciplina](https://img.shields.io/badge/Disciplina-Computação%20Gráfica-blue)](https://github.com)
[![OpenGL](https://img.shields.io/badge/OpenGL-Modern-green)](https://www.opengl.org/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-yellow)](https://www.python.org/)
[![GLFW](https://img.shields.io/badge/GLFW-3.3-orange)](https://www.glfw.org/)

> **Prof. Carlos Barros**  
> **UNILAB - Universidade da Integração Internacional da Lusofonia Afro-Brasileira**  
> **Curso: Engenharia de Computação**

---

## 📌 Sobre o Projeto

Este repositório contém o material de apoio para a disciplina de **Computação Gráfica**, focado no desenvolvimento com **OpenGL Moderno** utilizando a linguagem **Python** e a biblioteca **GLFW**.  
A proposta é construir um ambiente de desenvolvimento eficiente e explorar os conceitos fundamentais da computação gráfica moderna.

---

## 🚀 Configuração do Ambiente de Desenvolvimento

Siga os passos abaixo para configurar seu ambiente Python com todas as dependências necessárias.

### 1️⃣ Instalar Python e pip (Linux)

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 2️⃣ Criar um ambiente virtual

```bash
python3 -m venv myenv
```

### 3️⃣ Ativar o ambiente virtual

```bash
source myenv/bin/activate
```

### 4️⃣ Desativar o ambiente virtual (quando necessário)

```bash
deactivate
```

### 5️⃣ Instalar as bibliotecas necessárias

```bash
pip install numpy pyopengl glfw scipy pyglm pillow requests ipython PyOpenGL-accelerate
```

### 6️⃣ Caso tenha um arquivo requirements.txt

```bash
pip install -r requirements.txt
```

### 7️⃣ Salvar as dependências

```bash
pip freeze > requirements.txt
```

### 🧠 Estrutura do Projeto

```bash
.
├── main.py                # Código principal do projeto
├── requirements.txt       # Dependências do projeto
├── myenv/                 # Ambiente virtual (ignorado no repositório)
└── README.md              # Este arquivo

```

### 🧪 Criar o arquivo main.py

```bash
touch main.py
```

### 8️⃣ Editar o arquivo

```bash
nano main.py
```


### 9️⃣ Inserir o código fonte no main.py

Utilize seu editor de preferência para adicionar o código OpenGL/GLFW.

### 🔟 Executar o programa

```bash
python main.py
```

### 🔁 Melhorando o Projeto

Após executar e testar o programa, você pode:
Refatorar o código
Adicionar novos shaders
Implementar transformações geométricas
Trabalhar com texturas e iluminação

### 💡 A disciplina incentiva a experimentação e a evolução contínua do projeto!


### 📚 Referências
OpenGL Documentation
GLFW Documentation
PyOpenGL
Learn OpenGL (Modern)

### 👨‍🏫 Professor
Carlos Barros
Engenharia de Computação — UNILAB

### 📄 Licença

Este material é de uso acadêmico e está disponível para os alunos da disciplina.

### 🧠 Estrutura do Projeto

```bash
.
├── main.py                # Código principal do projeto
├── requirements.txt       # Dependências do projeto
├── shaders/               # Diretório para shaders (opcional)
│   ├── vertex_shader.glsl
│   └── fragment_shader.glsl
├── textures/              # Diretório para texturas (opcional)
├── myenv/                 # Ambiente virtual (ignorado no repositório)
└── README.md              # Este arquivo
```

### 💻 Exemplo Mínimo de Código OpenGL com GLFW

```python
import glfw
from OpenGL.GL import *
import numpy as np
import sys

def main():
    # Inicializar GLFW
    if not glfw.init():
        sys.exit("Falha ao inicializar GLFW")
    
    # Configurar a janela
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    
    # Criar janela
    window = glfw.create_window(800, 600, "OpenGL Moderno - UNILAB", None, None)
    if not window:
        glfw.terminate()
        sys.exit("Falha ao criar janela")
    
    glfw.make_context_current(window)
    
    # Definir dados do triângulo
    vertices = np.array([
        -0.5, -0.5, 0.0,  # Vértice 1
         0.5, -0.5, 0.0,  # Vértice 2
         0.0,  0.5, 0.0   # Vértice 3
    ], dtype=np.float32)
    
    cores = np.array([
        1.0, 0.0, 0.0,  # Vermelho
        0.0, 1.0, 0.0,  # Verde
        0.0, 0.0, 1.0   # Azul
    ], dtype=np.float32)
    
    # Criar Vertex Array Object (VAO)
    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)
    
    # Criar Vertex Buffer Object (VBO) para vértices
    VBO_vertices = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO_vertices)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), None)
    glEnableVertexAttribArray(0)
    
    # Criar VBO para cores
    VBO_cores = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO_cores)
    glBufferData(GL_ARRAY_BUFFER, cores.nbytes, cores, GL_STATIC_DRAW)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), None)
    glEnableVertexAttribArray(1)
    
    # Loop principal
    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Desenhar triângulo
        glBindVertexArray(VAO)
        glDrawArrays(GL_TRIANGLES, 0, 3)
        
        glfw.swap_buffers(window)
        glfw.poll_events()
    
    # Limpar recursos
    glDeleteVertexArrays(1, [VAO])
    glDeleteBuffers(1, [VBO_vertices])
    glDeleteBuffers(1, [VBO_cores])
    glfw.terminate()

if __name__ == "__main__":
    main()
```

### 🎨 Entendendo os Shaders

Os shaders são pequenos programas executados na GPU que controlam o pipeline gráfico. No OpenGL Moderno, os dois shaders mais importantes são:

#### Vertex Shader (vertex_shader.glsl)

Responsável por processar cada vértice individualmente:

```glsl
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;

out vec3 ourColor;

void main() {
    gl_Position = vec4(aPos, 1.0);
    ourColor = aColor;
}
```

#### Fragment Shader (fragment_shader.glsl)

Define a cor final de cada pixel (fragmento):

```glsl
#version 330 core
in vec3 ourColor;
out vec4 FragColor;

void main() {
    FragColor = vec4(ourColor, 1.0);
}
```

#### Como Compilar Shaders em Python

```python
def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    
    # Verificar erros de compilação
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        error = glGetShaderInfoLog(shader).decode()
        print(f"Erro no shader: {error}")
        return None
    
    return shader

def create_program(vertex_source, fragment_source):
    vertex_shader = compile_shader(vertex_source, GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment_source, GL_FRAGMENT_SHADER)
    
    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)
    
    # Verificar erros de linkagem
    if not glGetProgramiv(program, GL_LINK_STATUS):
        error = glGetProgramInfoLog(program).decode()
        print(f"Erro ao linkar programa: {error}")
        return None
    
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)
    
    return program
```

#### 🔧 Transformações Geométricas

As transformações são essenciais para criar animações e movimentar objetos na cena:

```python

import numpy as np

def create_translation_matrix(tx, ty, tz):
    """Cria matriz de translação"""
    return np.array([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1]
    ], dtype=np.float32)

def create_rotation_matrix(angle, axis):
    """Cria matriz de rotação (angle em radianos)"""
    c = np.cos(angle)
    s = np.sin(angle)
    
    if axis == 'x':
        return np.array([
            [1, 0, 0, 0],
            [0, c, -s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
    elif axis == 'y':
        return np.array([
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
    elif axis == 'z':
        return np.array([
            [c, -s, 0, 0],
            [s, c, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

def create_scale_matrix(sx, sy, sz):
    """Cria matriz de escala"""
    return np.array([
        [sx, 0, 0, 0],
        [0, sy, 0, 0],
        [0, 0, sz, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)
```

#### 🖼️ Trabalhando com Texturas

```python
from PIL import Image

def load_texture(filepath):
    """Carrega uma textura de arquivo e retorna o ID da textura OpenGL"""
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    
    # Configurar parâmetros da textura
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    # Carregar imagem com PIL
    img = Image.open(filepath)
    img = img.transpose(Image.FLIP_TOP_BOTTOM)  # Inverter eixo Y
    img_data = np.array(img, dtype=np.uint8)
    
    # Enviar dados para GPU
    if img.mode == 'RGB':
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.width, img.height, 
                     0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    elif img.mode == 'RGBA':
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 
                     0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    
    glGenerateMipmap(GL_TEXTURE_2D)
    
    return texture
```

#### 💡Iluminação e Materiais

Para criar efeitos de iluminação realistas, é necessário implementar os modelos de iluminação:

##### Componentes da Iluminação

```glsl
// Vertex Shader com iluminação básica
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 FragPos;
out vec3 Normal;

void main() {
    FragPos = vec3(model * vec4(aPos, 1.0));
    Normal = mat3(transpose(inverse(model))) * aNormal;
    gl_Position = projection * view * vec4(FragPos, 1.0);
}
```

```glsl
// Fragment Shader com iluminação Phong
#version 330 core
in vec3 FragPos;
in vec3 Normal;

out vec4 FragColor;

uniform vec3 lightPos;
uniform vec3 lightColor;
uniform vec3 objectColor;
uniform vec3 viewPos;

void main() {
    // Componente ambiente
    float ambientStrength = 0.1;
    vec3 ambient = ambientStrength * lightColor;
    
    // Componente difusa
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;
    
    // Componente especular
    float specularStrength = 0.5;
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = specularStrength * spec * lightColor;
    
    vec3 result = (ambient + diffuse + specular) * objectColor;
    FragColor = vec4(result, 1.0);
}
```

### 🧪Executando o Projeto

```bash
python main.py
```
