"""Tons de cinza"""
from io import BytesIO
from PIL import Image
import requests
from IPython.display import display
#URL_IMAGEM = 'http://imagens.usp.br/wp-content/uploads/13072012frutasfotoMarcosSantos008.jpg'
#response = requests.get(URL_IMAGEM)

#img = Image.open(BytesIO(response.content))
img = Image.open('ss.jpg')
largura = img.size[0]
altura = img.size[1]
print(largura)
print(altura)

matrix_pixeis = img.load()

for i in range(largura):
    for j in range(altura):
        pixel = matrix_pixeis[i, j]
        if i == 0 and j ==0:
            print(type(pixel))
            print(pixel)

        R = pixel[0]
        G = pixel[1]
        B = pixel[2]
        R_F = float(R)
        B_F = float(B)
        G_F = float(G)
        #M = (R+G+B)//3
        M_F = R_F*0.3+G_F*0.59+B_F*0.11
        M_I = int(M_F)
        #M = (R+G+B)//3
        novo_pixel = (M_I,M_I,M_I,20)
        matrix_pixeis[i, j] = novo_pixel


img.show()

