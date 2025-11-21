import React, { createContext, useContext, useState } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState(true);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  const theme = {
    colors: {
      // Modern refined teal/cyan palette
      primary: '#06B6D4', // Cyan-500 - more polished than previous
      primaryLight: '#22D3EE', // Cyan-400
      primaryDark: '#0891B2', // Cyan-600
      primaryGlow: 'rgba(6, 182, 212, 0.15)',
      
      secondary: '#8B5CF6', // Purple-500
      accent: '#F59E0B', // Amber-500
      
      // Modern dark mode background (lighter, cleaner)
      background: isDarkMode ? '#0F172A' : '#FFFFFF', // Slate-900
      backgroundSecondary: isDarkMode ? '#1E293B' : '#F8FAFC', // Slate-800
      surface: isDarkMode ? '#1E293B' : '#FFFFFF', // Slate-800
      surfaceHover: isDarkMode ? '#334155' : '#F1F5F9', // Slate-700
      surfaceElevated: isDarkMode ? '#334155' : '#FFFFFF', // Slate-700
      
      text: isDarkMode ? '#F1F5F9' : '#0F172A', // Slate-100 / Slate-900
      textSecondary: isDarkMode ? '#CBD5E1' : '#475569', // Slate-300 / Slate-600
      textMuted: isDarkMode ? '#94A3B8' : '#64748B', // Slate-400 / Slate-500
      
      success: '#10B981', // Emerald-500
      warning: '#F59E0B', // Amber-500
      error: '#EF4444', // Red-500
      info: '#3B82F6', // Blue-500
      
      border: isDarkMode ? '#334155' : '#E2E8F0', // Slate-700 / Slate-200
      borderLight: isDarkMode ? '#1E293B' : '#F1F5F9', // Slate-800 / Slate-100
      
      shadow: isDarkMode ? 'rgba(0, 0, 0, 0.3)' : 'rgba(0, 0, 0, 0.1)',
    },
    gradients: {
      primary: 'linear-gradient(135deg, #06B6D4 0%, #0891B2 100%)',
      primarySubtle: 'linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(8, 145, 178, 0.1) 100%)',
      secondary: 'linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%)',
      surface: isDarkMode 
        ? 'linear-gradient(135deg, #1E293B 0%, #334155 100%)'
        : 'linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)',
      card: isDarkMode
        ? 'linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.4) 100%)'
        : 'linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)',
    },
    shadows: {
      xs: isDarkMode ? '0 1px 2px rgba(0, 0, 0, 0.3)' : '0 1px 2px rgba(0, 0, 0, 0.05)',
      small: isDarkMode ? '0 2px 4px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(51, 65, 85, 0.5)' : '0 2px 4px rgba(0, 0, 0, 0.05)',
      medium: isDarkMode ? '0 4px 12px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(51, 65, 85, 0.5)' : '0 4px 12px rgba(0, 0, 0, 0.1)',
      large: isDarkMode ? '0 8px 24px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(51, 65, 85, 0.5)' : '0 8px 24px rgba(0, 0, 0, 0.15)',
      xl: isDarkMode ? '0 16px 48px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(51, 65, 85, 0.5)' : '0 16px 48px rgba(0, 0, 0, 0.2)',
      glow: '0 0 20px rgba(6, 182, 212, 0.3)',
    },
    borderRadius: {
      xs: '4px',
      small: '6px',
      medium: '8px',
      large: '12px',
      xl: '16px',
      '2xl': '20px',
      full: '9999px',
    },
    spacing: {
      xs: '4px',
      sm: '8px',
      md: '16px',
      lg: '24px',
      xl: '32px',
      '2xl': '48px',
      '3xl': '64px',
    },
    typography: {
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif",
      fontSize: {
        xs: '12px',
        sm: '14px',
        base: '16px',
        lg: '18px',
        xl: '20px',
        '2xl': '24px',
        '3xl': '30px',
        '4xl': '36px',
      },
      fontWeight: {
        normal: 400,
        medium: 500,
        semibold: 600,
        bold: 700,
      },
      lineHeight: {
        tight: 1.25,
        normal: 1.5,
        relaxed: 1.75,
      },
    },
    breakpoints: {
      mobile: '768px',
      tablet: '1024px',
      desktop: '1280px',
    },
    transitions: {
      fast: '150ms ease',
      normal: '200ms ease',
      slow: '300ms ease',
    },
    isDarkMode,
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, isDarkMode }}>
      {children}
    </ThemeContext.Provider>
  );
};