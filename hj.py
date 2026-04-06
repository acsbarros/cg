import glfw
from OpenGL.GL import *
import imgui
from imgui.integrations.glfw import GlfwRenderer

def main():
    # Inicializar GLFW
    if not glfw.init():
        return

    # Configurar a janela
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

    window = glfw.create_window(800, 600, "GLFW + ImGui", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    # Inicializar ImGui
    imgui.create_context()
    impl = GlfwRenderer(window)

    show_button_clicked = False  # Variável para o botão

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        # Limpar a tela
        glClearColor(0.2, 0.2, 0.2, 1)
        glClear(GL_COLOR_BUFFER_BIT)

        # Iniciar uma nova frame do ImGui
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
