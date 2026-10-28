#include <iostream>
#include <Windows.h>
#include <glfw3.h>
#include <GL/glut.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <string>

using namespace std;

#define FONTE GLUT_BITMAP_9_BY_15

float ANGULO_INICIAL_BRACO = 0.0f;
float ANGULO_FINAL_BRACO = -33.0f;
float ORDENADA_INICIAL_BLOCO = -9.0f;
float ORDENADA_FINAL_BLOCO = -20.0f;

double angle, fAspect;
double eyex, eyey, eyez;
float orbitDegreesX, orbitDegreesY, orbitDegreesZ;

float angleBraco = ANGULO_INICIAL_BRACO;
float speedRotacao = -0.5f;
float eixoBloco = ORDENADA_INICIAL_BLOCO;
float speedQueda = -0.5f;



static void error_callback(int error, const char* description)
{
    fputs(description, stderr);
}


static void mouse_button_callback(GLFWwindow* window, int button, int action, int mods)
{
    /*if (button == GLFW_MOUSE_BUTTON_RIGHT && action == GLFW_PRESS)
        cout << "GLFW_MOUSE_BUTTON_RIGHT";*/

    if (button == GLFW_MOUSE_BUTTON_LEFT && action == GLFW_PRESS) {
        //  cout << "GLFW_MOUSE_BUTTON_LEFT";
        double xpos, ypos;
        //getting cursor position
        glfwGetCursorPos(window, &xpos, &ypos);
    }

    if (button == GLFW_MOUSE_BUTTON_1 && action == GLFW_PRESS) {
        if (angle >= 4) angle -= 4;
    }
    if (button == GLFW_MOUSE_BUTTON_3 && action == GLFW_PRESS) {
        if (angle <= 72) angle += 4;
    }
}
void cursor_enter_callback(GLFWwindow* window, int entered)
{
    if (entered)
    {
        // The cursor entered the content area of the window
        cout << "entrou";
    }
    else
    {
        // The cursor left the content area of the window
        cout << "deixou";
    }
}
static void key_callback(GLFWwindow* window, int key, int scancode, int action, int mods)
{
    if (action == GLFW_PRESS && key == GLFW_KEY_RIGHT) {
        cout << "GLFW_KEY_RIGHT";
        orbitDegreesX += 5;
        if (orbitDegreesX > 360)
            orbitDegreesX -= 360.0;
    }
    if (action == GLFW_PRESS && key == GLFW_KEY_LEFT) {
        cout << "GLFW_KEY_LEFT";
        orbitDegreesX -= 5;
        if (orbitDegreesX > 360)
            orbitDegreesX -= 360.0;
        
    }

    if (action == GLFW_PRESS && key == GLFW_KEY_UP) {
        cout << "GLFW_KEY_UP";
        orbitDegreesY += 5;
        if (orbitDegreesY > 360)
            orbitDegreesY -= 360.0;
        
    }
    if (action == GLFW_PRESS && key == GLFW_KEY_DOWN) {
        cout << "GLFW_KEY_DOWN";
        orbitDegreesY -= 5;
        if (orbitDegreesY > 360)
            orbitDegreesY -= 360.0;
        
    }
    if (action == GLFW_PRESS && key == GLFW_KEY_W) {

        cout << "GLFW_KEY_W";
        orbitDegreesX = 0;
        orbitDegreesY = 0;
        orbitDegreesZ = 0;
        eyex = 0;
        eyey = 80;
        eyez = 200;

        
    }
    if (action == GLFW_PRESS && key == GLFW_KEY_S) {

        
    }
    if (action == GLFW_PRESS && key == GLFW_KEY_A) {
        orbitDegreesZ += 5;
        if (orbitDegreesZ > 360)
            orbitDegreesZ -= 360.0;
        
    }
    if (action == GLFW_PRESS && key == GLFW_KEY_D) {
        orbitDegreesZ -= 5;
        if (orbitDegreesZ > 360)
            orbitDegreesZ -= 360.0;
        
    }
}

void init()
{
    glClearColor(1.0f, 1.0f, 1.0f, 1.0f);
    glClearColor(0, 0, 0, 1);
   // glEnable(GL_LIGHTING);
   // glEnable(GL_LIGHT0);
   // glEnable(GL_COLOR_MATERIAL);
    glEnable(GL_DEPTH_TEST);
   // glEnable(GL_NORMALIZE);
   // glEnable(GL_DEPTH_TEST);
}
void desenhaChao()
{
    glColor3f(1, 0, 1);
    glLineWidth(1);
    glBegin(GL_LINES);
    for (float z = -100; z <= 100; z += 10)
    {
        glVertex3f(-100, -0.1f, z);
        glVertex3f(100, -0.1f, z);
    }
    for (float x = -100; x <= 100; x += 10)
    {
        glVertex3f(x, -0.1f, -100);
        glVertex3f(x, -0.1f, 100);
    }
    glEnd();
}
void desenhaBloco()
{
    glPushMatrix();
    glColor3f(1, 0, 1);
    glTranslated(25.0f, eixoBloco, 40.0f);
    glutSolidCube(2.0f);
    glPopMatrix();
}

