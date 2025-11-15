import React, { createContext, useContext, useState } from 'react';

interface TabsContextType {
  activeTab: string;
  setActiveTab: (value: string) => void;
}

const TabsContext = createContext<TabsContextType | undefined>(undefined);

export const Tabs = ({ 
  children, 
  defaultValue, 
  className = '' 
}: { 
  children: React.ReactNode; 
  defaultValue: string;
  className?: string;
}) => {
  const [activeTab, setActiveTab] = useState(defaultValue);
  
  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className={className}>
        {children}
      </div>
    </TabsContext.Provider>
  );
};

export const TabsList = ({ children, className = '' }: { children: React.ReactNode; className?: string }) => {
  return (
    <div className={`inline-flex h-12 items-center justify-center rounded-xl bg-gradient-to-r from-gray-50 to-slate-50 border-2 border-gray-200 p-1.5 shadow-sm ${className}`}>
      {children}
    </div>
  );
};

export const TabsTrigger = ({ 
  children, 
  value, 
  className = '' 
}: { 
  children: React.ReactNode; 
  value: string;
  className?: string;
}) => {
  const context = useContext(TabsContext);
  if (!context) throw new Error('TabsTrigger must be used within Tabs');
  
  const { activeTab, setActiveTab } = context;
  const isActive = activeTab === value;
  
  return (
    <button
      onClick={() => setActiveTab(value)}
      className={`inline-flex items-center justify-center whitespace-nowrap rounded-lg px-6 py-2.5 text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 ${
        isActive 
          ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg transform scale-105' 
          : 'bg-white text-gray-700 hover:bg-gradient-to-r hover:from-indigo-50 hover:to-purple-50 hover:text-indigo-700 shadow-sm'
      } ${className}`}
    >
      {children}
    </button>
  );
};

export const TabsContent = ({ 
  children, 
  value, 
  className = '' 
}: { 
  children: React.ReactNode; 
  value: string;
  className?: string;
}) => {
  const context = useContext(TabsContext);
  if (!context) throw new Error('TabsContent must be used within Tabs');
  
  const { activeTab } = context;
  
  if (activeTab !== value) return null;
  
  return (
    <div className={`mt-2 ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 ${className}`}>
      {children}
    </div>
  );
};

