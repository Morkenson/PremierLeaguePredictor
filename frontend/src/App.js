import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import styled, { ThemeProvider } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Home, 
  Target, 
  Trophy, 
  BarChart3, 
  Calendar,
  Menu,
  X
} from 'lucide-react';
import { ThemeProvider as CustomThemeProvider, useTheme } from './contexts/ThemeContext';
import { GlobalStyle } from './styles/GlobalStyle';
import { Toaster } from 'react-hot-toast';
import logoImage from './static/prem.webp';

import Dashboard from './pages/Dashboard';
import Predictor from './pages/Predictor';
import LeagueTable from './pages/LeagueTable';
import TeamStats from './pages/TeamStats';
import Fixtures from './pages/Fixtures';

const AppContainer = styled.div`
  display: flex;
  min-height: 100vh;
  background: ${props => props.theme.colors.background};
  color: ${props => props.theme.colors.text};
  font-family: ${props => props.theme.typography.fontFamily};
`;

const Sidebar = styled(motion.aside)`
  position: fixed;
  top: 0;
  left: 0;
  width: 220px;
  height: 100vh;
  background: ${props => props.theme.colors.surface};
  border-right: 1px solid ${props => props.theme.colors.border};
  z-index: 1000;
  display: flex;
  flex-direction: column;
  box-shadow: ${props => props.theme.shadows.medium};
  overflow-y: auto;
  overflow-x: hidden;
  
  /* Custom scrollbar */
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background: ${props => props.theme.colors.border};
    border-radius: ${props => props.theme.borderRadius.full};
    
    &:hover {
      background: ${props => props.theme.colors.textMuted};
    }
  }

  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    transform: ${props => props.isOpen ? 'translateX(0)' : 'translateX(-100%)'};
    width: 280px;
    box-shadow: ${props => props.isOpen ? props.theme.shadows.xl : 'none'};
  }
`;

const SidebarHeader = styled.div`
  padding: ${props => props.theme.spacing.xl};
  border-bottom: 1px solid ${props => props.theme.colors.border};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  min-height: 72px;
`;

const LogoIcon = styled.div`
  width: 36px;
  height: 36px;
  border-radius: ${props => props.theme.borderRadius.medium};
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
  background: ${props => props.theme.colors.surface};
  
  img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    display: block;
  }
`;

const LogoText = styled.div`
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
  color: ${props => props.theme.colors.text};
  letter-spacing: -0.5px;
`;

const Nav = styled.nav`
  flex: 1;
  padding: ${props => props.theme.spacing.md} 0;
  overflow-y: auto;
`;

const NavItem = styled(motion.div)`
  margin: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.medium};
  overflow: hidden;
`;

const NavLink = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.lg};
  color: ${props => props.active ? props.theme.colors.primary : props.theme.colors.textSecondary};
  background: ${props => props.active 
    ? props.theme.gradients.primarySubtle 
    : 'transparent'};
  border-left: 3px solid ${props => props.active ? props.theme.colors.primary : 'transparent'};
  transition: all ${props => props.theme.transitions.normal};
  cursor: pointer;
  font-size: ${props => props.theme.typography.fontSize.base};
  font-weight: ${props => props.active 
    ? props.theme.typography.fontWeight.semibold 
    : props.theme.typography.fontWeight.medium};
  position: relative;

  &:hover {
    background: ${props => props.active 
      ? props.theme.gradients.primarySubtle 
      : props.theme.colors.surfaceHover};
    color: ${props => props.theme.colors.primary};
    transform: translateX(2px);
  }

  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    background: ${props => props.theme.colors.primary};
    opacity: ${props => props.active ? 1 : 0};
    transition: opacity ${props => props.theme.transitions.normal};
  }
`;

const NavIcon = styled.div`
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: ${props => props.active ? 'inherit' : 'inherit'};
`;

const MainContent = styled.main`
  flex: 1;
  margin-left: 220px;
  min-height: 100vh;
  transition: margin-left ${props => props.theme.transitions.normal};

  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    margin-left: 0;
  }
