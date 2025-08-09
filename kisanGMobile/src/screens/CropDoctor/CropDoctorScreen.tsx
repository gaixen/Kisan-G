import React, { useState } from 'react';
import { View, StyleSheet, Image, ScrollView } from 'react-native';
import { Text, Button, Card, ActivityIndicator, MD2Colors } from 'react-native-paper';
import { launchCamera, launchImageLibrary, Asset } from 'react-native-image-picker';
import { analyzeCrop } from '../../services/api';

const CropDoctorScreen = () => {
  const [image, setImage] = useState<Asset | null>(null);
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSelectImage = (source: 'camera' | 'library') => {
    const options = {
      mediaType: 'photo',
      quality: 1,
    } as const;

    const callback = (response: any) => {
      if (response.didCancel) {
        console.log('User cancelled image picker');
      } else if (response.errorCode) {
        setError('ImagePicker Error: ' + response.errorMessage);
      } else {
        setImage(response.assets[0]);
        setAnalysis(null); // Clear previous analysis
        setError(null);
      }
    };

    if (source === 'camera') {
      launchCamera(options, callback);
    } else {
      launchImageLibrary(options, callback);
    }
  };

  const handleAnalyze = async () => {
    if (!image || !image.uri) {
      setError('Please select an image first.');
      return;
    }

    setLoading(true);
    setError(null);
    setAnalysis(null);

    const formData = new FormData();
    formData.append('file', {
      uri: image.uri,
      name: image.fileName || 'photo.jpg',
      type: image.type || 'image/jpeg',
    });
    formData.append('query', 'Analyze the provided image for crop diseases.');

    try {
      const res = await analyzeCrop(formData);
      setAnalysis(res.data);
    } catch (err) {
      console.error(err);
      setError('Failed to analyze crop. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Crop Doctor</Text>
        <Text style={styles.subtitle}>Upload an image to diagnose your crop</Text>
      </View>

      <View style={styles.controls}>
        <Button icon="camera" mode="contained" onPress={() => handleSelectImage('camera')}>
          Use Camera
        </Button>
        <Button icon="image-album" mode="outlined" onPress={() => handleSelectImage('library')} style={styles.libraryButton}>
          From Gallery
        </Button>
      </View>

      {image && image.uri && (
        <View style={styles.previewContainer}>
          <Image source={{ uri: image.uri }} style={styles.preview} />
          <Button mode="contained" onPress={handleAnalyze} disabled={loading} style={styles.analyzeButton}>
            Analyze Crop
          </Button>
        </View>
      )}

      {loading && <ActivityIndicator animating={true} color={MD2Colors.green800} size="large" style={styles.loader} />}

      {error && <Text style={styles.error}>{error}</Text>}

      {analysis && (
        <Card style={styles.resultsCard}>
          <Card.Title title="Analysis Report" />
          <Card.Content>
            <Text style={styles.resultText}>{analysis.final_report || 'No detailed report available.'}</Text>
          </Card.Content>
        </Card>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  subtitle: {
    textAlign: 'center',
    color: 'gray',
    marginTop: 4,
  },
  controls: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingHorizontal: 20,
  },
  libraryButton: {
    
  },
  previewContainer: {
    alignItems: 'center',
    marginVertical: 20,
  },
  preview: {
    width: 300,
    height: 300,
    borderRadius: 10,
  },
  analyzeButton: {
    marginTop: 20,
  },
  loader: {
    marginVertical: 20,
  },
  error: {
    color: 'red',
    textAlign: 'center',
    margin: 20,
  },
  resultsCard: {
    margin: 20,
  },
  resultText: {
    fontSize: 16,
    lineHeight: 24,
  },
});

export default CropDoctorScreen;
