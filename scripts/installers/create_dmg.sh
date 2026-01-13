#!/bin/bash

# Script para criar um instalador .dmg para MacOS
# Requer 'create-dmg' (pode ser instalado via brew install create-dmg)
# ou uso manual de hdiutil. Este script usa hdiutil para maior compatibilidade.

APP_NAME="Profgent"
VERSION="1.0"
DIST_DIR="../../dist/onedir/${APP_NAME}.app" # O PyInstaller gera .app no mac
DMG_NAME="${APP_NAME}_${VERSION}_Installer.dmg"
OUTPUT_DIR="../../dist/installers"

mkdir -p "$OUTPUT_DIR"

if [ ! -d "$DIST_DIR" ]; then
    echo "Erro: Bundle .app não encontrado em $DIST_DIR"
    echo "Certifique-se de ter rodado o build_executable.py no MacOS primeiro."
    exit 1
fi

echo "Criando imagem de disco temporária..."
hdiutil create -size 200m -fs HFS+ -volname "$APP_NAME" -ov -srcfolder "$DIST_DIR" "temp.dmg"

echo "Convertendo para formato comprimido (UDZO)..."
hdiutil convert "temp.dmg" -format UDZO -o "$OUTPUT_DIR/$DMG_NAME"

rm "temp.dmg"

echo "Instalador criado em: $OUTPUT_DIR/$DMG_NAME"
