import React from 'react';
import { useUIStore } from '../state/uiStore';

// Export these constants so they can be imported elsewhere if needed
export const SIDEBAR_WIDTH = 320;
export const HEADER_HEIGHT = 64;

interface PageLayoutProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  headerHeight?: number;
  fullHeight?: boolean; // Whether the content should take full viewport height
}

/**
 * PageLayout - A layout component that adjusts its width and margin
 * based on the sidebar's open/closed state and header height
 */
export default function PageLayout({ 
  children, 
  className = '', 
  style = {}, 
  headerHeight = HEADER_HEIGHT,
  fullHeight = false
}: PageLayoutProps) {
  const sidebarOpen = useUIStore((s: { sidebarOpen: boolean }) => s.sidebarOpen);

  // Base styles that respond to the sidebar state and header height
  const baseStyle: React.CSSProperties = {
    transition: 'margin 225ms cubic-bezier(0.0, 0, 0.2, 1) 0ms',
    marginLeft: sidebarOpen ? `${SIDEBAR_WIDTH}px` : 0,
    width: sidebarOpen ? `calc(100% - ${SIDEBAR_WIDTH}px)` : '100%',
    marginTop: headerHeight, // Add margin for header
    height: fullHeight ? `calc(100vh - ${headerHeight}px)` : 'auto',
  };

  // Merge the base styles with any custom styles provided
  const mergedStyle = { ...baseStyle, ...style };

  return (
    <main className={`page-layout ${className}`} style={mergedStyle}>
      {children}
    </main>
  );
}
