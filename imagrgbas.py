import cv2
import numpy as np

# 1. Defina o caminho exato da sua imagem aqui
caminho = 'ss.jpg'  # Substitua pelo caminho correto da sua imagem

# Carrega a imagem
img = cv2.imread(caminho, cv2.IMREAD_UNCHANGED)

# 2. Verificação se a imagem foi realmente carregada
if img is None:
    print(f"Erro: Não foi possível carregar a imagem em '{caminho}'. Check se o nome e a pasta estão corretos.")
    exit()

# Adiciona o canal Alpha se a imagem for apenas RGB
if len(img.shape) == 2:  # Imagem em escala de cinza
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
elif img.shape[2] == 3:  # Imagem RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

def atualizar(val):
    temp = img.copy()
    fator_alpha = val / 100.0
    temp[:, :, 3] = (temp[:, :, 3] * fator_alpha).astype(np.uint8)
    cv2.imshow("Controle de Transparencia", temp)

cv2.namedWindow("Controle de Transparencia")
cv2.createTrackbar("Opacidade", "Controle de Transparencia", 100, 100, atualizar)

atualizar(100)
cv2.waitKey(0)
cv2.destroyAllWindows()