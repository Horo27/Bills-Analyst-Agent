import { User, Bot } from 'lucide-react';
import { format } from 'date-fns';

const ChatMessage = ({ message, timestamp }) => {
  const isUser = message.type === 'human';
  
  return (
    <div className={`flex gap-3 p-4 ${isUser ? 'bg-gray-50' : 'bg-white'}`}>
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isUser ? 'bg-primary-500 text-white' : 'bg-gray-200 text-gray-600'
      }`}>
        {isUser ? <User size={16} /> : <Bot size={16} />}
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-medium text-sm text-gray-900">
            {isUser ? 'You' : 'Smart Home Assistant'}
          </span>
          {timestamp && (
            <span className="text-xs text-gray-500">
              {format(new Date(timestamp), 'HH:mm')}
            </span>
          )}
        </div>
        
        <div className="text-gray-800 whitespace-pre-wrap break-words">
          {message.content}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;