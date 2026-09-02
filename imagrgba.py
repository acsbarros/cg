from PIL import Image

# Converte de RGB para RGBA
img = Image.open('ss.jpg').convert('RGBA')
pixels = img.load()
data = img.getdata()
print(type(data[0]))  # Exibe o primeiro pixel (R, G, B, A)
print(type(pixels[0, 0]))  # Exibe o pixel na posição (0, 0)




# Acessa a tupla (R, G, B, A)
#x, y = 10, 20
#r, g, b, a = pixels[x, y]

# Altera o pixel para 50% de transparência (Alpha = 128)
#pixels[x, y] = (r, g, b, 128)

# Salva obrigatoriamente em um formato que suporte transparência (ex: PNG)
#img.save('imagem_transparente.png')