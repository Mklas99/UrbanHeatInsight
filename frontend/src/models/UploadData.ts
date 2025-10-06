// Define the UploadedData type
export interface UploadedData {
  fileName: string;
  fileSize: string;
  uploadTime: string;
  format: string;
  stats: {
    rowCount: number;
    columnCount: number;
    dataTypes: Record<string, string>;
    missingValues: Record<string, number>;
    memoryUsage: string;
  };
  data: Record<string, any>[];
  processedData: Record<string, any>[] | null;
}