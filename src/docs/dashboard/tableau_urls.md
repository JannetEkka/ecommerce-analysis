# Tableau Dashboard URLs

This document maintains the URLs for all Tableau Public dashboards used in the project.

## Regional Performance Dashboard
- **Public URL**: [YOUR_URL_HERE]
- **Embed URL**: [YOUR_EMBED_URL_HERE]
- **Last Updated**: [DATE]
- **Description**: Shows regional sales performance including total sales, unique customers, and average order value.

## How to Update URLs
1. After making changes in Tableau Public, get the new embed URL
2. Update the URL in:
   - `src/frontend/public/dashboards.html`
   - `src/frontend/src/components/DashboardView.js`

## Embedding Instructions
To embed a new dashboard:

1. In Tableau Public:
   - Click "Share" on your visualization
   - Copy the embed code
   - Extract the URL from the embed code

2. In the code:
   ```javascript
   // Add to dashboards object in DashboardContainer
   const dashboards = {
     regional: 'existing_url',
     newDashboard: 'new_dashboard_url'
   };
   ```

## Dashboard Refresh Schedule
- Data is updated daily at [TIME]
- Manual refresh can be triggered through Tableau Public interface