import React, { useState } from 'react';
import './App.css';
import { Heading, Button, Flex, View, TextField, Text, Image } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import athenaService from './services/athenaService';
import QueryResultsTable from './components/QueryResultsTable';

function App() {
  const [queryResults, setQueryResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchText, setSearchText] = useState('');

  const executeQuery = async () => {
    setLoading(true);
    setError(null);
    setQueryResults(null);

    const dynamicQuery = `select concat('[',dataset,'](https://huggingface.co/datasets/',dataset,')') as "Data Set", score as "OTDI Score", license as "License" from aialliance.otdi where date = cast('2025-06-29' as date) ${searchText} limit 100`;

    try {
      const results = await athenaService.executeQuery(dynamicQuery);
      setQueryResults(results);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <Flex direction="row" gap="1rem" alignItems="center">
          <Heading level={1}>NextGem Data Catalog</Heading>
          <Image
            src="/nextgem_logo.png"
            alt="NextGem Logo"
            height="135px"
          />
        </Flex>
        <View marginTop="2rem">
          <Flex direction="column" gap="1rem" alignItems="center">
            <TextField
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              placeholder="Enter search terms..."
              width="400px"
            />
            <Button onClick={executeQuery} disabled={loading}>
              {loading ? 'Executing Query...' : 'Search Catalog'}
            </Button>
            <View marginTop="2rem" width="100%">
              <QueryResultsTable 
                data={queryResults} 
                loading={loading} 
                error={error} 
              />
            </View>
          </Flex>
        </View>
      </header>
    </div>
  );
}

export default App;
