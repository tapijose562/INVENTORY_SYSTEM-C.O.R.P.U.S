export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  is_active: boolean;
  role: string;
}

export interface Product {
  id: number;
  name: string;
  brand: string;
  color_primary: string;
  size: string;
  stock: number;
  price?: number;
  image_url?: string;
  yolo_confidence: number;
}

export interface DetectionResult {
  brand: string;
  color: string;
  size: string;
  text: string;
  confidence: number;
  rgb: any;
  metadata: any;
}

export interface TrainingSession {
  id: number;
  name: string;
  status: string;
  dataset_size: number;
  accuracy?: number;
  loss?: number;
}
