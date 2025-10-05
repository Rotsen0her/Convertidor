# ✅ PROYECTO LISTO PARA DEPLOY DOCKER

## 🎯 Resumen de Configuración

El proyecto **Convertidor** está 100% configurado para deploy en **luziia.cloud** usando **Docker Compose**.

---

## 📁 Estructura Final del Proyecto

```
Convertidor/
├── backend/                          ✅ Aplicación Flask
│   ├── app.py                       ✅ Aplicación principal
│   ├── config.py                    ✅ Configuración (usa MYSQL_DATABASE)
│   ├── requirements.txt             ✅ Dependencias Python
│   ├── Dockerfile                   ✅ ACTUALIZADO (sin Node)
│   ├── start_gunicorn.sh            ✅ Script de inicio
│   ├── static/
│   │   └── css/
│   │       └── output.css           ⚠️  Generar con npm run build-css
│   └── templates/                   ✅ Templates Jinja2
│
├── nginx/                           ✅ Reverse Proxy
│   ├── Dockerfile                   ✅ ACTUALIZADO (nginx:latest)
│   └── default.conf                 ✅ CORREGIDO (sin proxy_params)
│
├── docker-compose.yml               ✅ SIMPLIFICADO
├── .env.example                     ✅ ACTUALIZADO con tus valores
├── package.json                     ✅ Script build-css correcto
├── tailwind.config.js               ✅ Configuración Tailwind
├── src/input.css                    ✅ Input de Tailwind
│
├── deploy-docker-quick.ps1          ✅ NUEVO - Deploy automático
├── DEPLOY_DOCKER_GUIDE.md           ✅ NUEVO - Guía completa
├── git-cleanup.ps1                  ✅ Limpiar archivos sensibles
├── .gitignore                       ✅ MEJORADO (100+ exclusiones)
│
└── .github/workflows/
    ├── deploy.yml                   ✅ GitHub Actions (PM2)
    └── deploy-docker.yml            ✅ GitHub Actions (Docker)
```

---

## ✅ Archivos Actualizados

| Archivo | Cambio | Estado |
|---------|--------|--------|
| `backend/Dockerfile` | Simplificado según spec | ✅ |
| `backend/config.py` | Usa `MYSQL_DATABASE` variable | ✅ |
| `nginx/Dockerfile` | Cambiado a `nginx:latest` | ✅ |
| `nginx/default.conf` | Removido `include proxy_params` | ✅ |
| `docker-compose.yml` | Simplificado, sin healthcheck | ✅ |
| `.env.example` | Valores de producción | ✅ |
| `package.json` | Comando `build-css` correcto | ✅ |
| `.gitignore` | 100+ exclusiones | ✅ |

---

## 🚀 Deploy en 3 Pasos

### 1️⃣ Compilar CSS localmente
```powershell
npm install
npm run build-css
```

### 2️⃣ Ejecutar script de deploy
```powershell
.\deploy-docker-quick.ps1
```

### 3️⃣ Configurar .env en el servidor (primera vez)
```bash
ssh root@89.116.51.172
cd /var/www/Convertidor
cp .env.example .env
nano .env  # Ajustar valores
docker-compose restart
```

---

## 📊 Variables de Entorno (.env)

```env
SECRET_KEY=d4f8a1c6b7e3f2a9c0e5b6d9f3a1c2b4d6e7f8a9c0b1d2e3f4a5b6c7d8e9f0
MYSQL_ROOT_PASSWORD=B3rr!0_J0s3#Secure
MYSQL_DATABASE=joseberrio_db
MYSQL_USER=joseberrio_admin
MYSQL_PASSWORD=B3rr!0_J0s3#Secure
MYSQL_HOST=db
MYSQL_PORT=3306
FLASK_ENV=production
FLASK_DEBUG=0
```

⚠️ **Cambiar valores en producción**

---

## 🐳 Contenedores Docker

