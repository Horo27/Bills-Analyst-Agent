import { Calendar, DollarSign, Tag, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import { format, isAfter, isBefore } from 'date-fns';

const BillCard = ({ bill, onStatusChange }) => {
  const isOverdue = bill.status === 'pending' && isBefore(new Date(bill.due_date), new Date());
  const isPaid = bill.status === 'paid';
  
  const getStatusIcon = () => {
    if (isPaid) return <CheckCircle className="text-success-500" size={16} />;
    if (isOverdue) return <AlertCircle className="text-error-500" size={16} />;
    return <Clock className="text-warning-500" size={16} />;
  };

  const getStatusColor = () => {
    if (isPaid) return 'bg-success-50 text-success-700 border-success-200';
    if (isOverdue) return 'bg-error-50 text-error-700 border-error-200';
    return 'bg-warning-50 text-warning-700 border-warning-200';
  };

  const handleMarkPaid = () => {
    if (onStatusChange && bill.status === 'pending') {
      onStatusChange(bill.id, 'paid');
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 mb-1">{bill.name}</h3>
          {bill.description && (
            <p className="text-sm text-gray-600 mb-2">{bill.description}</p>
          )}
        </div>
        <div className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor()}`}>
          <div className="flex items-center gap-1">
            {getStatusIcon()}
            {bill.status.charAt(0).toUpperCase() + bill.status.slice(1)}
          </div>
        </div>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex items-center gap-2 text-sm">
          <DollarSign size={14} className="text-gray-400" />
          <span className="font-medium text-gray-900">${bill.amount}</span>
        </div>
        
        <div className="flex items-center gap-2 text-sm">
          <Calendar size={14} className="text-gray-400" />
          <span className="text-gray-600">
            Due: {format(new Date(bill.due_date), 'MMM dd, yyyy')}
          </span>
        </div>
        
        <div className="flex items-center gap-2 text-sm">
          <Tag size={14} className="text-gray-400" />
          <span className="text-gray-600">{bill.category.name}</span>
        </div>
      </div>

      {bill.vendor && (
        <div className="text-sm text-gray-600 mb-3">
          <strong>Vendor:</strong> {bill.vendor}
        </div>
      )}

      {bill.status === 'pending' && (
        <button
          onClick={handleMarkPaid}
          className="w-full py-2 px-3 bg-success-500 text-white rounded-lg hover:bg-success-600 transition-colors text-sm font-medium"
        >
          Mark as Paid
        </button>
      )}
    </div>
  );
};

export default BillCard;