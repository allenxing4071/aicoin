'use client';

interface ModelCardProps {
  model: {
    name: string;
    slug?: string;
    value: number;
    change: number;
    color: string;
    icon?: string;
  };
}

export default function ModelCard({ model }: ModelCardProps) {
  const isPositive = model.change >= 0;
  
  const handleClick = () => {
    if (model.slug) {
      window.location.href = `/models/${model.slug}`;
    }
  };

  return (
    <div onClick={handleClick} className="bg-white rounded-lg px-4 py-2 border-2 border-gray-200 hover:border-gray-300 transition-all cursor-pointer group hover:shadow-md flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <div 
          className="w-8 h-8 rounded-lg flex items-center justify-center text-xl group-hover:scale-110 transition-transform flex-shrink-0"
          style={{ 
            backgroundColor: model.color + '15',
            border: `1px solid ${model.color}40`
          }}
        >
          {model.icon || model.name.charAt(0)}
        </div>
        <div className="text-[10px] text-gray-500 font-mono uppercase tracking-wider truncate">
          {model.name}
        </div>
      </div>
      
      <div className="flex items-center space-x-4">
        <div className="text-gray-900 text-base font-bold">
          ${model.value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </div>
        <div className={`text-sm font-bold flex items-center ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
          {isPositive ? '+' : ''}{model.change.toFixed(2)}%
          <div 
            className="w-2 h-2 rounded-full ml-2" 
            style={{ backgroundColor: model.color, boxShadow: `0 0 8px ${model.color}` }} 
          />
        </div>
      </div>
    </div>
  );
}