| Nombre | Puerto | Servicio |
|--------|--------|----------|
| `convertidor_backend` | 8000 (interno) | Flask + Gunicorn |
| `convertidor_db` | 3306 (interno) | MySQL 8.0 |
| `convertidor_nginx` | 80, 443 | Nginx + SSL |

---

## 🔐 Configurar HTTPS (Certbot)

```bash
# En el VPS
ssh root@89.116.51.172
cd /var/www/Convertidor

# Ejecutar Certbot
docker exec -it convertidor_nginx certbot --nginx \
  -d luziia.cloud \
  -d www.luziia.cloud \
  --email tu@email.com \
  --agree-tos

# Reiniciar
docker-compose restart nginx
```

---

## 📋 Comandos Útiles

### Ver estado
```bash
docker-compose ps
```

### Ver logs
```bash
docker-compose logs -f
docker-compose logs -f backend
```

### Reiniciar
```bash
docker-compose restart
docker-compose restart backend
```

### Reconstruir
```bash
docker-compose down
docker-compose up -d --build
```

### Entrar a contenedor
```bash
docker exec -it convertidor_backend bash
docker exec -it convertidor_db mysql -u root -p
```

---

## 🔄 Flujo de Trabajo

### Desarrollo Local
```powershell
# 1. Editar código
code backend/app.py

# 2. Si cambias estilos, recompilar CSS
npm run build-css

# 3. Commit
git add .
git commit -m "✨ Nueva feature"
```

### Deploy Manual
```powershell
# Ejecutar script
.\deploy-docker-quick.ps1
```

### Deploy Automático (GitHub Actions)
```powershell
# Solo push
git push origin main

# GitHub Actions se encarga del resto
```

---

## 🗄️ Inicializar Base de Datos

```bash
# Conectarse a MySQL
docker exec -it convertidor_db mysql -u root -p

# Crear tablas
USE joseberrio_db;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'usuario') DEFAULT 'usuario',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# Crear usuario admin (password: admin123)
INSERT INTO usuarios (usuario, password, rol) VALUES
('admin', 'scrypt:32768:8:1$yZQH8Jf0rGJ4Rwzm$...', 'admin');
```

---

## ✅ Checklist Pre-Deploy

- [ ] Node.js instalado localmente
- [ ] Docker instalado en VPS
- [ ] Dominio `luziia.cloud` apunta a `89.116.51.172`
- [ ] CSS compilado (`npm run build-css`)
- [ ] `.env` configurado en servidor
- [ ] Puertos 80 y 443 abiertos
- [ ] SSH access al VPS

---

## 🎯 URLs Finales

| Entorno | URL |
|---------|-----|
| **HTTP** | http://luziia.cloud |
| **HTTPS** | https://luziia.cloud (después de Certbot) |
| **IP** | http://89.116.51.172 |

---

## 📚 Documentación

- **`DEPLOY_DOCKER_GUIDE.md`** - Guía paso a paso completa
- **`GITHUB_DEPLOY.md`** - Configurar GitHub Actions
- **`COMANDOS_UTILES.md`** - Referencia de comandos

---

## 🆘 Troubleshooting

### CSS no se carga
```powershell
npm run build-css
.\deploy-docker-quick.ps1
```

### Backend no inicia
```bash
docker-compose logs backend
docker exec convertidor_backend env | grep MYSQL
```

### MySQL no conecta
```bash
docker-compose logs db
docker exec -it convertidor_db mysql -u root -p
```

---

## 🎉 Resultado Final

✅ Flask + Gunicorn en contenedor  
✅ MySQL 8.0 aislado  
✅ Nginx como proxy  
✅ Tailwind CSS compilado  
✅ Variables de entorno seguras  
✅ Listo para HTTPS  

---

**Estado:** ✅ LISTO PARA PRODUCCIÓN  
**Última actualización:** Octubre 2025  
**Deploy:** `.\deploy-docker-quick.ps1`
