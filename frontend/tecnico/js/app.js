// Configurações (carregadas do config.js)
const API_BASE_URL = CONFIG.API_BASE_URL;
const CHATWOOT_API_URL = CONFIG.CHATWOOT_API_URL;
const CHATWOOT_ACCOUNT_ID = CONFIG.CHATWOOT_ACCOUNT_ID;

// Estado da aplicação
let currentConversation = null;
let conversations = [];
let socket = null;

// Elementos DOM
const conversationsList = document.getElementById('conversationsList');
const chatHeader = document.getElementById('chatHeader');
const messagesContainer = document.getElementById('messagesContainer');
const messageInput = document.getElementById('messageInput');
const messageText = document.getElementById('messageText');
const sendBtn = document.getElementById('sendBtn');
const recordBtn = document.getElementById('recordBtn');
const audioFileInput = document.getElementById('audioFile');
const contactName = document.getElementById('contactName');
const contactPhone = document.getElementById('contactPhone');
const conversationStatus = document.getElementById('conversationStatus');
const typingIndicator = document.getElementById('typingIndicator');
const loadingOverlay = document.getElementById('loadingOverlay');
const refreshBtn = document.getElementById('refreshBtn');
const searchInput = document.getElementById('searchInput');

// Testar conectividade com a API
async function testAPIConnection() {
    try {
        console.log('Testando conectividade com API...');
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        console.log('✅ API conectada:', data);
        return true;
    } catch (error) {
        console.error('❌ Erro na conectividade da API:', error);
        return false;
    }
}

// Inicialização
document.addEventListener('DOMContentLoaded', async function() {
    initializeApp();
    
    // Testar conectividade
    const isConnected = await testAPIConnection();
    if (!isConnected) {
        console.warn('API não está conectada, usando dados mockados');
    }
    
    setupEventListeners();
    loadConversations();
});

function initializeApp() {
    console.log('Inicializando Cidadão.AI - Painel Técnico');
    
    // Configurar auto-resize do textarea
    messageText.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });
    
    // Configurar envio com Enter
    messageText.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

function setupEventListeners() {
    sendBtn.addEventListener('click', sendMessage);
    if (recordBtn) recordBtn.addEventListener('click', toggleRecording);
    if (audioFileInput) audioFileInput.addEventListener('change', handleAudioFile);
    refreshBtn.addEventListener('click', loadConversations);
    searchInput.addEventListener('input', filterConversations);
    
    // Carregar conversas iniciais
    loadConversations();
    
    // Inicializar WebSocket
    setupWebSocket();
}

// Gravação de áudio
let mediaRecorder = null;
let recordedChunks = [];
let isRecording = false;

async function toggleRecording() {
    try {
        // Verificar suporte básico
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            console.warn('❌ API de mídia não suportada');
            showError('Seu navegador não suporta acesso ao microfone. Use o botão de upload.');
            return;
        }

        if (!isRecording) {
            // Primeiro obter acesso ao microfone
            let stream;
            try {
                stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        channelCount: 1,
                        sampleRate: 48000,
                        sampleSize: 16,
                        echoCancellation: true,
                        noiseSuppression: true
                    }
                });
                console.log('✅ Acesso ao microfone concedido');
            } catch (err) {
                console.error('❌ Erro ao acessar microfone:', err);
                showError('Não foi possível acessar o microfone. Verifique as permissões.');
                return;
            }

            // Agora que temos o stream, verificar suporte ao MediaRecorder
            if (!window.MediaRecorder) {
                console.warn('❌ MediaRecorder não suportado');
                stream.getTracks().forEach(track => track.stop());
                showError('Seu navegador não suporta gravação de áudio. Use o botão de upload.');
                return;
            }

            // Tentar formatos em ordem de preferência
            const mimeTypes = [
                'audio/ogg;codecs=opus',  // Melhor formato para WhatsApp
                'audio/webm;codecs=opus', // Alternativa comum
                'audio/webm',             // Fallback webm
                'audio/ogg'               // Fallback ogg
            ];
            
            const mimeType = mimeTypes.find(type => {
                try {
                    return MediaRecorder.isTypeSupported(type);
                } catch (e) {
                    console.warn(`⚠️ Erro ao verificar suporte para ${type}:`, e);
                    return false;
                }
            });

            if (!mimeType) {
                console.warn('❌ Nenhum formato suportado');
                stream.getTracks().forEach(track => track.stop());
                showError('Seu navegador não suporta os formatos de áudio necessários. Use o botão de upload.');
                return;
            }
            
            // Iniciar gravação com o stream obtido
            console.log(`🎙️ Iniciando gravação: ${mimeType}`);
            mediaRecorder = new MediaRecorder(stream, { 
                mimeType,
                audioBitsPerSecond: 128000
            });
            
            recordedChunks = [];
            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    console.log(`📊 Chunk: ${e.data.size} bytes`);
                    recordedChunks.push(e.data);
                }
            };
            
            mediaRecorder.onstop = sendRecordedAudio;
            mediaRecorder.onerror = (e) => {
                console.error('❌ Erro na gravação:', e);
                stopRecording();
                showError('Erro ao gravar áudio. Tente novamente ou use o upload.');
            };
            
            // Solicitar chunks a cada 1 segundo
            mediaRecorder.start(1000);
            isRecording = true;
            
            // Atualizar UI
            recordBtn.classList.add('bg-red-500', 'text-white');
            recordBtn.innerHTML = '<i class="fas fa-stop"></i> Gravando...';
            
            // Timeout de segurança (30s)
            setTimeout(() => {
                if (isRecording) {
                    console.log('⏱️ Timeout de gravação');
                    stopRecording();
                }
            }, 30000);
            
        } else {
            stopRecording();
        }
    } catch (err) {
        console.error('❌ Erro geral na gravação:', err);
        showError('Erro ao manipular gravação. Use o botão de upload como alternativa.');
    }
}

