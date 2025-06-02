import json
import os
import re
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Configuración tipográfica profesional
rcParams['text.usetex'] = False
plt.rcParams['mathtext.fontset'] = 'cm'  # Fuente matemática Computer Modern
plt.rcParams['font.family'] = 'serif'    # Fuente principal serif
plt.rcParams['font.serif'] = ['Times New Roman']  # Fuente específica
plt.rcParams['font.size'] = 24
plt.rcParams['axes.unicode_minus'] = False  # Manejo correcto de signos negativos

def normalizar_espacios(texto):
    """Normaliza espacios en el texto, preservando expresiones matemáticas"""
    # Preservar espacios en expresiones matemáticas entre $
    partes = re.split(r'(\$.+?\$)', texto)
    resultado = []
    for i, parte in enumerate(partes):
        if i % 2 == 1:  # Es una expresión matemática
            resultado.append(parte)
        else:  # Es texto normal
            # Normalizar espacios múltiples y añadir espacio después de puntuación
            parte = re.sub(r'\s+', ' ', parte.strip())
            parte = re.sub(r'([.,:;!?])(\w)', r'\1 \2', parte)
            resultado.append(parte)
    return ' '.join(''.join(resultado).split())  # Eliminar espacios duplicados

def reparar_expresion(texto):
    """Corrige expresiones matemáticas problemáticas"""
    if not isinstance(texto, str):
        return str(texto)
    
    texto = normalizar_espacios(texto)
    
    # Eliminar signos $ inconsistentes
    texto = texto.strip().replace('$ $', '').strip('$')
    
    # Manejar prefijos como "Resuelve:"
    if re.match(r'^(Resolver?e?[:\s])', texto, re.IGNORECASE):
        texto = re.sub(r'^Resolver?e?[:\s]\s*', '', texto, flags=re.IGNORECASE)
    
    # Corregir paréntesis escapados y otros formatos
    texto = texto.replace(r'\(', '').replace(r'\)', '')
    texto = re.sub(r'\\[()]', '', texto)
    
    # Convertir fracciones y operadores
    texto = re.sub(r'(\d+)\s*/\s*(\d+)', r'\\frac{\1}{\2}', texto)
    texto = re.sub(r'([+=*/-])', r' \1 ', texto)
    
    return texto.strip()

def crear_imagen_segura(texto, archivo):
    fig = plt.figure(figsize=(12, 4), facecolor='white', dpi=200)
    ax = fig.add_subplot(111)
    
    try:
        texto_corregido = reparar_expresion(texto)
        
        # Configuración de texto uniforme
        props = {
            'ha': 'center',
            'va': 'center',
            'fontsize': 28,
            'fontfamily': 'serif'
        }
        
        if any(c in texto_corregido for c in {'\\', '^', '_', '{', '}'}):
            # Asegurar que las expresiones matemáticas estén bien formadas
            if not texto_corregido.startswith('$'):
                texto_corregido = f'${texto_corregido}$'
            ax.text(0.5, 0.5, texto_corregido, **props)
        else:
            # Texto normal con espaciado consistente
            ax.text(0.5, 0.5, texto_corregido, **props)
            
    except Exception as e:
        print(f"⚠️ Error procesando: '{texto[:50]}...' - Usando texto plano. Error: {str(e)}")
        ax.text(0.5, 0.5, texto, **props)
    
    ax.axis('off')
    plt.savefig(archivo, bbox_inches='tight', dpi=200, pad_inches=0.1)
    plt.close()

# Procesamiento de archivos (igual que antes)
with open('preguntas.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

os.makedirs('preguntas_ok', exist_ok=True)
os.makedirs('opciones_ok', exist_ok=True)

for isla, preguntas in data.items():
    for i, pregunta in enumerate(preguntas, 1):
        crear_imagen_segura(
            pregunta['pregunta'],
            f'preguntas_ok/{isla}_p{i}.png'
        )
        for j, opcion in enumerate(pregunta['opciones'], 1):
            crear_imagen_segura(
                opcion['texto'],
                f'opciones_ok/{isla}_p{i}_op{j}.png'
            )

print("✅ ¡Proceso completado exitosamente!")
print(f"Preguntas generadas: {sum(len(p) for p in data.values())}")
print(f"Opciones generadas: {sum(len(p['opciones']) for p in sum(data.values(), []))}")