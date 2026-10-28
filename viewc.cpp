#include <iostream>
#include <glfw3.h>
#include <GL/glut.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <string>

using namespace std;

void drawText(const char* text, int length, int x, int y) {

    glLoadIdentity();
    glColor3f(0.5f, 0.5f, 0.5f);     //<-- this line controls the color (now text is gray)
    glTranslatef(0.0f, 0.0f, -5.0f);
    glRasterPos2i(x, y);
    for (int i = 0; i < length; i++) {
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, (int)text[i]);
    }


}
#define FONTE GLUT_BITMAP_9_BY_15


static void error_callback(int error, const char* description)
{
    fputs(description, stderr);
}

GLfloat vetor[4][3];
GLfloat r1 = 1.0;
GLfloat g1 = 1.0;
GLfloat b1 = 1.0;

GLfloat tx1 = 0.0;
GLfloat ty1 = 0.0;
GLfloat tz1 = 0.0;

GLfloat rx1 = 0.0;
GLfloat ry1 = 0.0;
GLfloat rz1 = 0.0;

GLfloat sx1 = 1.0;
GLfloat sy1 = 1.0;
GLfloat sz1 = 1.0;



GLfloat tx3 = 0.0;
GLfloat ty3 = 0.0;
GLfloat tz3 = 0.0;

GLfloat rx3 = 0.0;
GLfloat ry3 = 0.0;
GLfloat rz3 = 0.0;

GLfloat sx3 = 1.0;
GLfloat sy3 = 1.0;
GLfloat sz3 = 1.0;


GLfloat r2 = 1.0;
GLfloat g2 = 1.0;
GLfloat b2 = 1.0;

GLfloat r3 = 1.0;
GLfloat g3 = 1.0;
GLfloat b3 = 1.0;


GLfloat r4 = 0.0;
GLfloat g4 = 0.0;
GLfloat b4 = 0.0;

int activeV = 0;
int onoff = 0;
int eixoX = 0;//1-x,2-y,3-z
int eixoY = 0;//1-x,2-y,3-z

