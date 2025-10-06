export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const calculateHeatIndex = (temp: number, humidity: number): number => {
  // Simple mock heat index calculation
  return (temp + (humidity/100) * 10).toFixed(1) as unknown as number;
};

export const generateMockData = (count: number) => {
  const data = [];
  for (let i = 0; i < count; i++) {
    data.push({
      id: i + 1,
      latitude: (48.2 + Math.random() * 0.1).toFixed(6),
      longitude: (16.3 + Math.random() * 0.1).toFixed(6),
      temperature: (20 + Math.random() * 15).toFixed(1),
      humidity: (30 + Math.random() * 50).toFixed(1),
      timestamp: new Date(Date.now() - Math.random() * 30 * 86400000).toISOString(),
      sensor_id: Math.floor(1000 + Math.random() * 9000),
      location_name: `Location ${String.fromCharCode(65 + Math.floor(Math.random() * 26))}`,
      measurement_quality: ['High', 'Medium', 'Low'][Math.floor(Math.random() * 3)]
    });
  }
  return data;
};