import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders GitHub Events Monitor heading', () => {
  render(<App />);
  const headingElement = screen.getByText(/GitHub Events Monitor/i);
  expect(headingElement).toBeInTheDocument();
});
