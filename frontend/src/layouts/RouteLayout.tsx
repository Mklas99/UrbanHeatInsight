import React from 'react';
import { Drawer, Box, useTheme } from '@mui/material';
import Header from './Header';
import { useUIStore } from '../state/uiStore';

/**
 * RouteLayout – a high level layout that renders the application header,
 * a persistent sidebar and the main content area. The sidebar content is
 * supplied via the `sidebar` prop allowing each route to provide its own
 * navigation or contextual controls. By centralising the layout concerns
 * here we adhere to the single responsibility principle – pages only
 * worry about their own content.
 */
export interface RouteLayoutProps {
  /** The React node to render inside the sidebar */
  sidebar: React.ReactNode;
  /** The main page content */
  children: React.ReactNode;
  /** Height of the fixed header in pixels. Defaults to 64px. */
  headerHeight?: number;
  /** Width of the sidebar in pixels. Defaults to 280px. */
  sidebarWidth?: number;
}

export default function RouteLayout({
  sidebar,
  children,
  headerHeight = 64,
  sidebarWidth = 280,
}: RouteLayoutProps) {
  // Consume sidebar state from our global store. When `sidebarOpen` is
  // toggled via the Header menu button the Drawer will open/close.
  const sidebarOpen = useUIStore((s) => s.sidebarOpen);

  const theme = useTheme();

  return (
    <>
      {/* Always render the header at the top of the page. */}
      <Header />

      {/* Sidebar using MUI's persistent drawer. The `sx` prop ensures the
          drawer does not overlap the header and uses our supplied width.
          On smaller screens you may wish to change variant to "temporary"
          and hide automatically – this example keeps things simple. */}
      <Drawer
        variant="persistent"
        open={sidebarOpen}
        anchor="left"
        sx={{
          width: sidebarWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: {
            width: sidebarWidth,
            boxSizing: 'border-box',
            top: `${headerHeight}px`,
            // Take full viewport height minus the header
            height: `calc(100vh - ${headerHeight}px)`,
            // Use theme background for a cohesive look
            backgroundColor: theme.palette.background.default,
          },
        }}
      >
        {sidebar}
      </Drawer>

      {/* Main content. When the sidebar is open we offset the content by
          the sidebar width. The margin-top ensures the content sits below
          the fixed header. */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          marginLeft: sidebarOpen ? `${sidebarWidth}px` : 0,
          marginTop: `${headerHeight}px`,
          height: `calc(100vh - ${headerHeight}px)`,
          transition: theme.transitions.create(['margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          // Let individual pages decide their own padding. Providing a small
          // default ensures content isn't flush against the viewport.
          p: 0.5,
        }}
      >
        {children}
      </Box>
    </>
  );
}