`;

const ContentWrapper = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: ${props => props.theme.spacing.xl};
  
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    padding: ${props => props.theme.spacing.lg};
  }
`;

const MobileOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  backdrop-filter: blur(4px);
  
  @media (min-width: ${props => props.theme.breakpoints.mobile}) {
    display: none;
  }
`;

const MobileMenuButton = styled.button`
  position: fixed;
  top: ${props => props.theme.spacing.lg};
  left: ${props => props.theme.spacing.lg};
  z-index: 1001;
  width: 44px;
  height: 44px;
  border-radius: ${props => props.theme.borderRadius.medium};
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  color: ${props => props.theme.colors.text};
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all ${props => props.theme.transitions.normal};
  box-shadow: ${props => props.theme.shadows.small};

  &:hover {
    background: ${props => props.theme.colors.surfaceHover};
    border-color: ${props => props.theme.colors.primary};
    color: ${props => props.theme.colors.primary};
  }

  @media (min-width: ${props => props.theme.breakpoints.mobile}) {
    display: none;
  }
`;

const AppContent = () => {
  const { theme } = useTheme();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState('Dashboard');

  const navItems = [
    { id: 'Dashboard', label: 'Dashboard', icon: Home },
    { id: 'Predictor', label: 'Match Predictor', icon: Target },
    { id: 'LeagueTable', label: 'League Table', icon: Trophy },
    { id: 'TeamStats', label: 'Team Stats', icon: BarChart3 },
    { id: 'Fixtures', label: 'Fixtures', icon: Calendar },
  ];

  const handleNavClick = (item) => {
    setCurrentPage(item.id);
    setSidebarOpen(false);
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'Dashboard':
        return <Dashboard />;
      case 'Predictor':
        return <Predictor />;
      case 'LeagueTable':
        return <LeagueTable />;
      case 'TeamStats':
        return <TeamStats />;
      case 'Fixtures':
        return <Fixtures />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: theme.colors.surface,
            color: theme.colors.text,
            border: `1px solid ${theme.colors.border}`,
          },
          success: {
            iconTheme: {
              primary: theme.colors.success,
              secondary: theme.colors.surface,
            },
          },
          error: {
            iconTheme: {
              primary: theme.colors.error,
              secondary: theme.colors.surface,
            },
          },
        }}
      />
      <AppContainer>
          <MobileMenuButton onClick={toggleSidebar}>
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </MobileMenuButton>

          <AnimatePresence>
            {sidebarOpen && (
              <MobileOverlay
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setSidebarOpen(false)}
              />
            )}
          </AnimatePresence>

          <Sidebar
            isOpen={sidebarOpen}
            initial={false}
            animate={{
              x: (typeof window !== 'undefined' && window.innerWidth > 768) || sidebarOpen ? 0 : -220,
            }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
          >
            <SidebarHeader>
              <LogoIcon>
                <img src={logoImage} alt="Premier League Logo" />
              </LogoIcon>
              <LogoText>Premier Predictor</LogoText>
            </SidebarHeader>

            <Nav>
              {navItems.map((item) => (
                <NavItem key={item.id}>
                  <NavLink
                    active={currentPage === item.id}
                    onClick={() => handleNavClick(item)}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <NavIcon active={currentPage === item.id}>
                      <item.icon size={18} />
                    </NavIcon>
                    {item.label}
                  </NavLink>
                </NavItem>
              ))}
            </Nav>
          </Sidebar>

          <MainContent>
            <ContentWrapper>
              {renderPage()}
            </ContentWrapper>
      </MainContent>
    </AppContainer>
    </ThemeProvider>
  );
};

function App() {
  return (
    <CustomThemeProvider>
      <AppContent />
    </CustomThemeProvider>
  );
}

export default App;
