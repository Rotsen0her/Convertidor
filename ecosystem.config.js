// Configuración PM2 para Convertidor Flask
// Este archivo debe estar en /var/www/convertidor/ en el servidor

module.exports = {
  apps: [{
    name: 'convertidor-flask',
    script: './start_gunicorn.sh',
    interpreter: '/bin/bash',
    cwd: '/var/www/convertidor',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    },
    error_file: './logs/error.log',
    out_file: './logs/output.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    // Crear directorio de logs si no existe
    post_update: ['mkdir -p logs'],
    // Reinicio automático en caso de error
    min_uptime: '10s',
    max_restarts: 10,
    restart_delay: 4000
  }]
};