function stopRecording() {
    if (!mediaRecorder) return;
    
    try {
        // Parar gravação
        mediaRecorder.stop();
        isRecording = false;
        
        // Parar todas as tracks
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        
        // Restaurar UI
        recordBtn.classList.remove('bg-red-500', 'text-white');
        recordBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        
    } catch (err) {
        console.error('❌ Erro ao parar gravação:', err);
    }
}

async function sendRecordedAudio() {
    try {
        if (!currentConversation || recordedChunks.length === 0) {
            console.warn('⚠️ Sem conversa ativa ou chunks vazios');
            return;
        }
        
        // Detectar tipo do primeiro chunk
        const mimeType = mediaRecorder.mimeType || recordedChunks[0]?.type || 'audio/ogg';
        console.log(`📦 Preparando áudio: ${mimeType}, ${recordedChunks.length} chunks`);
        
        // Criar blob com todos os chunks
        const blob = new Blob(recordedChunks, { type: mimeType });
        console.log(`📊 Tamanho do blob: ${blob.size} bytes`);
        
        // Verificar tamanho (max ~16MB)
        if (blob.size > 16 * 1024 * 1024) {
            showError('Áudio muito grande. Máximo ~16MB.');
            return;
        }
        
        // Preparar FormData
        const formData = new FormData();
        const ext = mimeType.includes('ogg') ? 'ogg' : 'webm';
        const filename = `voice_${Date.now()}.${ext}`;
        formData.append('file', blob, filename);
        formData.append('content', '🎤 Mensagem de voz');
        
        // Mostrar loading
        recordBtn.disabled = true;
        recordBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        
        try {
            console.log(`📤 Enviando áudio: ${filename}`);
            const resp = await fetch(`${API_BASE_URL}/api/conversations/${currentConversation.id}/voice`, {
                method: 'POST',
                body: formData
            });
            
            const data = await resp.json();
            if (resp.ok) {
                console.log('✅ Áudio enviado com sucesso:', data);
                // Recarregar mensagens
                await loadMessages(currentConversation.id);
            } else {
                throw new Error(data.detail || 'Falha ao enviar áudio');
            }
        } catch (err) {
            console.error('❌ Erro ao enviar áudio:', err);
            showError('Erro ao enviar áudio. Por favor, tente novamente.');
        }
        
    } finally {
        // Limpar estado
        recordedChunks = [];
        recordBtn.disabled = false;
        recordBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        recordBtn.classList.remove('bg-red-500', 'text-white');
    }
}

async function handleAudioFile(e) {
    const file = e.target.files?.[0];
    if (!file || !currentConversation) return;
    try {
        const formData = new FormData();
        formData.append('file', file, file.name || 'audio_upload');
        formData.append('content', '');
        const resp = await fetch(`${API_BASE_URL}/api/conversations/${currentConversation.id}/voice`, {
            method: 'POST',
            body: formData
        });
        const data = await resp.json();
        if (resp.ok) {
            console.log('Áudio enviado via upload:', data);
            await loadMessages(currentConversation.id);
        } else {
            throw new Error(data.detail || 'Falha ao enviar áudio');
        }
    } catch (err) {
        console.error('Erro ao enviar arquivo de áudio:', err);
        alert('Erro ao enviar arquivo de áudio.');
    } finally {
        audioFileInput.value = '';
    }
}

