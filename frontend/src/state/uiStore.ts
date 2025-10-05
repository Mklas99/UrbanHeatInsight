import { create } from 'zustand';
import logger from '../utils/logger';

const log = logger('state/uiStore.js');
log.info('uiStore module loaded');

interface UIStoreState {
  sidebarOpen: boolean;
  toggleSidebar: () => void;

  showHeatmap: boolean;
  setShowHeatmap: (v: boolean) => void;

  heatRadius: number;
  setHeatRadius: (v: number) => void;

  themeMode: string;
  setThemeMode: (m: string) => void;
  toggleTheme: () => void;

  language: string;
  setLanguage: (lng: string) => void;
}

export const useUIStore = create<UIStoreState>((set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),

  showHeatmap: true,
  setShowHeatmap: (v) => set({ showHeatmap: v }),

  heatRadius: 25,
  setHeatRadius: (v) => set({ heatRadius: v }),

  themeMode: (localStorage.getItem('uhi-theme') || 'light'),
  setThemeMode: (m) => { localStorage.setItem('uhi-theme', m); set({ themeMode: m }); },
  toggleTheme: () => set((s) => {
    const m = s.themeMode === 'light' ? 'dark' : 'light';
    localStorage.setItem('uhi-theme', m);
    return { themeMode: m };
  }),

  language: (localStorage.getItem('uhi-lang') || 'en'),
  setLanguage: (lng) => { localStorage.setItem('uhi-lang', lng); set({ language: lng }); },
}));

log.debug('uiStore ready');
