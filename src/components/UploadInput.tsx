import React from "react";

type UploadInputProps = {
  onUpload: (file: File) => void;
};

const UploadInput: React.FC<UploadInputProps> = ({ onUpload }) => (
  <div className="flex flex-col items-center">
    <input
      type="file"
      accept="image/*"
      onChange={e => {
        if (e.target.files && e.target.files[0]) {
          onUpload(e.target.files[0]);
        }
      }}
      className="hidden"
      id="upload-input"
    />
    <label htmlFor="upload-input"
      className="inline-flex items-center justify-center w-[460px] h-[50px] bg-primary text-white rounded cursor-pointer hover:bg-green-600">
      Upload Crop Image
    </label>
    <small className="text-gray-500 mt-2">JPG, PNG only. Clear, close-up photo recommended.</small>
  </div>
);
export default UploadInput;
