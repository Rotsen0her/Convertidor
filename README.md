# Convertidor - Proyecto Flask con Docker

## 🚀 Despliegue

### Paso 1: Compilar Tailwind localmente

**En Windows PowerShell:**
```powershell
npm install
npm run build:css
```

**O usa el script automatizado:**
```powershell
.\build.ps1
```

**En Linux/Mac:**
```bash
npm install && npm run build:css
```

### Paso 2: En el VPS
```bash
# Clonar repositorio
git clone https://github.com/tuusuario/convertidor.git
cd convertidor

# Configurar variables de entorno
cp .env.example .env
nano .env

# Levantar servicios
docker compose up -d --build
```

### Paso 3: Configurar HTTPS (opcional)
```bash
docker exec -it convertidor_nginx certbot --nginx -d luziia.cloud -d www.luziia.cloud
```

## 📁 Estructura del proyecto
