import React, { useEffect, useRef } from 'react';

const TableauDashboard = ({ url }) => {
  const vizRef = useRef(null);
  let viz = null;

  useEffect(() => {
    // Load the visualization
    const initViz = () => {
      const options = {
        hideTabs: true,
        hideToolbar: true,
        width: '100%',
        height: '800px'
      };

      // If a viz already exists, dispose of it first
      if (viz) {
        viz.dispose();
      }

      // Create new viz
      viz = new window.tableau.Viz(vizRef.current, url, options);
    };

    // Initialize viz when the component mounts
    initViz();

    // Cleanup when component unmounts
    return () => {
      if (viz) {
        viz.dispose();
      }
    };
  }, [url]);

  return (
    <div ref={vizRef} style={{ width: '100%', height: '800px' }} />
  );
};

// Main Dashboard Container
const DashboardContainer = () => {
  const dashboards = {
    regional: 'YOUR_REGIONAL_DASHBOARD_URL',
    // Add more dashboard URLs as needed
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-6">E-commerce Analytics</h1>
      
      {/* Regional Performance Dashboard */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Regional Performance</h2>
        <div className="border rounded-lg shadow-lg">
          <TableauDashboard url={dashboards.regional} />
        </div>
      </div>

      {/* Additional dashboards can be added here */}
    </div>
  );
};

export default DashboardContainer;