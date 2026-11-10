/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';
import { NextRouter } from 'next/router';

// Mock next/link since we can't use it directly in tests
vi.mock('next/link', () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

// Mock next/font
vi.mock('next/font/google', () => ({
  Inter: () => ({ className: 'mock-inter' }),
}));

// Mock metadata
vi.mock('next', () => ({
  metadata: {},
}));

// Import the component dynamically to avoid Next.js-specific issues
import * as pageModule from './page';

describe('Home Page', () => {
  it('renders the app title', async () => {
    const { default: Home } = pageModule;
    render(<Home />);
    expect(screen.getByText('SpeakNara')).toBeInTheDocument();
  });

  it('has sign in and register links', async () => {
    const { default: Home } = pageModule;
    render(<Home />);
    
    expect(screen.getByRole('link', { name: /sign in/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /register/i })).toBeInTheDocument();
  });
});