function setupWebSocket() {
    console.log('🔌 Conectando ao WebSocket...');
    
    // Conectar ao servidor Socket.IO
    socket = io(`${API_BASE_URL}`, {
        path: '/socket.io/socket.io',
        transports: ['websocket'],
        upgrade: false
    });
    
    // Eventos do Socket.IO
    socket.on('connect', () => {
        console.log('✅ WebSocket conectado!');
    });
    
    socket.on('disconnect', () => {
        console.log('❌ WebSocket desconectado');
    });
    
    socket.on('welcome', (data) => {
        console.log('👋 Mensagem do servidor:', data.message);
    });
    
    socket.on('new_message', (data) => {
        console.log('📨 Nova mensagem recebida:', data);
        // Se a mensagem é da conversa atual, atualizar
        if (currentConversation && data.conversation_id === currentConversation.id) {
            loadMessages(currentConversation.id);
        }
        // Atualizar lista de conversas
        loadConversations();
    });
    
    socket.on('conversation_update', (data) => {
        console.log('📝 Atualização de conversa:', data);
        loadConversations();
    });
    
    socket.on('typing_status', (data) => {
        console.log('⌨️ Status de digitação:', data);
        if (currentConversation && data.conversation_id === currentConversation.id) {
            updateTypingStatus(data.user, data.is_typing);
        }
    });
    
    socket.on('error', (error) => {
        console.error('🔴 Erro no WebSocket:', error);
    });
}

// Carregar conversas
async function loadConversations() {
    try {
        showLoading(true);
        
        // Chamada real para API
        console.log('🔍 Buscando conversas em:', `${API_BASE_URL}/api/conversations`);
        const response = await fetch(`${API_BASE_URL}/api/conversations`);
        console.log('📡 Status da resposta:', response.status);
        const data = await response.json();
        console.log('📦 Dados recebidos:', data);
        
        if (data.status === 'success') {
            console.log('Raw conversations data:', data.conversations);
            
            conversations = data.conversations.map(conv => {
                // Garantir que timestamp seja válido
                let timestamp;
                try {
                    timestamp = conv.timestamp ? new Date(conv.timestamp) : new Date();
                } catch (e) {
                    console.warn('Invalid timestamp:', conv.timestamp);
                    timestamp = new Date();
                }
                
                return {
                    ...conv,
                    timestamp: timestamp
                };
            });
            
            console.log('Processed conversations:', conversations);
            renderConversations();
            
            if (data.message) {
                console.log('API Info:', data.message);
            }
        } else {
            throw new Error(data.message || 'Erro ao carregar conversas');
        }
        
    } catch (error) {
        console.error('Erro ao carregar conversas:', error);
        console.error('Error details:', {
            message: error.message,
            stack: error.stack,
            response: error.response
        });
        showError('Erro ao carregar conversas: ' + error.message);
        
        // Usar dados mockados em caso de erro
        const mockConversations = [
            {
                id: 1,
                contact: {
                    name: 'João Silva',
                    phone: '+55 11 99999-9999'
                },
                lastMessage: 'Olá, preciso de ajuda com meu documento',
                timestamp: new Date(),
                status: 'open',
                unreadCount: 2
            }
        ];
        
        conversations = mockConversations;
        renderConversations();
    } finally {
        showLoading(false);
    }
}

function renderConversations() {
    conversationsList.innerHTML = '';
    
    if (conversations.length === 0) {
        conversationsList.innerHTML = `
            <div class="p-4 text-center text-gray-500">
                <i class="fas fa-comments text-2xl mb-2"></i>
                <p>Nenhuma conversa encontrada</p>
            </div>
        `;
        return;
    }
    
    conversations.forEach(conversation => {
        const conversationElement = createConversationElement(conversation);
        conversationsList.appendChild(conversationElement);
    });
}

