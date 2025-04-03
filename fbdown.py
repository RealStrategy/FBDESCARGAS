#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import platform
import subprocess
import re
import time
from urllib.parse import urlparse

# Constantes
VERSION = "1.1"
AUTHOR = "@RealStrategy"
CANAL = "https://www.youtube.com/@zonatodoreal"
SUPPORTED_DOMAINS = ['facebook.com', 'fb.watch']

def limpiar_nombre_archivo(nombre):
    """Limpia el nombre del archivo para que sea válido en Windows"""
    nombre = re.sub(r'[\\/*?:"<>|]', '', nombre)  # Elimina caracteres inválidos
    nombre = re.sub(r'\s+', ' ', nombre).strip()  # Reduce múltiples espacios
    nombre = nombre[:150]  # Limita la longitud del nombre
    return nombre

def clear_screen():
    """Limpia la pantalla de la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Muestra el encabezado"""
    clear_screen()
    print("\n" + "="*50)
    print(f" Facebook Video Downloader PRO".center(50))
    print(f" Versión {VERSION}".center(50))
    print("="*50 + "\n")

def obtener_carpeta_descargas():
    """Obtiene la ruta de descargas"""
    if os.path.exists('/data/data/com.termux/files/home'):  # Android (Termux)
        posibles_rutas = [
            '/sdcard/Download',
            '/storage/emulated/0/Download'
        ]
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                return ruta
        return '/sdcard/Download'
    
    # Para otros sistemas operativos
    sistema = platform.system()
    home = os.path.expanduser("~")
    
    if sistema == "Windows":
        downloads = os.path.join(os.environ["USERPROFILE"], "Downloads")
    elif sistema == "Darwin":
        downloads = os.path.join(home, "Downloads")
    else:  # Linux y otros
        downloads = os.path.join(home, "Descargas")
        if not os.path.exists(downloads):
            downloads = os.path.join(home, "Downloads")
    
    os.makedirs(downloads, exist_ok=True)
    return downloads

