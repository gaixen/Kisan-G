import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Linking } from 'react-native';
import { Text, TextInput, Button, Card, ActivityIndicator, MD2Colors } from 'react-native-paper';
import { getGovtSchemes } from '../../services/api';

const SchemeNavigatorScreen = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [schemes, setSchemes] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query) {
      setError('Please enter a search query.');
      return;
    }

    setLoading(true);
    setError(null);
    setSchemes([]);

    try {
      const res = await getGovtSchemes(query);
      setSchemes(res.data.schemes);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch schemes. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Scheme Navigator</Text>
        <Text style={styles.subtitle}>Find relevant government schemes</Text>
      </View>

      <Card style={styles.formCard}>
        <Card.Content>
          <TextInput
            label="Search for schemes (e.g., crop insurance)"
            value={query}
            onChangeText={setQuery}
            style={styles.input}
          />
          <Button mode="contained" onPress={handleSearch} disabled={loading} style={styles.searchButton}>
            Search Schemes
          </Button>
        </Card.Content>
      </Card>

      {loading && <ActivityIndicator animating={true} color={MD2Colors.green800} size="large" style={styles.loader} />}

      {error && <Text style={styles.error}>{error}</Text>}

      <ScrollView>
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
    </View>
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
  formCard: {
    marginHorizontal: 20,
  },
  input: {
    marginBottom: 10,
  },
  searchButton: {
    marginTop: 10,
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
    marginHorizontal: 20,
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

export default SchemeNavigatorScreen;
