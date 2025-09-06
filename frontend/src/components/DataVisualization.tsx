import React from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface DataVisualizationProps {
  data: Array<Record<string, any>>;
  chartType: string;
  title: string;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

const DataVisualization: React.FC<DataVisualizationProps> = ({ data, chartType, title }) => {
  if (!data || data.length === 0) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: '#666' }}>
        No data to display
      </div>
    );
  }

  const renderChart = () => {
    const keys = Object.keys(data[0]);
    const numericKeys = keys.filter(key => 
      data.some(item => typeof item[key] === 'number')
    );
    const categoryKey = keys.find(key => 
      !numericKeys.includes(key) && typeof data[0][key] === 'string'
    ) || keys[0];

    switch (chartType) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={categoryKey} />
              <YAxis />
              <Tooltip />
              <Legend />
              {numericKeys.map((key, index) => (
                <Line 
                  key={key} 
                  type="monotone" 
                  dataKey={key} 
                  stroke={COLORS[index % COLORS.length]} 
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        );

      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={categoryKey} />
              <YAxis />
              <Tooltip />
              <Legend />
              {numericKeys.map((key, index) => (
                <Bar 
                  key={key} 
                  dataKey={key} 
                  fill={COLORS[index % COLORS.length]} 
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        );

      case 'pie':
        const pieData = data.map((item, index) => ({
          name: item[categoryKey],
          value: item[numericKeys[0]] || 0,
          fill: COLORS[index % COLORS.length],
        }));
        return (
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} (${((percent || 0) * 100).toFixed(0)}%)`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        );

      case 'scatter':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <ScatterChart data={data}>
              <CartesianGrid />
              <XAxis dataKey={numericKeys[0]} type="number" />
              <YAxis dataKey={numericKeys[1]} type="number" />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Scatter dataKey={numericKeys[1]} fill="#8884d8" />
            </ScatterChart>
          </ResponsiveContainer>
        );

      default:
        return <DataTable data={data} />;
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ marginBottom: '20px', fontSize: '24px', fontWeight: 'bold' }}>
        {title}
      </h2>
      {renderChart()}
    </div>
  );
};

const DataTable: React.FC<{ data: Array<Record<string, any>> }> = ({ data }) => {
  const columns = Object.keys(data[0]);

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ backgroundColor: '#f5f5f5' }}>
            {columns.map(column => (
              <th 
                key={column} 
                style={{ 
                  padding: '12px', 
                  textAlign: 'left', 
                  borderBottom: '2px solid #ddd',
                  fontWeight: 'bold'
                }}
              >
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={index} style={{ backgroundColor: index % 2 === 0 ? '#fff' : '#f9f9f9' }}>
              {columns.map(column => (
                <td 
                  key={column} 
                  style={{ 
                    padding: '12px', 
                    borderBottom: '1px solid #ddd' 
                  }}
                >
                  {row[column]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DataVisualization;