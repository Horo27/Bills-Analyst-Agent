import { useState, useEffect, useRef } from 'react';
import { MessageSquare, Trash2, AlertCircle } from 'lucide-react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { agentAPI } from '../../services/api';

const ChatPanel = ({ onDataUpdate }) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Load conversation history on mount
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const sessionId = localStorage.getItem('sessionId');
      if (sessionId) {
        const history = await agentAPI.getHistory(sessionId);
        if (history.history && history.history.length > 0) {
          setMessages(history.history);
        }
      }
    } catch (error) {
      console.error('Failed to load chat history:', error);
      // Don't show error for history loading failure
    }
  };

  const handleSendMessage = async (message) => {
    // Clear any previous errors
    setError(null);
    
    // Add user message immediately
    const userMessage = {
      type: 'human',
      content: message,
      timestamp: new Date().toISOString(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await agentAPI.chat(message);
      
      // Add AI response
      const aiMessage = {
        type: 'ai',
        content: response.response,
        timestamp: response.timestamp || new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, aiMessage]);

      // Trigger data update in parent component
      if (onDataUpdate) {
        onDataUpdate({
          intent: response.intent,
          actionSuccessful: response.action_successful,
        });
      }
      
    } catch (error) {
      console.error('Chat error:', error);
      
      let errorMessage = 'Sorry, I encountered an error. Please try again.';
      
      if (error.code === 'ECONNABORTED') {
        errorMessage = 'Request timed out. Please check if the backend server is running.';
      } else if (error.response?.status === 500) {
        errorMessage = 'Server error. Please try again later.';
      } else if (!error.response) {
        errorMessage = 'Cannot connect to server. Please make sure the backend is running on http://localhost:8000';
      }
      
      const aiErrorMessage = {
        type: 'ai',
        content: errorMessage,
        timestamp: new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, aiErrorMessage]);
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = async () => {
    try {
      const sessionId = localStorage.getItem('sessionId');
      if (sessionId) {
        await agentAPI.clearSession(sessionId);
      }
      setMessages([]);
      setError(null);
      localStorage.removeItem('sessionId');
    } catch (error) {
      console.error('Failed to clear chat:', error);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-white">
        <div className="flex items-center gap-2">
          <MessageSquare className="text-primary-500" size={20} />
          <h2 className="font-semibold text-gray-900">Smart Home Assistant</h2>
        </div>
        <button
          onClick={handleClearChat}
          className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          title="Clear conversation"
        >
          <Trash2 size={16} />
        </button>
      </div>

      {/* Connection Status */}
      {error && (
        <div className="p-3 bg-error-50 border-b border-error-200">
          <div className="flex items-center gap-2 text-error-700">
            <AlertCircle size={16} />
            <span className="text-sm">Connection issue detected. Make sure the backend server is running.</span>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center max-w-md px-4">
              <MessageSquare size={48} className="mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-medium mb-2">Welcome to Smart Home Assistant</p>
              <p className="text-sm">
                Ask me about your bills, expenses, or maintenance tasks.
                <br />
                I can help you add bills, get summaries, and track upcoming payments.
              </p>
              <div className="mt-4 text-xs text-gray-400">
                <p>Try saying:</p>
                <ul className="mt-2 space-y-1">
                  <li>"Add a bill: Electric $120 due July 15th"</li>
                  <li>"Show me my monthly summary"</li>
                  <li>"What bills are due soon?"</li>
                </ul>
              </div>
            </div>
          </div>
        ) : (
          <div className="divide-y">
            {messages.map((message, index) => (
              <ChatMessage
                key={index}
                message={message}
                timestamp={message.timestamp}
              />
            ))}
            {isLoading && (
              <div className="flex gap-3 p-4 bg-white">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-sm text-gray-900">Smart Home Assistant</span>
                  </div>
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
};

export default ChatPanel;