function createConversationElement(conversation) {
    const div = document.createElement('div');
    div.className = `p-4 border-b border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors ${
        currentConversation?.id === conversation.id ? 'bg-blue-50 border-blue-200' : ''
    }`;
    
    const timeAgo = getTimeAgo(conversation.timestamp);
    const statusColor = getStatusColor(conversation.status);
    
    div.innerHTML = `
        <div class="flex items-center justify-between mb-2">
            <h3 class="font-semibold text-gray-800">${conversation.contact.name}</h3>
            <span class="text-xs text-gray-500">${timeAgo}</span>
        </div>
        <p class="text-sm text-gray-600 mb-2 truncate">${conversation.lastMessage}</p>
        <div class="flex items-center justify-between">
            <span class="text-xs px-2 py-1 rounded-full ${statusColor}">${conversation.status}</span>
            ${conversation.unreadCount > 0 ? `
                <span class="bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    ${conversation.unreadCount}
                </span>
            ` : ''}
        </div>
    `;
    
    div.addEventListener('click', () => selectConversation(conversation));
    
    return div;
}

function getStatusColor(status) {
    switch (status) {
        case 'open': return 'bg-yellow-100 text-yellow-800';
        case 'resolved': return 'bg-green-100 text-green-800';
        case 'pending': return 'bg-blue-100 text-blue-800';
        default: return 'bg-gray-100 text-gray-800';
    }
}

function getTimeAgo(timestamp) {
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'Agora';
    if (minutes < 60) return `${minutes}m`;
    if (hours < 24) return `${hours}h`;
    return `${days}d`;
}

function selectConversation(conversation) {
    // Se estava em uma conversa, sair da sala
    if (currentConversation && socket) {
        socket.emit('leave_conversation', { conversation_id: currentConversation.id });
    }
    
    currentConversation = conversation;
    
    // Atualizar UI
    contactName.textContent = conversation.contact.name;
    contactPhone.textContent = conversation.contact.phone;
    conversationStatus.textContent = conversation.status;
    conversationStatus.className = `px-2 py-1 text-xs rounded-full ${getStatusColor(conversation.status)}`;
    
    // Mostrar chat
    chatHeader.classList.remove('hidden');
    messageInput.classList.remove('hidden');
    
    // Carregar mensagens
    loadMessages(conversation.id);
    
    // Atualizar lista de conversas
    renderConversations();
    
    // Entrar na sala da nova conversa
    if (socket) {
        socket.emit('join_conversation', { conversation_id: conversation.id });
    }
}

async function loadMessages(conversationId) {
    try {
        messagesContainer.innerHTML = `
            <div class="text-center text-gray-500 mt-20">
                <i class="fas fa-spinner fa-spin text-2xl mb-2"></i>
                <p>Carregando mensagens...</p>
            </div>
        `;
        
        // Chamada real para API
        console.log('🔄 Carregando mensagens para conversa:', conversationId);
        const response = await fetch(`${API_BASE_URL}/api/conversations/${conversationId}/messages`);
        console.log('📡 Status da resposta:', response.status);
        const data = await response.json();
        console.log('📦 Dados recebidos:', data);
        
        if (data.status === 'success') {
            const messages = data.messages.map(msg => ({
                ...msg,
                timestamp: new Date(msg.timestamp)
            }));
            renderMessages(messages);
            
            if (data.message) {
                console.log('Messages API Info:', data.message);
            }
        } else {
            throw new Error(data.message || 'Erro ao carregar mensagens');
        }
        
    } catch (error) {
        console.error('Erro ao carregar mensagens:', error);
        showError('Erro ao carregar mensagens: ' + error.message);
        
        // Usar dados mockados em caso de erro
        const mockMessages = [
            {
                id: 1,
                content: 'Olá, preciso de ajuda com meu documento',
                sender: 'contact',
                timestamp: new Date(Date.now() - 600000),
                status: 'sent'
            },
            {
                id: 2,
                content: 'Olá! Como posso ajudá-lo?',
                sender: 'user',
                timestamp: new Date(Date.now() - 300000),
                status: 'sent'
            }
        ];
        
        renderMessages(mockMessages);
    }
}

