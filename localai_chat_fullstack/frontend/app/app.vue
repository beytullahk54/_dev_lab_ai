<template>
  <div class="chat-container">
    <div class="chat-header">
      <h1>Chat</h1>
    </div>
    
    <div class="messages" ref="messagesContainer">
      <div 
        v-for="(message, index) in messages" 
        :key="index"
        :class="['message', message.sender]"
      >
        <div 
          class="message-content"
          v-if="message.sender === 'user'"
        >
          {{ message.text }}
        </div>
        <div 
          class="message-content markdown-content"
          v-else
          v-html="renderMarkdown(message.text)"
        ></div>
      </div>
    </div>
    
    <div class="input-area">
      <input 
        v-model="newMessage"
        @keyup.enter="sendMessage"
        type="text" 
        placeholder="Mesajınızı yazın..."
        class="message-input"
      />
      <button @click="sendMessage" class="send-button">
        Gönder
      </button>
    </div>
  </div>
</template>

<script setup>
    import { ref, nextTick } from 'vue'
    import { marked } from 'marked'

    // Markdown yapılandırması
    marked.setOptions({
      breaks: true,  // Satır sonlarını <br> olarak işle
      gfm: true      // GitHub Flavored Markdown
    })

    // Markdown render fonksiyonu
    const renderMarkdown = (text) => {
      if (!text) return ''
      return marked(text)
    }

    const messages = ref([
      { text: 'Merhaba! Nasıl yardımcı olabilirim?', sender: 'bot' }
    ])

    const newMessage = ref('merhaba')
    const messagesContainer = ref(null)

    const sendMessage = async () => {
      if (newMessage.value.trim()) {
        const userQuestion = newMessage.value
        
        // Kullanıcı mesajını ekle
        messages.value.push({
          text: userQuestion,
          sender: 'user'
        })
        
        newMessage.value = ''
        
        // Scroll to bottom
        nextTick(() => {
          if (messagesContainer.value) {
            messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
          }
        })
        
        // Bot mesajı için placeholder ekle
        const botMessageIndex = messages.value.length
        messages.value.push({
          text: '',
          sender: 'bot'
        })
        
        try {

          // Streaming API'ye istek at
          const response = await fetch('http://localhost:8000/ask/stream', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              question: userQuestion,
              max_length: 150
            })
          })
          
          if (!response.ok) {
            let errorMessage = "API isteği başarısız"
            alert(errorMessage)
            throw new Error(errorMessage)
          }
          
          const reader = response.body.getReader()
      
          const decoder = new TextDecoder()
          
          // Streaming verileri oku
          while (true) {
            const { done, value } = await reader.read()

           // console.log(decoder.decode(value))
            
            if (done) break
            
            // Gelen veriyi decode et
            const chunk = decoder.decode(value)
            console.log(chunk)
            const lines = chunk.split('\n')
            
            // Her satırı işle
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6))
                  
                  if (data.error) {
                    messages.value[botMessageIndex].text = `Hata: ${data.error}`
                    break
                  }
                  
                  if (data.chunk) {
                    // Chunk'ı mevcut mesaja ekle
                    messages.value[botMessageIndex].text += data.chunk
                    
                    // Her chunk'tan sonra scroll
                    nextTick(() => {
                      if (messagesContainer.value) {
                        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
                      }
                    })
                  }
                  
                  if (data.done) {
                    break
                  }
                } catch (e) {
                  console.error('JSON parse hatası:', e)
                }
              }
            }
          }
        } catch (error) {
          console.error('API Hatası:', error)
          messages.value[botMessageIndex].text = 'Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.'
        }
        
        // Final scroll
        nextTick(() => {
          if (messagesContainer.value) {
            messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
          }
        })
      }
    }
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 800px;
  margin: 0 auto;
  background: #f5f5f5;
}

.chat-header {
  background: #4a90e2;
  color: white;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.chat-header h1 {
  font-size: 24px;
  font-weight: 500;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  display: flex;
  max-width: 70%;
}

.message.user {
  align-self: flex-end;
}

.message.bot {
  align-self: flex-start;
}

.message-content {
  padding: 12px 16px;
  border-radius: 18px;
  word-wrap: break-word;
}

.message.user .message-content {
  background: #4a90e2;
  color: white;
}

.message.bot .message-content {
  background: white;
  color: #333;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.input-area {
  display: flex;
  gap: 10px;
  padding: 20px;
  background: white;
  border-top: 1px solid #e0e0e0;
}

.message-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 24px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.message-input:focus {
  border-color: #4a90e2;
}

.send-button {
  padding: 12px 24px;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 24px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.2s;
}

.send-button:hover {
  background: #357abd;
}

.send-button:active {
  transform: scale(0.98);
}

/* Markdown İçeriği Stilleri */
.markdown-content {
  line-height: 1.6;
}

.markdown-content p {
  margin: 0.5em 0;
}

.markdown-content p:first-child {
  margin-top: 0;
}

.markdown-content p:last-child {
  margin-bottom: 0;
}

.markdown-content code {
  background: #f4f4f4;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
  color: #e83e8c;
}

.markdown-content pre {
  background: #2d2d2d;
  color: #f8f8f2;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
}

.markdown-content pre code {
  background: transparent;
  padding: 0;
  color: #f8f8f2;
  font-size: 0.85em;
}

.markdown-content ul,
.markdown-content ol {
  margin: 8px 0;
  padding-left: 24px;
}

.markdown-content li {
  margin: 4px 0;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3,
.markdown-content h4 {
  margin: 12px 0 8px 0;
  font-weight: 600;
}

.markdown-content h1 {
  font-size: 1.5em;
}

.markdown-content h2 {
  font-size: 1.3em;
}

.markdown-content h3 {
  font-size: 1.1em;
}

.markdown-content blockquote {
  border-left: 3px solid #4a90e2;
  padding-left: 12px;
  margin: 8px 0;
  color: #666;
  font-style: italic;
}

.markdown-content strong {
  font-weight: 600;
}

.markdown-content em {
  font-style: italic;
}

.markdown-content a {
  color: #4a90e2;
  text-decoration: none;
}

.markdown-content a:hover {
  text-decoration: underline;
}

.markdown-content table {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
}

.markdown-content th,
.markdown-content td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.markdown-content th {
  background: #f4f4f4;
  font-weight: 600;
}
</style>
