/**
 * Configuración del frontend (inyectada en el deploy).
 * En local / mismo origen, API_BASE = '/api'. En CloudFront, se reemplaza por la
 * URL de API Gateway al subir el frontend a S3.
 */
window.METALSHOP_API_BASE = '/api';
window.METALSHOP_CURRENCY = 'MXN';
window.METALSHOP_LOCALE = 'es-MX';
