#!/usr/bin/env powershell
# Script para instalar Tesseract OCR automáticamente en Windows

# URLs de descarga
$tesseractUrl = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.0/tesseract-ocr-w64-setup-v5.3.0.exe"
$installerPath = "$env:TEMP\tesseract-installer.exe"

Write-Host "🔄 Descargando Tesseract OCR..." -ForegroundColor Cyan

try {
    # Descargar
    Invoke-WebRequest -Uri $tesseractUrl -OutFile $installerPath -ErrorAction Stop
    Write-Host "✅ Descarga completada" -ForegroundColor Green
    
    # Instalar
    Write-Host "🔧 Instalando Tesseract..." -ForegroundColor Cyan
    & $installerPath /S /D=C:\Program` Files\Tesseract-OCR
    
    # Esperar a que termine
    Start-Sleep -Seconds 30
    
    # Verificar
    $tesseractExe = "C:\Program Files\Tesseract-OCR\tesseract.exe"
    if (Test-Path $tesseractExe) {
        Write-Host "✅ Tesseract instalado exitosamente" -ForegroundColor Green
        & $tesseractExe --version
    } else {
        Write-Host "❌ La instalación no fue exitosa" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    Write-Host "Solución: Descarga manualmente desde https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Yellow
}

# Limpiar
Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
