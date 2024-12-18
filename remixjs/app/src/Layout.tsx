import * as React from 'react';
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import Copyright from './Copyright';

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <>
        {children}
        <Copyright />
    </>
  );
}
