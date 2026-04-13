import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import ChatPage from '../app/page';

test('renders the main heading', () => {
  render(<ChatPage />);
  const heading = screen.getByText(/ScholarAgent/i);
  expect(heading).toBeDefined();
});