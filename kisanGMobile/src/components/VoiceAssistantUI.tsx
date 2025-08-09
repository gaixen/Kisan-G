import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, Linking } from 'react-native';
import { FAB, Modal, Portal, Text, Button, Provider, ActivityIndicator, MD2Colors, Card } from 'react-native-paper';
import Voice, { SpeechResultsEvent } from '@react-native-voice/voice';
import { getGovtSchemes } from '../services/api';

const VoiceAssistantUI = () => {
  const [modalVisible, setModalVisible] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [schemes, setSchemes] = useState<any[]>([]);
  const [error, setError] = useState('');

  const onSpeechResults = (e: SpeechResultsEvent) => {
    if (e.value) {
      setTranscript(e.value[0]);
    }
  };

  const onSpeechError = (e: any) => {
    setError(JSON.stringify(e.error));
    setIsRecording(false);
  };

  useEffect(() => {
    Voice.onSpeechError = onSpeechError;
    Voice.onSpeechResults = onSpeechResults;

    return () => {
      Voice.destroy().then(Voice.removeAllListeners);
    };
  }, []);

  const startRecording = async () => {
    setIsRecording(true);
    setError('');
    setTranscript('');
    setSchemes([]);
    try {
      await Voice.start('en-US');
    } catch (e) {
      console.error(e);
      setError('Failed to start recording.');
    }
  };

  const stopRecording = async () => {
    setIsRecording(false);
    try {
      await Voice.stop();
    } catch (e) {
      console.error(e);
    }
  };

  const handleSearch = async () => {
    if (!transcript) return;

    setIsLoading(true);
    setError('');
    setSchemes([]);

    try {
      const res = await getGovtSchemes(transcript);
      if (res.data.schemes && res.data.schemes.length > 0) {
        setSchemes(res.data.schemes);
      } else {
        setError('No schemes found for your query.');
      }
    } catch (err) {
      console.error(err);
      setError('Failed to fetch schemes.');
    } finally {
      setIsLoading(false);
    }
  };

  const showModal = () => setModalVisible(true);
  const hideModal = () => {
    if (isRecording) {
      stopRecording();
    }
    setModalVisible(false);
    setTranscript('');
    setSchemes([]);
    setError('');
  };

  return (
    <Provider>
      <Portal>
        <FAB
          icon="microphone"
          style={styles.fab}
          onPress={showModal}
        />
        <Modal visible={modalVisible} onDismiss={hideModal} contentContainerStyle={styles.modalContainer}>
          <ScrollView contentContainerStyle={styles.scrollContent}>
            <Text style={styles.title}>Voice Assistant</Text>
            <Text style={styles.transcript}>{transcript || 'Press the button and speak'}</Text>
            
            <Button
              mode="contained"
              onPress={isRecording ? stopRecording : startRecording}
              style={styles.button}
              icon={isRecording ? 'stop-circle-outline' : 'microphone'}
            >
              {isRecording ? 'Stop Recording' : 'Start Recording'}
            </Button>

            {transcript && !isRecording && (
              <Button
                mode="contained-tonal"
                onPress={handleSearch}
                disabled={isLoading}
                style={styles.button}
                icon="magnify"
              >
                Search Schemes
              </Button>
            )}

            {isLoading && <ActivityIndicator animating={true} color={MD2Colors.green800} size="large" style={styles.loader} />}
            {error ? <Text style={styles.error}>{error}</Text> : null}

            {schemes.map((scheme, index) => (
              <Card key={index} style={styles.resultsCard}>
                <Card.Title title={scheme.source?.title || 'Scheme'} />
                <Card.Content>
                  <Text style={styles.description}>{scheme.content}</Text>
                  <Button
                    icon="link"
                    mode="text"
                    onPress={() => Linking.openURL(scheme.source?.url)}
                    style={styles.linkButton}
                  >
                    Learn More
                  </Button>
                </Card.Content>
              </Card>
            ))}
          </ScrollView>
        </Modal>
      </Portal>
    </Provider>
  );
};

const styles = StyleSheet.create({
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: '#6200ee',
  },
  modalContainer: {
    backgroundColor: 'white',
    padding: 20,
    margin: 20,
    borderRadius: 10,
    maxHeight: '80%',
  },
  scrollContent: {
    alignItems: 'center',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  transcript: {
    marginBottom: 20,
    textAlign: 'center',
    minHeight: 20,
  },
  button: {
    width: '90%',
    marginBottom: 10,
  },
  loader: {
    marginVertical: 20,
  },
  error: {
    color: 'red',
    marginTop: 10,
    textAlign: 'center',
  },
  resultsCard: {
    width: '100%',
    marginVertical: 10,
  },
  description: {
    marginBottom: 10,
  },
  linkButton: {
    marginTop: 10,
    alignSelf: 'flex-start',
  },
});

export default VoiceAssistantUI;
