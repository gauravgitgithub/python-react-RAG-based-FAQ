import React from 'react';
import { render } from '@testing-library/react';

// Simple test to verify the app can be imported
test('app can be imported', () => {
  // This test just verifies that the App component can be imported
  // without throwing any errors
  expect(() => {
    require('./App');
  }).not.toThrow();
});
