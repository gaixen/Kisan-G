import React, { useContext } from 'react';
import { AppContext } from '../../src/hooks/AppContext';
import CropCard from '../../src/components/CropCard';
import WeatherWidget from '../../src/components/WeatherWidget';
import VoiceAssistantInput from '../../src/components/VoiceAssistantInput';

const Dashboard: React.FC = () => {
  const { user, crops, highlights } = useContext(AppContext);

  return (
    <main className="p-4 pb-20 max-w-3xl mx-auto">
      <section className="flex flex-col gap-3">
        <h1 className="text-2xl font-bold mb-1">
          Hi {user?.name || 'Farmer'},
        </h1>
        <WeatherWidget />
        <div className="bg-blue-50 rounded-xl p-3 mb-3">
          {highlights.map((h, idx) => (
            <div key={idx} className="text-blue-900">{h}</div>
          ))}
        </div>
        <div className="grid grid-cols-3 gap-3">
          {crops.map((crop, idx) =>
            <CropCard key={idx} crop={crop} />
          )}
        </div>
        <section className="my-6">
          <div className="flex items-center gap-2">
            <span className="font-medium">Market Highlights</span>
            {/* Show relevant icon or stats */}
          </div>
          {/* Market stats as per design */}
        </section>
        <section>
          <VoiceAssistantInput />
        </section>
      </section>
    </main>
  );
};
export default Dashboard;
