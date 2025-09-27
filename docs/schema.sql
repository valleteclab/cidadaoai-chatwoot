-- CidadaoAI Chatwoot Database Schema
-- Database: PostgreSQL (Supabase)

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- User profiles table
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),
    cpf VARCHAR(14),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chatwoot_conversation_id INTEGER UNIQUE NOT NULL,
    user_id VARCHAR(255) REFERENCES user_profiles(user_id),
    status VARCHAR(50) DEFAULT 'open',
    channel VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    chatwoot_message_id INTEGER UNIQUE NOT NULL,
    content TEXT NOT NULL,
    message_type VARCHAR(20) NOT NULL, -- 'incoming' or 'outgoing'
    sender_type VARCHAR(20) NOT NULL, -- 'user' or 'agent' or 'bot'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI interactions table
CREATE TABLE ai_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    input_text TEXT NOT NULL,
    output_text TEXT NOT NULL,
    intent VARCHAR(100),
    confidence DECIMAL(3,2),
    entities JSONB,
    model_used VARCHAR(100),
    processing_time INTEGER, -- milliseconds
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Analytics table
CREATE TABLE analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    user_id VARCHAR(255),
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Knowledge base table
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    tags TEXT[],
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Feedback table
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_conversations_chatwoot_id ON conversations(chatwoot_conversation_id);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_chatwoot_id ON messages(chatwoot_message_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

CREATE INDEX idx_ai_interactions_message_id ON ai_interactions(message_id);
CREATE INDEX idx_ai_interactions_intent ON ai_interactions(intent);
CREATE INDEX idx_ai_interactions_created_at ON ai_interactions(created_at);

CREATE INDEX idx_analytics_event_type ON analytics(event_type);
CREATE INDEX idx_analytics_user_id ON analytics(user_id);
CREATE INDEX idx_analytics_created_at ON analytics(created_at);

CREATE INDEX idx_knowledge_base_category ON knowledge_base(category);
CREATE INDEX idx_knowledge_base_is_active ON knowledge_base(is_active);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_profiles_updated_at 
    BEFORE UPDATE ON user_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at 
    BEFORE UPDATE ON conversations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_base_updated_at 
    BEFORE UPDATE ON knowledge_base 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) policies can be added here if needed
-- ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
-- etc.

-- Sample data for knowledge base (optional)
INSERT INTO knowledge_base (title, content, category, tags) VALUES
('Como solicitar segunda via de documentos', 
 'Para solicitar a segunda via de documentos, você deve acessar o portal do cidadão e seguir os seguintes passos: 1) Faça login com seu CPF, 2) Selecione "Documentos", 3) Escolha o documento desejado, 4) Pague a taxa correspondente.',
 'documentos',
 ARRAY['segunda via', 'documentos', 'portal do cidadão']
),
('Horário de funcionamento dos órgãos públicos',
 'Os órgãos públicos municipais funcionam de segunda a sexta-feira, das 8h às 17h, com intervalo para almoço das 12h às 13h. Alguns serviços específicos podem ter horários diferenciados.',
 'atendimento',
 ARRAY['horário', 'funcionamento', 'atendimento']
),
('Como agendar consulta na saúde pública',
 'Para agendar consultas no SUS, você pode: 1) Ligar para a central de agendamento, 2) Comparecer presencialmente na UBS mais próxima, 3) Usar o aplicativo oficial do município.',
 'saude',
 ARRAY['agendamento', 'consulta', 'SUS', 'saúde']
);
