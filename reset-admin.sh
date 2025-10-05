mkdir -p scripts
cat > scripts/reset-admin.sh << 'EOF'
#!/bin/bash
set -e

echo "🔧 Resetear contraseña de administrador"
echo ""

# Verificar que los contenedores estén corriendo
if ! docker-compose ps | grep -q "convertidor_backend.*Up"; then
    echo "❌ Los contenedores no están corriendo"
    echo "   Ejecuta: docker-compose up -d"
    exit 1
fi

# Leer .env
if [ ! -f ".env" ]; then
    echo "❌ No se encuentra el archivo .env"
    exit 1
fi

source .env
MYSQL_DATABASE="${MYSQL_DATABASE:-zafiro_bi}"

# Solicitar nueva contraseña
read -sp "Nueva contraseña para admin: " NEW_PASSWORD
echo ""
read -sp "Confirmar contraseña: " NEW_PASSWORD_CONFIRM
echo ""

if [ "$NEW_PASSWORD" != "$NEW_PASSWORD_CONFIRM" ]; then
    echo "❌ Las contraseñas no coinciden"
    exit 1
fi

# Generar hash
echo "📝 Generando hash de contraseña..."
HASH=$(docker-compose exec -T backend python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('${NEW_PASSWORD}'))" | tr -d '\r\n')

# Actualizar en base de datos
echo "💾 Actualizando contraseña en ${MYSQL_DATABASE}..."
docker-compose exec -T db mysql -u root -p${MYSQL_ROOT_PASSWORD} ${MYSQL_DATABASE} <<EOSQL
UPDATE usuarios SET password = '${HASH}' WHERE usuario = 'admin';
SELECT CONCAT('✅ Contraseña actualizada - Hash length: ', LENGTH(password)) as resultado FROM usuarios WHERE usuario = 'admin' LIMIT 1;
EOSQL

echo ""
echo "✅ Contraseña de admin actualizada correctamente"
EOF

chmod +x scripts/reset-admin.sh