void desenhaBraco()
{
    glLineWidth(5);
    glBegin(GL_LINES);
    glColor3f(1, 0, 0);
    glVertex3f(0.0f, 0.0f, 0.0f);
    glVertex3f(25.0f, 0.0f, 40.0f);
    glEnd();

    glLineWidth(5);
    glBegin(GL_LINES);
    glColor3f(1, 128 / 255, 128 / 255);
    glVertex3f(25.0f, 0, 40.0f);
    glVertex3f(25.0f, -9, 40.0f);

    glEnd();
}

void desenhaCilindro()
{
    glPushMatrix();
    glColor3f(0, 1, 1);
    glTranslated(-26, 10, 7);
    glRotatef(90, 1, 0, 0);
    glutSolidCube(2.0f);
    //glutSolidCylinder(2.0f, 10, 32, 12);
    glPopMatrix();
}

void desenhaMesa()
{
    glBegin(GL_QUADS);
    glColor3f(0, 0, 1);
    glVertex3f(-10, 20, -10);//p1
    glVertex3f(10, 20, -10);//p2
    glVertex3f(10, 20, 10);//p3
    glVertex3f(-10, 20, 10);//p4
    glEnd();

    glLineWidth(2);
    glBegin(GL_LINES);
    glColor3f(0, 0, 1);
    glVertex3f(-10, 20, -10);
    glVertex3f(-10, 0, -10);
    glVertex3f(10, 20, -10);
    glVertex3f(10, 0, -10);
    glVertex3f(10, 20, 10);
    glVertex3f(10, 0, 10);
    glVertex3f(-10, 20, 10);
    glVertex3f(-10, 0, 10);
    glEnd();
}

void posicionaObservador()
{
    // Especifica sistema de coordenadas do modelo
    glMatrixMode(GL_MODELVIEW);
    // Inicializa sistema de coordenadas do modelo
    glLoadIdentity();
    // Especifica posição do observador e do alvo
    gluLookAt(eyex, eyey, eyez, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0);
}

void especificaParametrosVisualizacao()
{
    // Especifica sistema de coordenadas de projeção
    glMatrixMode(GL_PROJECTION);
    // Inicializa sistema de coordenadas de projeção
    glLoadIdentity();
    // Especifica a projeção perspectiva(angulo,aspecto,zMin,zMax)
    gluPerspective(angle, fAspect, 0.5, 500);
    posicionaObservador();
}

void resize(int w,int h) {

    if (h == 0) h = 1;

    glViewport(0, 0, w, h);
    fAspect = (float)w / (float)h;
}

int main(int argc, char** argv)
{
    GLFWwindow* window;
    glfwSetErrorCallback(error_callback);
    if (!glfwInit())
        exit(EXIT_FAILURE);
    // window = glfwCreateWindow(640, 480, "Simple example", NULL, NULL);
    window = glfwCreateWindow(640, 480, "cenario", NULL, NULL);
    if (!window)
    {
        glfwTerminate();

        exit(EXIT_FAILURE);
    }
    glfwMakeContextCurrent(window);
    glfwSwapInterval(1);
    glfwSetKeyCallback(window, key_callback);
    glfwSetInputMode(window, GLFW_STICKY_KEYS, 1);
    //glfwSetCursorEnterCallback(window, cursor_enter_callback);
    glfwSetMouseButtonCallback(window, mouse_button_callback);
    //glfwSetCursorPosCallback(window, mouse_button_callback);

    glutInit(&argc, argv);
    angle = 45;
    fAspect = 1;
    eyex = 0;
    eyey = 10;
    eyez = 200;
    orbitDegreesX = 0;
    orbitDegreesY = 0;
    orbitDegreesZ = 0;
    init();

    while (!glfwWindowShouldClose(window))
    {
        float ratio;
        int width, height;

        glfwGetFramebufferSize(window, &width, &height);
        ratio = width / (float)height;

       // glShadeModel(GL_FLAT);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        glMatrixMode(GL_PROJECTION);
        glLoadIdentity();
        resize(width, height);


        especificaParametrosVisualizacao();
        glTranslatef(0, -28, 0);
        desenhaChao();
        desenhaChao();
        desenhaMesa();
        desenhaCilindro();
        glTranslatef(-25.0f, 30.0f, -40.0f);

       // glRotated(angleBraco, 0.0f, 1.0f, 0.0f);
        desenhaBloco();
        desenhaBraco();

        /*if (angleBraco != ANGULO_FINAL_BRACO) {
            angleBraco += speedRotacao;
        }
        else {
            if (eixoBloco != ORDENADA_FINAL_BLOCO) {
                eixoBloco += speedQueda;
            }
            else {
                angleBraco = ANGULO_INICIAL_BRACO;
                eixoBloco = ORDENADA_INICIAL_BLOCO;
            }
        }*/

       
    glfwSwapBuffers(window);
    glfwPollEvents();
    }
glfwDestroyWindow(window);

glfwTerminate();
exit(EXIT_SUCCESS);
}