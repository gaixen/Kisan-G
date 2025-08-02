import React, { useState } from 'react';
import UploadInput from '../../src/components/UploadInput';
import {diagnoseCrop} from '../../src/services/api';

const CropDoctor: React.FC = () => {
  const [image, setImage] = useState<File | null>(null);
  const [diagnosis, setDiagnosis] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (file: File) => {
    setImage(file);
    setLoading(true);
    const result = await diagnoseCrop(file);
    setDiagnosis(result);
    setLoading(false);
  };

  return (
      <div className="max-w-xl mx-auto p-4 pb-20">
      {/* // properly centre the next text in the middle of the screen. */}
      
      <h2 className="text-xl font-bold mb-4">Diagnose Your Crop Instantly</h2> 
      <UploadInput onUpload={handleUpload} />
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
          </div>
        </div>
      )}
    </div>
  );
};
export default CropDoctor;
