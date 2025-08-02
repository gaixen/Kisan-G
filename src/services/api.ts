import axios from "axios";

// Mock data for development - replace with real API calls when backend is ready
const mockMarketData = [
  { commodity: "Wheat", date: "2024-01-29", price: 2150, trend: 1 },
  { commodity: "Rice", date: "2024-01-29", price: 3200, trend: -1 },
  { commodity: "Tomato", date: "2024-01-29", price: 45, trend: 0 },
  { commodity: "Onion", date: "2024-01-29", price: 28, trend: 1 },
];

const mockSchemes = [
  {
    id: "pm-kisan",
    title: "PM-KISAN Samman Nidhi",
    description: "Direct income support of ₹6000 per year to small farmer families",
    eligibility: "Landholding up to 2 hectares",
    eligible: true
  },
  {
    id: "crop-insurance",
    title: "Pradhan Mantri Fasal Bima Yojana",
    description: "Crop insurance scheme providing coverage against crop loss",
    eligibility: "All farmers growing notified crops",
    eligible: true
  }
];

export const diagnoseCrop = async (image: File) => {
  try {
    const formData = new FormData();
    formData.append('image', image);
    const { data } = await axios.post("/api/crop-diagnosis", formData);
    return data;
  } catch (error) {
    // Mock response for development
    return {
      label: "Leaf Blight",
      confidence: 0.85,
      remedy: "Apply copper-based fungicide and ensure proper drainage. Remove affected leaves.",
      moreInfo: "https://example.com/leaf-blight-info",
      referenceImages: []
    };
  }
};

export const getMarketData = async () => {
  try {
    const { data } = await axios.get("/api/market");
    return data;
  } catch (error) {
    // Return mock data for development
    return mockMarketData;
  }
};

export const searchSchemes = async (query: string, user: any) => {
  try {
    const { data } = await axios.post("/api/schemes/search", { query, user });
    return data;
  } catch (error) {
    // Return mock data for development
    return mockSchemes.filter(scheme => 
      scheme.title.toLowerCase().includes(query.toLowerCase()) ||
      scheme.description.toLowerCase().includes(query.toLowerCase())
    );
  }
};

export const applyScheme = async (schemeId: string, user: any) => {
  try {
    const { data } = await axios.post("/api/schemes/apply", { schemeId, user });
    return data;
  } catch (error) {
    // Mock response for development
    return {
      message: "Application submitted successfully! You will receive updates via SMS."
    };
  }
};

// ...Other API calls
