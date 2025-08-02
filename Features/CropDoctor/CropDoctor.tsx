import React, { useState } from 'react';
import UploadInput from '../../src/components/UploadInput';
import {diagnoseCrop} from '../../src/services/api';
import axios from 'axios';

const CropDoctor: React.FC = () => {
  const [image, setImage] = useState<File | null>(null);
  const [video, setVideo] = useState<File | null>(null);
  const [diagnosis, setDiagnosis] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [uploadType, setUploadType] = useState<'image' | 'video'>('image');

  const handleUpload = async (file: File) => {
    setImage(file);
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await axios.post('/upload-crop-image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      const result = {
        label: response.data.predicted_disease,
        confidence: response.data.confidence,
        remedy: response.data.solution,
        moreInfo: '#',
        referenceImages: []
      };
      setDiagnosis(result);
    } catch (error) {
      console.error('Error uploading image:', error);
      // Fallback to existing API
      const result = await diagnoseCrop(file);
      setDiagnosis(result);
    }
    setLoading(false);
  };

  const handleVideoUpload = async (file: File) => {
    setVideo(file);
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await axios.post('/upload-crop-video', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      const result = {
        label: response.data.predicted_disease,
        confidence: response.data.confidence,
        remedy: response.data.solution,
        moreInfo: '#',
        referenceImages: []
      };
      setDiagnosis(result);
    } catch (error) {
      console.error('Error uploading video:', error);
      alert('Failed to process video.');
    }
    setLoading(false);
  };

  const verifyWithOfficer = async () => {
    try {
      await axios.post('/api/whatsapp/send', {
        phone_number: '1234567890',  // Mock number
        message: `Verification request: ${diagnosis.label}. Confidence: ${Math.round(diagnosis.confidence * 100)}%`
      });
      alert('Verification request sent via WhatsApp.');
    } catch (error) {
      console.error('Error sending WhatsApp message:', error);
      alert('Failed to send verification request.');
    }
  };

  return (
      <div className="max-w-xl mx-auto p-4 pb-20">
      {/* // properly centre the next text in the middle of the screen. */}
      
      <h2 className="text-xl font-bold mb-4">Diagnose Your Crop Instantly</h2>
      
      <div className="mb-4">
        <div className="flex gap-4 mb-3">
          <button
            onClick={() => setUploadType('image')}
            className={`px-4 py-2 rounded ${uploadType === 'image' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
          >
            Upload Image
          </button>
          <button
            onClick={() => setUploadType('video')}
            className={`px-4 py-2 rounded ${uploadType === 'video' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
          >
            Upload Video
          </button>
        </div>
        
        {uploadType === 'image' ? (
          <UploadInput onUpload={handleUpload} />
        ) : (
          <div>
            <input
              type="file"
              accept="video/*"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleVideoUpload(file);
              }}
              className="border p-2 rounded w-full"
            />
          </div>
        )}
      </div>
      {loading && <div className="mt-4">Diagnosing... Please wait.</div>}
      {diagnosis && (
        <div className="bg-white rounded-xl shadow mt-4 p-4">
          <p className="text-lg font-semibold">
            {diagnosis.label} ({Math.round(diagnosis.confidence * 100)}% confident)
          </p>
          <div className="flex gap-2 mt-2">
            {diagnosis.referenceImages?.map((src: string, i: number) => (
              <img key={i} className="w-20 h-20 object-cover rounded" src={src} alt="reference" />
            ))}
          </div>
          <div className="mt-2">
            <p className="font-bold text-green-700">Suggested Remedy:</p>
            <p>{diagnosis.remedy}</p>
            <a href={diagnosis.moreInfo} className="text-primary underline" target="_blank" rel="noopener">Learn More</a>
            <button
              className="bg-blue-500 text-white mt-4 px-4 py-2 rounded"
              onClick={verifyWithOfficer}
            >
              Verify with Local Officer
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
export default CropDoctor;
