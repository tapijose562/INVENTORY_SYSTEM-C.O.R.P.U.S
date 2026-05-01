#!/usr/bin/env python3
"""
Script para probar la configuración de IA para sugerencias de texto OCR
"""
import os
from app.core.config import settings
from app.services.ai import AISuggestionService

def test_ai_configuration():
    print("🔍 Probando configuración de IA para sugerencias OCR...\n")

    # Verificar configuración
    print("📋 Configuración actual:")
    print(f"  OpenRouter API Key: {'✅ Configurada' if settings.OPENROUTER_API_KEY and settings.OPENROUTER_API_KEY != 'tu_clave_api_de_openrouter_aqui' else '❌ No configurada'}")
    print(f"  OpenRouter Model: {settings.OPENROUTER_MODEL}")
    print(f"  Ollama URL: {'✅ Configurada' if settings.OLLAMA_API_URL else '❌ No configurada'}")
    print(f"  Ollama Model: {settings.OLLAMA_MODEL}")
    print()

    # Probar sugerencia
    test_ocr = "NIKE AIR MAX 90 TALLA 42"
    print(f"🧪 Probando con texto OCR de ejemplo: '{test_ocr}'")

    try:
        suggestion = AISuggestionService.suggest_text(ocr_text=test_ocr)
        print(f"🤖 Sugerencia generada: '{suggestion}'")

        if "OpenRouter API" in suggestion or "Ollama" in suggestion:
            print("⚠️  Se está usando fallback - configura una API válida")
        else:
            print("✅ ¡La IA está funcionando correctamente!")

    except Exception as e:
        print(f"❌ Error al generar sugerencia: {e}")

    print("\n💡 Para configurar:")
    print("1. OpenRouter: Obtén tu API key en https://openrouter.ai/keys")
    print("2. Ollama: Instala Ollama y ejecuta 'ollama serve'")
    print("3. Actualiza las variables en backend/.env")

if __name__ == "__main__":
    test_ai_configuration()