import React, { useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, TextInput, Button, Card, ActivityIndicator, MD2Colors } from 'react-native-paper';
import { getMarketTrends } from '../../services/api';

const MarketAnalystScreen = () => {
  const [commodity, setCommodity] = useState('');
  const [state, setState] = useState('');
  const [market, setMarket] = useState('');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!commodity || !state || !market) {
      setError('Please fill in all fields.');
      return;
    }

    setLoading(true);
    setError(null);
    setData(null);

    try {
      const res = await getMarketTrends(commodity, state, market);
      setData(res.data);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch market data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Market Analyst</Text>
        <Text style={styles.subtitle}>Get the latest price trends</Text>
      </View>

      <Card style={styles.formCard}>
        <Card.Content>
          <TextInput
            label="Commodity (e.g., Wheat)"
            value={commodity}
            onChangeText={setCommodity}
            style={styles.input}
          />
          <TextInput
            label="State (e.g., Maharashtra)"
            value={state}
            onChangeText={setState}
            style={styles.input}
          />
          <TextInput
            label="Market (e.g., Mumbai)"
            value={market}
            onChangeText={setMarket}
            style={styles.input}
          />
          <Button mode="contained" onPress={handleSearch} disabled={loading} style={styles.searchButton}>
            Search Trends
          </Button>
        </Card.Content>
      </Card>

      {loading && <ActivityIndicator animating={true} color={MD2Colors.green800} size="large" style={styles.loader} />}

      {error && <Text style={styles.error}>{error}</Text>}

      {data && (
        <Card style={styles.resultsCard}>
          <Card.Title title="Market Report" subtitle={`${data.commodity} in ${data.market}, ${data.state}`} />
          <Card.Content>
            <Text style={styles.price}>Latest Price: ₹{data.latest_price}/quintal</Text>
            <Text style={styles.trend}>Trend: {data.trend}</Text>
            <View style={styles.details}>
              <Text>Avg: ₹{data.average_price}</Text>
              <Text>High: ₹{data.highest_price}</Text>
              <Text>Low: ₹{data.lowest_price}</Text>
            </View>
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
  formCard: {
    margin: 20,
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
    margin: 20,
  },
  price: {
    fontSize: 22,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
  },
  trend: {
    fontSize: 18,
    textAlign: 'center',
    textTransform: 'capitalize',
    marginBottom: 10,
  },
  details: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 10,
  },
});

export default MarketAnalystScreen;
