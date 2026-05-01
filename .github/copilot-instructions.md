# Inventory Corpus v2 - Instrucciones de Desarrollo

## Descripción del Proyecto
Sistema avanzado de gestión de inventario de calzado con IA integrada, detección de objetos YOLO mejorada, detección de colores RGB, OCR para texto/números, y reentrenamiento continuo del modelo.

## Stack Tecnológico
- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Frontend**: Angular 17+, RxJS, Angular Material
- **IA/ML**: YOLO v8, OpenCV, Pytesseract (OCR)
- **Autenticación**: JWT/OAuth2
- **BD**: SQLite (desarrollo) / PostgreSQL (producción)

## Estructura del Proyecto
```
Inventory-Corpus-v2/
├── backend/              # API FastAPI
├── frontend/             # Angular SPA
├── ml-pipeline/          # Scripts de IA y entrenamiento
├── docs/                 # Documentación
└── .github/             # Configuración
```

## Características Principales
✅ Detección avanzada de objetos con YOLO
✅ Extracción de colores RGB en tiempo real
✅ OCR para lectura de etiquetas y números
✅ Sistema de entrenamiento continuo
✅ Soporte para nuevos productos no entrenados
✅ Integración webcam en tiempo real
✅ Autenticación segura JWT
✅ CRUD completo de inventario

## Próximos Pasos
- [ ] Configurar backend Python
- [ ] Crear modelos de base de datos
- [ ] Implementar APIs REST
- [ ] Configurar frontend Angular
- [ ] Integrar pipeline de ML
- [ ] Implementar sistema de entrenamiento
