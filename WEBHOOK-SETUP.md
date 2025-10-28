# 🔄 Configuración de Auto-Deploy con Webhook Local

## 📋 Opción sin GitHub Actions (Todo en tu servidor)

### **PASO 1: Subir archivos al servidor**

Desde tu computadora (PowerShell):

```powershell
# Subir archivos necesarios
scp app/auto-deploy.sh riogas@serviciosgis.riogas.uy:/home/riogas/ruteo/app/
scp webhook.conf riogas@serviciosgis.riogas.uy:/home/riogas/ruteo/
scp webhook.service riogas@serviciosgis.riogas.uy:/tmp/
```

### **PASO 2: En el servidor, configurar permisos**

```bash
# Conectarse al servidor
ssh riogas@serviciosgis.riogas.uy

# Dar permisos de ejecución
chmod +x ~/ruteo/app/auto-deploy.sh

# Crear directorio de logs
mkdir -p ~/ruteo/logs
```

### **PASO 3: Instalar y configurar webhook**

```bash
# Instalar webhook
sudo apt update
sudo apt install webhook -y

# Copiar servicio systemd
sudo cp /tmp/webhook.service /etc/systemd/system/

# Recargar systemd
sudo systemctl daemon-reload

# Habilitar e iniciar el servicio
sudo systemctl enable webhook
sudo systemctl start webhook

# Verificar estado
sudo systemctl status webhook
```

### **PASO 4: Configurar Port Forwarding en el Router**

Redirigir puerto para webhook:

```
Puerto externo: 9000
Puerto interno: 9000
IP interna: [IP de tu servidor]
Protocolo: TCP
```

### **PASO 5: Configurar Webhook en GitHub**

1. Ve a: `https://github.com/Riogas/ruteo/settings/hooks`
2. Click en **"Add webhook"**
3. Configura:

```
Payload URL: http://serviciosgis.riogas.uy:9000/hooks/ruteo-deploy
Content type: application/json
Secret: MI_SECRET_SUPER_SEGURO_123
```

4. En **"Which events would you like to trigger this webhook?"**:
   - Selecciona: **"Just the push event"**

5. Click en **"Add webhook"**

### **PASO 6: Probar**

Haz un commit y push:

```powershell
git add .
git commit -m "test: probar auto-deploy con webhook"
git push origin main
```

Verifica los logs en el servidor:

```bash
tail -f ~/ruteo/deploy.log
```

---

## 🔒 Seguridad

**IMPORTANTE**: Cambia el secret en `webhook.conf`:

```bash
nano ~/ruteo/webhook.conf
```

Cambia `MI_SECRET_SUPER_SEGURO_123` por algo aleatorio:

```bash
# Generar un secret aleatorio
openssl rand -hex 32
```

Usa ese mismo secret en GitHub webhook configuration.

---

## 📊 Verificar funcionamiento

```bash
# Ver logs del webhook service
sudo journalctl -u webhook -f

# Ver logs del deployment
tail -f ~/ruteo/deploy.log

# Ver estado del servicio
sudo systemctl status webhook
```

---

## 🛑 Comandos útiles

```bash
# Detener webhook
sudo systemctl stop webhook

# Reiniciar webhook
sudo systemctl restart webhook

# Ver configuración actual
cat ~/ruteo/webhook.conf

# Probar manualmente el script
bash ~/ruteo/app/auto-deploy.sh
```

---

## 🔄 Diferencias con GitHub Actions

| Aspecto | GitHub Actions | Webhook Local |
|---------|---------------|---------------|
| **Dónde se ejecuta** | En la nube de GitHub | En tu servidor |
| **Requiere IP pública** | Sí (para SSH) | Sí (para webhook) |
| **Configuración** | Archivo .yml | Script bash + webhook |
| **Logs** | En GitHub | En tu servidor |
| **Dependencias** | GitHub disponible | Tu servidor disponible |
| **Costo** | Gratis (con límites) | Gratis (usa tu servidor) |

---

## ✅ Ventajas del Webhook Local

- ✅ No necesita acceso SSH desde GitHub
- ✅ Más rápido (no espera runners de GitHub)
- ✅ Logs directos en tu servidor
- ✅ Más control sobre el proceso
- ✅ No consume minutos de GitHub Actions

---

## 🚀 Resumen del Flujo

```
1. Git push → GitHub
2. GitHub → envía webhook → http://serviciosgis.riogas.uy:9000
3. Tu servidor → recibe webhook → ejecuta auto-deploy.sh
4. auto-deploy.sh → git pull + docker rebuild
5. Listo ✅
```

