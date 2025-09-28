# 📋 Comandos para Acessar o Servidor e Deploy

## 🖥️ **Comandos SSH e Ambiente:**

### **1. Acessar o Servidor**
```bash
ssh root@sisgov.app.br
```

### **2. Navegar para o Diretório do Projeto**
```bash
cd /root/projetos/cidadaoai-chatwoot
```

### **3. Ativar o Ambiente Virtual (se necessário)**
```bash
source venv/bin/activate
```

### **4. Atualizar o Projeto**
```bash
git pull origin main
./update-server.sh
```

### **5. Verificar Status dos Serviços**
```bash
docker service ls --filter name=cidadaoai
```

### **6. Ver Logs do Serviço**
```bash
docker service logs -f cidadaoai_cidadaoai_app
```

## 🔄 **Processo de Deploy Completo:**

### **Local (Desenvolvimento):**
```bash
git add .
git commit -m "Descrição das mudanças"
git push origin main
```

### **Servidor (Produção):**
```bash
ssh root@sisgov.app.br
cd /root/projetos/cidadaoai-chatwoot
git pull origin main
./update-server.sh
```

## 📝 **Notas Importantes:**
- O projeto roda via Docker Swarm
- Usa o script `update-server.sh` para atualizações
- Serviço principal: `cidadaoai_cidadaoai_app`
- Stack: `cidadaoai`
