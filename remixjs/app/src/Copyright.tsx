import * as React from 'react';
import Typography from '@mui/material/Typography';
import Link from '@mui/material/Link';
import { Box, Divider, Grid2 } from '@mui/material';

export default function Copyright() {
  return (
    <Grid2 container direction="column" sx={{paddingY: 4}}>
      <Grid2>
        <Divider />
      </Grid2>
      <Grid2>
        <Typography
          variant="body2"
          align="center"
          sx={{
            color: 'text.secondary',
          }}
        >
          {'Copyright © '}
          <Link color="inherit" href="https://mui.com/">
            Random search engine
          </Link>{' '}
          {new Date().getFullYear()}.
        </Typography>
      </Grid2>
    </Grid2>
  );
}
