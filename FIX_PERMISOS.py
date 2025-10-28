"""
SOLUCIÓN: Permission Denied en auto-deploy.sh
==============================================

PROBLEMA:
---------
El webhook no puede ejecutar /home/riogas/ruteo/app/auto-deploy.sh
Error: "permission denied"

CAUSA:
------
El archivo auto-deploy.sh no tiene permisos de ejecución (+x)

SOLUCIÓN:
---------

Ejecuta estos comandos en el servidor:

1. Dar permisos de ejecución al script:
   
   chmod +x /home/riogas/ruteo/app/auto-deploy.sh

2. Verificar que tiene los permisos correctos:
   
   ls -l /home/riogas/ruteo/app/auto-deploy.sh
   
   Debería mostrar algo como:
   -rwxr-xr-x 1 riogas riogas ... auto-deploy.sh
   ^^^
   Las 'x' indican que es ejecutable

3. También dar permisos al script de rotación de logs:
   
   chmod +x /home/riogas/ruteo/app/rotate-logs.sh

4. Verificar permisos de todos los scripts:
   
   ls -l /home/riogas/ruteo/app/*.sh

COMANDO RÁPIDO:
---------------
chmod +x /home/riogas/ruteo/app/*.sh

Esto da permisos de ejecución a todos los archivos .sh en la carpeta app/

VERIFICACIÓN:
-------------
Después de dar los permisos, puedes probar manualmente:

bash /home/riogas/ruteo/app/auto-deploy.sh

Si funciona correctamente, el próximo push a GitHub debería 
activar el auto-deploy automáticamente.

NOTA:
-----
Este problema ocurrió porque cuando subiste los archivos a Git,
los permisos de ejecución no se preservaron. Git guarda los permisos
de archivos, así que puedes también corregirlo localmente y hacer push:

EN TU MÁQUINA LOCAL (Windows con Git Bash):
--------------------------------------------
git update-index --chmod=+x app/auto-deploy.sh
git update-index --chmod=+x app/rotate-logs.sh
git commit -m "Fix: Agregar permisos de ejecución a scripts .sh"
git push origin main

Luego en el servidor, hacer pull y los permisos vendrán correctos.

"""

print(__doc__)
