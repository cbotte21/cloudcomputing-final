// app/routes/index.tsx
import type { MetaFunction } from '@remix-run/node';
import { useState } from 'react';
import { Box, Button, Grid2, TextField } from '@mui/material';
import { Form } from '@remix-run/react';

export const meta: MetaFunction = () => [
  { title: 'Remix Starter' },
  { name: 'description', content: 'Welcome to remix!' },
];

export default function Index({defaultQuery = ''}: any) {
  const [query, setQuery] = useState(defaultQuery);

  const handleRedirect = () => {
    if (query) {
      window.location.href = `/search?q=${encodeURIComponent(query)}`;
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      handleRedirect();
    }
  };

  return (
    <Box sx={{paddingY: 4}}>
      <Form onSubmit={(e) => {e.preventDefault(); handleRedirect()}}>
        <Grid2 container alignItems="center" justifyContent="center" spacing={2}>
          <Grid2 size={4}>
            <TextField 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown} // Add the key down event handler
              label="Search" 
              variant="outlined"
              fullWidth
            />
          </Grid2>
          <Grid2>
            <Button 
              type='submit'
              variant='contained'
            >
              GO
            </Button>
          </Grid2>
        </Grid2>
      </Form>
    </Box>
  );
}