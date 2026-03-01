export interface Product {
  id: number;
  name: string;
  category: string;
  description: string;
  price: number;
  image: string;
}

export interface Message {
  id: string;
  role: "user" | "agent";
  text: string;
  products: Product[];
}

export interface ChatRequest {
  query: string;
  session_id: string;
}

export interface ChatResponse {
  text: string;
  products: Product[];
}
