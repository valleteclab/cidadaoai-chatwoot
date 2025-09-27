#!/bin/bash

# Arquivos para verificar
files=(
    "frontend/tecnico/js/app.js"
    "frontend/tecnico/js/config.js"
    "frontend/tecnico/index.html"
    "backend/main.py"
)

echo "🔍 Verificando arquivos..."
echo

for file in "${files[@]}"; do
    echo "📄 Verificando: $file"
    if [ -f "$file" ]; then
        echo "   ✅ Arquivo existe"
        echo "   📊 Tamanho: $(stat -f %z "$file") bytes"
        echo "   🕒 Última modificação: $(stat -f %Sm "$file")"
        echo "   📝 Primeiras 3 linhas:"
        head -n 3 "$file"
        echo
    else
        echo "   ❌ Arquivo não encontrado!"
        echo
    fi
done

echo "✨ Verificação concluída!"
