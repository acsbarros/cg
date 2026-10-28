import math
import sys
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

# Variáveis globais de estado
r1, g1, b1 = 1.0, 1.0, 1.0
r2, g2, b2 = 1.0, 1.0, 1.0
r3, g3, b3 = 1.0, 1.0, 1.0
r4, g4, b4 = 0.0, 0.0, 0.0

tx1, ty1, tz1 = 0.0, 0.0, 0.0
rx1, ry1, rz1 = 0.0, 0.0, 0.0
sx1, sy1, sz1 = 1.0, 1.0, 1.0

tx3, ty3, tz3 = 0.0, 0.0, 0.0
rx3, ry3, rz3 = 0.0, 0.0, 0.0
sx3, sy3, sz3 = 1.0, 1.0, 1.0

activeV = 0
eixoX = 0
eixoY = 0

def error_callback(error, description):
    sys.stderr.write(f"Erro GLFW: {description.decode('utf-8')}\n")

def mouse_button_callback(window, button, action, mods):
    global r1, g1, b1, r2, g2, b2, r3, g3, b3, r4, g4, b4, activeV
    
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        xpos, ypos = glfw.get_cursor_pos(window)
        
        if activeV == 1:
            r1, g1, b1 = 1.0, 1.0, 1.0
        if activeV == 3:
            r3, g3, b3 = 1.0, 1.0, 1.0

        # Quadrante Superior Esquerdo (Triângulo)
        if 0 < xpos < 500 / 2.0:
            if 0 < ypos < 500 / 2.0:
                r1, g1, b1 = 0.0, 0.0, 0.0
                activeV = 1

        # Quadrante Superior Direito (Círculo)
        if 500 / 2.0 < xpos < 500:
            if 0 < ypos < 500 / 2.0:
                r2, g2, b2 = 0.0, 0.0, 0.0
                activeV = 2

        # Quadrante Inferior Esquerdo (Quadrado)
        if 0 < xpos < 500 / 2.0:
            if 500 / 2.0 < ypos < 500:
                r3, g3, b3 = 0.0, 0.0, 0.0
                activeV = 3

        # Quadrante Inferior Direito
        if 500 / 2.0 < xpos < 500:
            if 500 / 2.0 < ypos < 500:
                r4, g4, b4 = 0.0, 0.0, 0.0
                activeV = 4

def key_callback(window, key, scancode, action, mods):
    global rx1, rx3, sx1, sy1, sz1, sx3, sy3, sz3, ty1, ty3, tx1, tx3, eixoX
    
    if action == glfw.PRESS and key == glfw.KEY_RIGHT:
        if activeV == 1:
            rx1 += 10
            eixoX = 1
        elif activeV == 3:
            rx3 += 10
            eixoX = 1
            
    if action == glfw.PRESS and key == glfw.KEY_LEFT:
        if activeV == 1:
            rx1 -= 10
            eixoX = 1
        elif activeV == 3:
            rx3 -= 10
            eixoX = 1
            
    if action == glfw.PRESS and key == glfw.KEY_UP:
        if activeV == 1:
            sx1 += 0.1; sy1 += 0.1; sz1 += 0.1
        elif activeV == 3:
            sx3 += 0.1; sy3 += 0.1; sz3 += 0.1
            
    if action == glfw.PRESS and key == glfw.KEY_DOWN:
        if activeV == 1:
            sx1 -= 0.1; sy1 -= 0.1; sz1 -= 0.1
        elif activeV == 3:
            sx3 -= 0.1; sy3 -= 0.1; sz3 -= 0.1
            
    if action == glfw.PRESS:
        if key == glfw.KEY_W:
            if activeV == 1: ty1 += 0.1
            elif activeV == 3: ty3 += 0.1
        elif key == glfw.KEY_S:
            if activeV == 1: ty1 -= 0.1
            elif activeV == 3: ty3 -= 0.1
        elif key == glfw.KEY_A:
            if activeV == 1: tx1 -= 0.1
            elif activeV == 3: tx3 -= 0.1
        elif key == glfw.KEY_D:
            if activeV == 1: tx1 += 0.1
            elif activeV == 3: tx3 += 0.1

def main():
    glfw.set_error_callback(error_callback)
    if not glfw.init():
        sys.exit(1)
        
    window = glfw.create_window(500, 500, "Trabalho 01", None, None)
    if not window:
        glfw.terminate()
        sys.exit(1)
        
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    glfw.set_key_callback(window, key_callback)
    glfw.set_input_mode(window, glfw.STICKY_KEYS, glfw.TRUE)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    
    while not glfw.window_should_close(window):
        width, height = glfw.get_framebuffer_size(window)
        
        glShadeModel(GL_FLAT)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # --- Viewport 1 (Superior Esquerdo) - Triângulo ---
        glViewport(0, width // 2, width // 2, width // 2)
        glScissor(0, width // 2, width // 2, width // 2)
        glEnable(GL_SCISSOR_TEST)
        glClearColor(r1, g1, b1, 0)
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        
        glPushMatrix()
        if activeV == 1:
            glRotated(rx1, 0, 0, 1)
            glScaled(sx1, sy1, sz1)
            glTranslated(tx1, ty1, tz1)
        glBegin(GL_LINE_LOOP)
        glColor3f(0.0, 1.0, 1.0)
        glVertex3f(-0.6, -0.4, 0.0)
        glVertex3f(0.6, -0.4, 0.0)
        glVertex3f(0.0, 0.6, 0.0)
        glEnd()
        glPopMatrix()

        # --- Viewport 2 (Superior Direito) - Círculo ---
        glViewport(width // 2, height // 2, width // 2, height // 2)
        glScissor(width // 2, height // 2, width // 2, height // 2)
        glEnable(GL_SCISSOR_TEST)
        glClearColor(r2, g2, b2, 0)
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        
        glPushMatrix()
        glBegin(GL_LINE_LOOP)
        glColor3f(0.0, 1.0, 0.0)
        for ii in range(100):
            theta = 2.0 * 3.1415926 * float(ii) / float(100)
            x = 0.5 * math.cos(theta)
            y = 0.5 * math.sin(theta)
            glVertex2f(x, y)
        glEnd()
        glPopMatrix()

        # --- Viewport 3 (Inferior Esquerdo) - Quadrado ---
        glViewport(0, 0, width // 2, height // 2)
        glScissor(0, 0, width // 2, height // 2)
        glEnable(GL_SCISSOR_TEST)
        glClearColor(r3, g3, b3, 0)
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        
        glPushMatrix()
        if activeV == 3:
            glRotated(rx3, 0, 0, 1)
            glScaled(sx3, sy3, sz3)
            glTranslated(tx3, ty3, 0.0)
        glColor3f(1.0, 1.0, 0.0)
        glBegin(GL_LINE_LOOP)
        glVertex3f(-0.5, -0.5, 0)
        glVertex3f(-0.5, 0.5, 0)
        glVertex3f(0.5, 0.5, 0)
        glVertex3f(0.5, -0.5, 0)
        glEnd()
        glPopMatrix()

        # --- Viewport 4 (Inferior Direito) ---
        glViewport(width // 2, 0, width // 2, height // 2)
        glScissor(width // 2, 0, width // 2, height // 2)
        glEnable(GL_SCISSOR_TEST)
        glClearColor(0, 0, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        if width <= height:
            gluOrtho2D(0.0, 500.0, 0.0, 500.0 * height / float(width))
        else:
            gluOrtho2D(0.0, 500.0 * width / float(height), 0.0, 500.0)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.destroy_window(window)
    glfw.terminate()
    sys.exit(0)

if __name__ == "__main__":
    main()