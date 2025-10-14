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
      primary: '#00D4AA',
      primaryDark: '#00B894',
      secondary: '#6C5CE7',
      accent: '#FD79A8',
      background: isDarkMode ? '#0A0E27' : '#FFFFFF',
      surface: isDarkMode ? '#1A1F3A' : '#F7FAFC',
      surfaceLight: isDarkMode ? '#2D3748' : '#EDF2F7',
      text: isDarkMode ? '#FFFFFF' : '#1A202C',
      textSecondary: isDarkMode ? '#A0AEC0' : '#4A5568',
      textMuted: isDarkMode ? '#718096' : '#718096',
      success: '#48BB78',
      warning: '#ED8936',
      error: '#F56565',
      border: isDarkMode ? '#2D3748' : '#E2E8F0',
      shadow: isDarkMode ? 'rgba(0, 0, 0, 0.1)' : 'rgba(0, 0, 0, 0.05)',
    },
    gradients: {
      primary: 'linear-gradient(135deg, #00D4AA 0%, #00B894 100%)',
      secondary: 'linear-gradient(135deg, #6C5CE7 0%, #A29BFE 100%)',
      surface: isDarkMode 
        ? 'linear-gradient(135deg, #1A1F3A 0%, #2D3748 100%)'
        : 'linear-gradient(135deg, #F7FAFC 0%, #EDF2F7 100%)',
    },
    shadows: {
      small: isDarkMode ? '0 2px 4px rgba(0, 0, 0, 0.1)' : '0 2px 4px rgba(0, 0, 0, 0.05)',
      medium: isDarkMode ? '0 4px 8px rgba(0, 0, 0, 0.15)' : '0 4px 8px rgba(0, 0, 0, 0.1)',
      large: isDarkMode ? '0 8px 16px rgba(0, 0, 0, 0.2)' : '0 8px 16px rgba(0, 0, 0, 0.15)',
      xl: isDarkMode ? '0 16px 32px rgba(0, 0, 0, 0.25)' : '0 16px 32px rgba(0, 0, 0, 0.2)',
    },
    borderRadius: {
      small: '4px',
      medium: '8px',
      large: '12px',
      xl: '16px',
    },
    spacing: {
      xs: '4px',
      sm: '8px',
      md: '16px',
      lg: '24px',
      xl: '32px',
      xxl: '48px',
    },
    breakpoints: {
      mobile: '768px',
      tablet: '1024px',
      desktop: '1200px',
    },
    isDarkMode,
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, isDarkMode }}>
      {children}
    </ThemeContext.Provider>
  );
};