static void mouse_button_callback(GLFWwindow* window, int button, int action, int mods)
{
    /*if (button == GLFW_MOUSE_BUTTON_RIGHT && action == GLFW_PRESS)
        cout << "GLFW_MOUSE_BUTTON_RIGHT";*/

    if (button == GLFW_MOUSE_BUTTON_LEFT && action == GLFW_PRESS) {
        //  cout << "GLFW_MOUSE_BUTTON_LEFT";
        double xpos, ypos;
        //getting cursor position
        glfwGetCursorPos(window, &xpos, &ypos);

        if (activeV == 1) {
            r1 = 1.0;
            g1 = 1.0;
            b1 = 1.0;
        }
        if (activeV == 3) {
            r3 = 1.0;
            g3 = 1.0;
            b3 = 1.0;
        }

        if (xpos > 0 && xpos < (float)500 / 2.0)
        {
            if (ypos > 0 && ypos < 500 / 2)
            {
                //cout << "v-1";                          
                r1 = 0.0;
                g1 = 0.0;
                b1 = 0.0;
                activeV = 1;
            }
        }

        if ((xpos > 500 / 2) && (xpos < 500))
        {
            if ((ypos > 0 / 2) && (ypos < 500 / 2)) {
                //cout << "v-2";
                r2 = 0.0;
                g2 = 0.0;
                b2 = 0.0;
                activeV = 2;
            }

        }

        if ((xpos > 0) && (xpos < 500 / 2))
        {
            if ((ypos > 500 / 2) && ypos < 500)
            {
                // cout << "v-3";
                r3 = 0.0;
                g3 = 0.0;
                b3 = 0.0;
                activeV = 3;
            }
        }
        if ((xpos > 500 / 2) && xpos < 500)
        {
            if ((ypos > 500 / 2) && ypos < 500)
            {
                // cout << "v-4";
                r4 = 0.0;
                g4 = 0.0;
                b4 = 0.0;
                activeV = 4;
            }
        }
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


    /*  if (button == GLFW_MOUSE_BUTTON_MIDDLE && action == GLFW_PRESS)
          cout << "GLFW_MOUSE_BUTTON_MIDDLE";*/
          //cout << key;    
    if (action == GLFW_PRESS && key == GLFW_KEY_RIGHT) {
        //glfwSetWindowShouldClose(window, GL_TRUE);   
        if (activeV == 1) {
            rx1 += 10;
            eixoX = 1;
        }
        if (activeV == 3) {
            rx3 += 10;
            eixoX = 1;
        }
    }
    if (action == GLFW_PRESS && key == GLFW_KEY_LEFT) {
        if (activeV == 1) {
            rx1 -= 10;
            eixoX = 1;
        }
        if (activeV == 3) {
            rx3 -= 10;
            eixoX = 1;
        }
    }

    if (action == GLFW_PRESS && key == GLFW_KEY_UP) {
        if (activeV == 1) {
            sx1 += 0.1;
            sy1 += 0.1;
            sz1 += 0.1;
        }
        if (activeV == 3) {
            sx3 += 0.1;
            sy3 += 0.1;
            sz3 += 0.1;
        }
    }
    if (action == GLFW_PRESS && key == GLFW_KEY_DOWN) {
        if (activeV == 1) {
            sx1 -= 0.1;
            sy1 -= 0.1;
            sz1 -= 0.1;
        }
        if (activeV == 3) {
            sx3 -= 0.1;
            sy3 -= 0.1;
            sz3 -= 0.1;
        }
    }
    if (action == GLFW_PRESS && key == GLFW_KEY_W) {

        if (activeV == 1) {
            ty1 += 0.1;
        }
        if (activeV == 3) {
            ty3 += 0.1;
        }
    }
    if (action == GLFW_PRESS && key == GLFW_KEY_S) {
        if (activeV == 1) {
            ty1 -= 0.1;
        }
        if (activeV == 3) {
            ty3 -= 0.1;
        }
    }
    if (action == GLFW_PRESS && key == GLFW_KEY_A) {
        if (activeV == 1) {
            tx1 -= 0.1;
        }
        if (activeV == 3) {
            tx3 -= 0.1;
        }
    }
    if (action == GLFW_PRESS && key == GLFW_KEY_D) {
        if (activeV == 1) {
            tx1 += 0.1;
        }
        if (activeV == 3) {
            tx3 += 0.1;
        }
    }
}

int main(int argc, char** argv)
{
    GLFWwindow* window;
    glfwSetErrorCallback(error_callback);
    if (!glfwInit())
        exit(EXIT_FAILURE);
    // window = glfwCreateWindow(640, 480, "Simple example", NULL, NULL);
    window = glfwCreateWindow(500, 500, "Trabalho 01", NULL, NULL);
    if (!window)
    {
        glfwTerminate();

        exit(EXIT_FAILURE);
    }
    glfwMakeContextCurrent(window);
    glfwSwapInterval(1);
    glfwSetKeyCallback(window, key_callback);
    glfwSetInputMode(window, GLFW_STICKY_KEYS, 1);
    //  glfwSetCursorEnterCallback(window, cursor_enter_callback);
    glfwSetMouseButtonCallback(window, mouse_button_callback);
    // glfwSetCursorPosCallback(window, mouse_button_callback);

     //printf("%s", glGetString(GL_VERSION));
    glutInit(&argc, argv);

    while (!glfwWindowShouldClose(window))
    {
        float ratio;
        int width, height;

        glfwGetFramebufferSize(window, &width, &height);
        ratio = width / (float)height;

        glShadeModel(GL_FLAT);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);


        // X,0
        // 0,0
        glViewport(0, width / 2, width / 2, width / 2);
        glScissor(0, width / 2, width / 2, width / 2);
        glEnable(GL_SCISSOR_TEST);
        glClearColor(r1, g1, b1, 0);
        glClear(GL_COLOR_BUFFER_BIT);
        glLoadIdentity();
        //triangulo
        glPushMatrix();
        if (activeV == 1) {
            glRotated(rx1, 0, 0, 1);
            glScaled(sx1, sy1, sz1);
            glTranslated(tx1, ty1, tz1);
        }
        glBegin(GL_LINE_LOOP);
        glColor3f(0.f, 1.f, 1.f);
        glVertex3f(-0.6f, -0.4f, 0.f);
        glVertex3f(0.6f, -0.4f, 0.f);
        glVertex3f(0.f, 0.6f, 0.f);
        glEnd();
        glPopMatrix();



    
        // 0,X
            // 0,0
        glViewport(width / 2, height / 2, width / 2, height / 2);
        glScissor(width / 2, height / 2, width / 2, height / 2);
        glEnable(GL_SCISSOR_TEST);
        glClearColor(r2, g2, b2, 0);
        glClear(GL_COLOR_BUFFER_BIT);
        glLoadIdentity();
        glPushMatrix();
        if (activeV == 2) {

        }
        //circulo
        glBegin(GL_LINE_LOOP);
        glColor3f(0.f, 1.f, 0.f);
        for (int ii = 0; ii < 100; ii++) {
            float theta = 2.0f * 3.1415926f * float(ii) / float(100);//get the current angle 
            float x = 0.5 * cosf(theta);//calculate the x component 
            float y = 0.5 * sinf(theta);//calculate the y component 
            glVertex2f(x + 0, y + 0);//output vertex 
        }
        glEnd();
        glPopMatrix();


        // 0,0
        // X,0
        glViewport(0, 0, width / 2, height / 2);
        glScissor(0, 0, width / 2, height / 2);
        glEnable(GL_SCISSOR_TEST);
        glClearColor(r3, g3, b3, 0);
        glClear(GL_COLOR_BUFFER_BIT);
        glLoadIdentity();
        glPushMatrix();
        if (activeV == 3) {
            glRotated(rx3, 0, 0, 1);
            glScaled(sx3, sy3, sz3);
            glTranslated(tx3, ty3, 0.0);
        }
        glColor3f(1.f, 1.f, 0.f);
        //quadrado
        glBegin(GL_LINE_LOOP);
        glVertex3f(-0.5, -0.5, 0);
        glVertex3f(-0.5f, 0.5, 0);
        glVertex3f(0.5, 0.5, 0);
        glVertex3f(0.5f, -0.5, 0);
        glEnd();
        glPopMatrix();



    // 0,0
    // 0,X        
    glViewport(width / 2, 0, width / 2, height / 2);
    glScissor(width / 2, 0, width / 2, height / 2);
    glEnable(GL_SCISSOR_TEST);
    glClearColor(0, 0, 0, 0);
    glClear(GL_COLOR_BUFFER_BIT);
    glLoadIdentity();
    glColor3f(1.f, 0.f, 0.f);
    //titulo
    glRasterPos2f(-0.3, 0.9);
    glutBitmapWidth(FONTE, '18');
    glutBitmapCharacter(FONTE, 'C');
    glutBitmapCharacter(FONTE, 'O');
    glutBitmapCharacter(FONTE, 'M');
    glutBitmapCharacter(FONTE, 'P');
    glutBitmapCharacter(FONTE, '.');
    glutBitmapCharacter(FONTE, 'G');
    glRasterPos2f(-0.3, 0.8);
    glutBitmapCharacter(FONTE, 'B');
    glutBitmapCharacter(FONTE, 'A');
    glutBitmapCharacter(FONTE, 'R');
    glutBitmapCharacter(FONTE, 'R');
    glutBitmapCharacter(FONTE, 'O');
    glutBitmapCharacter(FONTE, 'S');
    glRasterPos2f(-0.3, 0.7);
    glutBitmapCharacter(FONTE, 'U');
    glutBitmapCharacter(FONTE, 'N');
    glutBitmapCharacter(FONTE, 'I');
    glutBitmapCharacter(FONTE, 'L');
    glutBitmapCharacter(FONTE, 'A');
    glutBitmapCharacter(FONTE, 'B');


    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();

    if (width <= height)
        gluOrtho2D(0.0f, 500.0f, 0.0f, 500.0f * height / (float)width);
    else
        gluOrtho2D(0.0f, 500.0f * width / (float)height, 0.0f, 500.0f);



    glfwSwapBuffers(window);
    glfwPollEvents();
    }
glfwDestroyWindow(window);

glfwTerminate();
exit(EXIT_SUCCESS);
}