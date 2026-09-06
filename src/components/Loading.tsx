import React from "react";
const Loading = () => {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="flex items-center gap-3">
          <div className="h-6 w-6 animate-spin rounded-full border-4 border-slate-300 border-t-blue-600" />
  
          <span className="text-sm text-slate-600">
            Creating your trip...
          </span>
        </div>
      </div>
    );
  };
  
  export default Loading;