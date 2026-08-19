import React from 'react';
import ReactDOM from 'react-dom/client';
import { MantineProvider } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import { StorageEngineProvider } from './storage/storageEngineHooks';
import '@mantine/core/styles.css';
import '@mantine/dates/styles.css';
import '@mantine/notifications/styles.css';
import { GlobalConfigParser } from './GlobalConfigParser';

const studyGreen = [
  '#3b6fc2', '#3b6fc2', '#3b6fc2', '#3b6fc2', '#3b6fc2',
  '#3b6fc2', '#3b6fc2', '#3b6fc2', '#3b6fc2', '#3b6fc2',
] as const;

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <StorageEngineProvider>
      <MantineProvider theme={{ colors: { studyGreen }, primaryColor: 'studyGreen' }}>
        <Notifications />
        <GlobalConfigParser />
      </MantineProvider>
    </StorageEngineProvider>
  </React.StrictMode>,
);