function renderMessages(messages) {
    messagesContainer.innerHTML = '';
    
    messages.forEach(message => {
        const messageElement = createMessageElement(message);
        messagesContainer.appendChild(messageElement);
    });
    
    // Scroll para o final
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function createMessageElement(message) {
    const div = document.createElement('div');
    const isUser = message.sender === 'user';
    
    div.className = `mb-4 flex ${isUser ? 'justify-end' : 'justify-start'}`;
    
    const time = message.timestamp.toLocaleTimeString('pt-BR', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    // Verificar se tem áudio
    let audioHtml = '';
    let messageContent = message.content || '';
    
    // Verificar áudio em attachments ou URL direta
    const hasAudio = message.audio_url || (message.attachments && message.attachments.some(a => a.file_type === 'audio'));
    const audioAttachment = message.attachments?.find(a => a.file_type === 'audio');
    
    // Tentar todas as possíveis URLs de áudio
    const possibleUrls = [
        message.audio_url,                  // URL do nosso backend
        audioAttachment?.local_url,         // URL local processada
        audioAttachment?.data_url,          // URL direta do Chatwoot
        `/media/audio/audio_${message.conversation_id}_${message.id}_*.ogg`  // Padrão do arquivo
    ].filter(Boolean);
    
    console.log('📝 Processando mensagem:', {
        id: message.id,
        conversation_id: message.conversation_id,
        content: messageContent,
        hasAudio,
        attachments: message.attachments,
        possibleUrls
    });
    
    if (hasAudio) {
        // Tentar primeira URL disponível
        const audioUrl = possibleUrls[0];
        if (audioUrl) {
            console.log('🎵 Renderizando áudio:', audioUrl);
            audioHtml = `
                <div class="audio-player mt-2 bg-gray-100 rounded-lg p-2">
                    <audio controls class="w-full">
                        <source src="${audioUrl}" type="audio/ogg">
                        Seu navegador não suporta o elemento de áudio.
                    </audio>
                </div>
            `;
            
            // Se não tem texto, mostrar ícone de áudio
            if (!messageContent) {
                messageContent = '🎵 Mensagem de áudio';
            }
        }
    }
    
    div.innerHTML = `
        <div class="message-bubble ${isUser ? 'bg-blue-600 text-white' : 'bg-white border border-gray-200'} rounded-lg p-3 shadow-sm">
            <p class="text-sm">${messageContent}</p>
            ${audioHtml}
            <div class="text-xs mt-1 ${isUser ? 'text-blue-100' : 'text-gray-500'}">
                ${time}
                ${isUser ? `<i class="fas fa-check ml-1"></i>` : ''}
            </div>
        </div>
    `;
    
    return div;
}

async function sendMessage() {
    const content = messageText.value.trim();
    if (!content || !currentConversation) return;
    
    try {
        // Limpar input
        messageText.value = '';
        messageText.style.height = 'auto';
        
        // Mostrar mensagem imediatamente
        const tempMessage = {
            id: Date.now(),
            content: content,
            sender: 'user',
            timestamp: new Date(),
            status: 'sending'
        };
        
        const messageElement = createMessageElement(tempMessage);
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Enviar mensagem real para API
        const response = await fetch(`${API_BASE_URL}/api/conversations/${currentConversation.id}/messages`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: content
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // Atualizar status da mensagem
            const checkIcon = messageElement.querySelector('.fa-check');
            if (checkIcon) {
                checkIcon.className = 'fas fa-check-double ml-1';
            }
            
            console.log('Mensagem enviada com sucesso:', data.message_id);
        } else {
            throw new Error(data.message || 'Erro ao enviar mensagem');
        }
        
    } catch (error) {
        console.error('Erro ao enviar mensagem:', error);
        showError('Erro ao enviar mensagem: ' + error.message);
        
        // Remover mensagem temporária em caso de erro
        const tempMessage = messagesContainer.querySelector('.message-bubble:last-child');
        if (tempMessage) {
            tempMessage.parentElement.remove();
        }
    }
}

function filterConversations() {
    const searchTerm = searchInput.value.toLowerCase();
    const filteredConversations = conversations.filter(conversation => 
        conversation.contact.name.toLowerCase().includes(searchTerm) ||
        conversation.contact.phone.includes(searchTerm) ||
        conversation.lastMessage.toLowerCase().includes(searchTerm)
    );
    
    // Renderizar conversas filtradas
    conversationsList.innerHTML = '';
    filteredConversations.forEach(conversation => {
        const conversationElement = createConversationElement(conversation);
        conversationsList.appendChild(conversationElement);
    });
}

function showLoading(show) {
    if (show) {
        loadingOverlay.classList.remove('hidden');
    } else {
        loadingOverlay.classList.add('hidden');
    }
}

function showError(message) {
    // TODO: Implementar notificação de erro
    console.error(message);
    alert(message);
}

// Utilitários
function formatPhoneNumber(phone) {
    return phone.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
}

// Exportar para uso global
window.CidadaoAI = {
    loadConversations,
    selectConversation,
    sendMessage
};