def verificar_instalacion_yt_dlp():
    """Verifica e instala yt-dlp"""
    try:
        import yt_dlp
        print("\n✓ yt-dlp ya está instalado")
        return yt_dlp
    except ImportError:
        print("\nInstalando yt-dlp...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            import yt_dlp
            print("✓ yt-dlp instalado correctamente")
            return yt_dlp
        except Exception as e:
            print(f"\nError al instalar yt-dlp: {str(e)}")
            sys.exit(1)

def verificar_cookies_facebook():
    """Verifica si existen cookies para Facebook"""
    cookies_path = os.path.join(obtener_carpeta_descargas(), "facebook_cookies.txt")
    if os.path.exists(cookies_path):
        print("\n✓ Archivo de cookies encontrado (para videos privados)")
        return cookies_path
    return None

def mostrar_progreso(d):
    """Muestra el progreso de descarga"""
    if d['status'] == 'downloading':
        porcentaje = d.get('_percent_str', '0%').strip()
        velocidad = d.get('_speed_str', '?').strip()
        eta = d.get('_eta_str', '?').strip()
        sys.stdout.write(f"\rDescargando: {porcentaje} | Velocidad: {velocidad} | Tiempo restante: {eta}")
        sys.stdout.flush()

def es_url_facebook_valida(url):
    """Verifica si la URL es de Facebook"""
    try:
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            return False
        
        dominio = parsed.netloc.lower()
        return any(sd in dominio for sd in SUPPORTED_DOMAINS)
    except:
        return False

def descargar_video_facebook(url):
    """Descarga video de Facebook"""
    try:
        yt_dlp = verificar_instalacion_yt_dlp()
        carpeta_descargas = obtener_carpeta_descargas()
        cookies_path = verificar_cookies_facebook()
        
        config = {
            'format': 'best',  # Descarga el mejor formato disponible
            'outtmpl': os.path.join(carpeta_descargas, '%(title)s.%(ext)s'),
            'progress_hooks': [mostrar_progreso],
            'retries': 5,
            'nocheckcertificate': True,
            'quiet': True,
            'windowsfilenames': True,  # Para nombres de archivo compatibles con Windows
        }
        
        if cookies_path:
            config['cookiefile'] = cookies_path
        else:
            print("\n⚠ Descargando sin cookies - algunos videos pueden fallar")
        
        with yt_dlp.YoutubeDL(config) as ydl:
            print("\nObteniendo información del video...")
            info = ydl.extract_info(url, download=False)
            
            # Limpiar el título para el nombre del archivo
            titulo_limpio = limpiar_nombre_archivo(info.get('title', 'video_facebook'))
            
            print("\n--- INFORMACIÓN DEL VIDEO ---")
            print(f"\nTítulo original: {info.get('title', 'Desconocido')}")
            print(f"Título limpio: {titulo_limpio}")
            print(f"Duración: {info.get('duration', 'Desconocido')} segundos")
            print(f"Formato: {info.get('ext', 'Desconocido')}")
            print(f"Resolución: {info.get('resolution', 'Desconocido')}")
            
            confirmar = input("\n¿Descargar este video? (s/n): ").lower()
            if confirmar != 's':
                print("\nDescarga cancelada")
                return
            
            # Configurar nombre de archivo limpio
            config['outtmpl'] = os.path.join(carpeta_descargas, f'{titulo_limpio}.%(ext)s')
            
            print("\nIniciando descarga...")
            with yt_dlp.YoutubeDL(config) as ydl_clean:
                ydl_clean.download([url])
            
            print(f"\n✓ Descarga completada: {titulo_limpio}.{info.get('ext', 'mp4')}")
            print(f"Ubicación: {carpeta_descargas}")
            
    except Exception as e:
        if "Private video" in str(e):
            print("\n✗ Error: Video privado. Necesitas cookies de Facebook.")
            print("Guarda tus cookies en 'facebook_cookies.txt' en la carpeta de descargas.")
        else:
            print(f"\n✗ Error: {str(e)}")

def mostrar_instrucciones():
    """Muestra instrucciones básicas"""
    print_header()
    print("\nINSTRUCCIONES:")
    print("\n1. Copia el enlace de cualquier video público de Facebook")
    print("2. Pega el enlace cuando se te solicite")
    print("\nPara videos privados:")
    print("1. Exporta tus cookies de Facebook como 'facebook_cookies.txt'")
    print("2. Coloca el archivo en tu carpeta de descargas")
    input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    print_header()
    
    if len(sys.argv) > 1:
        # Modo directo desde línea de comandos
        url = sys.argv[1]
        if es_url_facebook_valida(url):
            descargar_video_facebook(url)
        else:
            print("\nError: La URL no es de Facebook")
            print("Ejemplos válidos:")
            print("- https://www.facebook.com/watch/?v=123456789")
            print("- https://fb.watch/abc123def/")
    else:
        # Modo interactivo
        while True:
            print(" MENÚ PRINCIPAL ".center(50, "-"))
            print("\n1. Descargar Video de Facebook")
            print("2. Instrucciones")
            print("3. Salir")
            print("-"*50 + "\n")
            opcion = input("\nSelecciona una opción (1-3): ").strip()
            
            if opcion == "1":
                url = input("\nPega el enlace del video de Facebook: ").strip()
                
                if not es_url_facebook_valida(url):
                    print("\nError: URL no válida. Debe ser de Facebook.")
                    print("Ejemplo: https://www.facebook.com/watch/?v=123456789")
                    continue
                    
                descargar_video_facebook(url)
                
            elif opcion == "2":
                mostrar_instrucciones()
                
            elif opcion == "3":
                print("\n¡Hasta luego!")
                break
                
            else:
                print("\nOpción no válida")
            
            input("\nPresiona Enter para continuar...")
            print_header()
