import React from 'react';
import { Header } from './Header';
import { Navigation } from './Navigation';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div>
      <Header />
      <Navigation />
      <div className="container">
        {children}
      </div>
      <footer className="footer">
        Compliance AI Platform © 2025
      </footer>
    </div>
  );
}
