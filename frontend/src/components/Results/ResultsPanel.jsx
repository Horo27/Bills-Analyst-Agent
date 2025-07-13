import { useState, useEffect } from 'react';
import { BarChart3, Calendar, DollarSign, FileText, RefreshCw } from 'lucide-react';
import BillCard from './BillCard';
import SummaryCard from './SummaryCard';
import CategoryChart from './CategoryChart';
import { billsAPI, analyticsAPI } from '../../services/api';

const ResultsPanel = ({ lastChatUpdate }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [bills, setBills] = useState([]);
  const [upcomingBills, setUpcomingBills] = useState([]);
  const [summary, setSummary] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'bills', label: 'All Bills', icon: FileText },
    { id: 'upcoming', label: 'Upcoming', icon: Calendar },
  ];

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    // Refresh data when chat indicates a successful action
    if (lastChatUpdate?.actionSuccessful) {
      loadData();
    }
  }, [lastChatUpdate]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [billsData, upcomingData, summaryData, statsData] = await Promise.all([
        billsAPI.getAll({ limit: 50 }),
        billsAPI.getUpcoming(30),
        analyticsAPI.getSummary(),
        analyticsAPI.getStats(),
      ]);

      setBills(billsData);
      setUpcomingBills(upcomingData.upcoming_bills || []);
      setSummary(summaryData);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBillStatusChange = async (billId, newStatus) => {
    try {
      await billsAPI.update(billId, { status: newStatus });
      loadData(); // Refresh data
    } catch (error) {
      console.error('Failed to update bill status:', error);
    }
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Summary Cards */}
      {summary && stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <SummaryCard
            title="This Month"
            value={`$${summary.total_amount?.toFixed(2) || '0.00'}`}
            subtitle={`${summary.total_bills || 0} bills`}
            icon={DollarSign}
            color="primary"
          />
          <SummaryCard
            title="Upcoming Bills"
            value={stats.upcoming_bills_count || 0}
            subtitle="Next 30 days"
            icon={Calendar}
            color="warning"
          />
          <SummaryCard
            title="Overdue Bills"
            value={stats.overdue_bills_count || 0}
            subtitle="Need attention"
            icon={FileText}
            color="error"
          />
          <SummaryCard
            title="Payment Rate"
            value={`${stats.payment_completion_rate?.toFixed(1) || '0.0'}%`}
            subtitle="This month"
            icon={BarChart3}
            color="success"
          />
        </div>
      )}

      {/* Category Breakdown */}
      {summary?.category_breakdown && (
        <CategoryChart categories={summary.category_breakdown} />
      )}

      {/* Recent Bills */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Recent Bills</h3>
          <button
            onClick={loadData}
            disabled={loading}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {bills.slice(0, 6).map((bill) => (
            <BillCard
              key={bill.id}
              bill={bill}
              onStatusChange={handleBillStatusChange}
            />
          ))}
        </div>
        
        {bills.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            <FileText size={48} className="mx-auto mb-4 text-gray-300" />
            <p>No bills found. Try adding some bills through the chat!</p>
          </div>
        )}
      </div>
    </div>
  );

  const renderBills = () => (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">All Bills</h3>
        <button
          onClick={loadData}
          disabled={loading}
          className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {bills.map((bill) => (
          <BillCard
            key={bill.id}
            bill={bill}
            onStatusChange={handleBillStatusChange}
          />
        ))}
      </div>
      
      {bills.length === 0 && (
        <div className="text-center text-gray-500 py-8">
          <FileText size={48} className="mx-auto mb-4 text-gray-300" />
          <p>No bills found. Try adding some bills through the chat!</p>
        </div>
      )}
    </div>
  );

  const renderUpcoming = () => (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Upcoming Bills (Next 30 Days)</h3>
        <button
          onClick={loadData}
          disabled={loading}
          className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {upcomingBills.map((bill) => (
          <BillCard
            key={bill.id}
            bill={bill}
            onStatusChange={handleBillStatusChange}
          />
        ))}
      </div>
      
      {upcomingBills.length === 0 && (
        <div className="text-center text-gray-500 py-8">
          <Calendar size={48} className="mx-auto mb-4 text-gray-300" />
          <p>No upcoming bills in the next 30 days!</p>
        </div>
      )}
    </div>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderOverview();
      case 'bills':
        return renderBills();
      case 'upcoming':
        return renderUpcoming();
      default:
        return renderOverview();
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header with Tabs */}
      <div className="bg-white border-b">
        <div className="flex items-center justify-between p-4">
          <h2 className="font-semibold text-gray-900">Dashboard</h2>
        </div>
        
        <div className="flex border-b">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600 bg-primary-50'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <Icon size={16} />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto scrollbar-thin p-6">
        {renderContent()}
      </div>
    </div>
  );
};

export default ResultsPanel;