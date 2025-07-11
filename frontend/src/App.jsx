import { useState } from 'react';
import { Home } from 'lucide-react';
import ChatPanel from './components/Chat/ChatPanel';
import ResultsPanel from './components/Results/ResultsPanel';

function App() {
  const [lastChatUpdate, setLastChatUpdate] = useState(null);

  const handleChatDataUpdate = (updateData) => {
    setLastChatUpdate({
      ...updateData,
      timestamp: Date.now(),
    });
  };

  return (
    <div className="h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary-500 text-white rounded-lg">
            <Home size={20} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">
              Smart Home Expense & Maintenance Analyst
            </h1>
            <p className="text-sm text-gray-600">
              Manage your household expenses and maintenance tasks with AI assistance
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Panel - Left Side */}
        <div className="w-1/2 border-r border-gray-200">
          <ChatPanel onDataUpdate={handleChatDataUpdate} />
        </div>

        {/* Results Panel - Right Side */}
        <div className="w-1/2">
          <ResultsPanel lastChatUpdate={lastChatUpdate} />
        </div>
      </div>
    </div>
  );
}

export default App;