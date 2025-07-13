import { TrendingUp, TrendingDown, DollarSign, FileText, Calendar } from 'lucide-react';

const SummaryCard = ({ title, value, subtitle, trend, icon: Icon, color = 'primary' }) => {
  const colorClasses = {
    primary: 'bg-primary-50 text-primary-600 border-primary-200',
    success: 'bg-success-50 text-success-600 border-success-200',
    warning: 'bg-warning-50 text-warning-600 border-warning-200',
    error: 'bg-error-50 text-error-600 border-error-200',
  };

  const getTrendIcon = () => {
    if (trend > 0) return <TrendingUp size={16} className="text-success-500" />;
    if (trend < 0) return <TrendingDown size={16} className="text-error-500" />;
    return null;
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-3">
        <div className={`p-2 rounded-lg border ${colorClasses[color]}`}>
          {Icon && <Icon size={20} />}
        </div>
        {trend !== undefined && (
          <div className="flex items-center gap-1">
            {getTrendIcon()}
            <span className={`text-sm font-medium ${
              trend > 0 ? 'text-success-600' : trend < 0 ? 'text-error-600' : 'text-gray-600'
            }`}>
              {trend > 0 ? '+' : ''}{trend}%
            </span>
          </div>
        )}
      </div>
      
      <div>
        <h3 className="text-2xl font-bold text-gray-900 mb-1">{value}</h3>
        <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
        {subtitle && (
          <p className="text-xs text-gray-500">{subtitle}</p>
        )}
      </div>
    </div>
  );
};

export default SummaryCard;