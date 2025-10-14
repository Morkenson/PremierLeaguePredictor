import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import styled from 'styled-components';

import Dashboard from './pages/Dashboard';
import Predictor from './pages/Predictor';
import LeagueTable from './pages/LeagueTable';
import TeamStats from './pages/TeamStats';
import Fixtures from './pages/Fixtures';

const AppContainer = styled.div`
  display: flex;
  min-height: 100vh;
  background: #0A0E27;
  color: #FFFFFF;
`;

const MainContent = styled.main`
  flex: 1;
  margin-left: 250px;
  padding: 20px;
  transition: margin-left 0.3s ease;

  @media (max-width: 768px) {
    margin-left: 0;
    padding: 10px;
  }
`;

const ContentWrapper = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const Sidebar = styled.aside`
  position: fixed;
  top: 0;
  left: 0;
  width: 250px;
  height: 100vh;
  background: linear-gradient(135deg, #1A1F3A 0%, #2D3748 100%);
  border-right: 1px solid #2D3748;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  padding: 20px;
  color: #FFFFFF;

  @media (max-width: 768px) {
    transform: ${props => props.isOpen ? 'translateX(0)' : 'translateX(-100%)'};
  }
`;

const Logo = styled.div`
  font-size: 20px;
  font-weight: 700;
  color: #00D4AA;
  margin-bottom: 30px;
`;

const NavItem = styled.div`
  padding: 12px 16px;
  margin: 4px 0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: ${props => props.active ? 'rgba(0, 212, 170, 0.1)' : 'transparent'};
  border-left: 3px solid ${props => props.active ? '#00D4AA' : 'transparent'};

  &:hover {
    background: rgba(0, 212, 170, 0.05);
  }
`;

const Header = styled.header`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;
  margin-bottom: 24px;
  border-bottom: 1px solid #2D3748;
`;

const PageTitle = styled.h1`
  font-size: 28px;
  font-weight: 700;
  color: #FFFFFF;
  margin: 0;
`;

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState('Dashboard');

  const navItems = [
    { id: 'Dashboard', label: 'Dashboard' },
    { id: 'Predictor', label: 'Match Predictor' },
    { id: 'LeagueTable', label: 'League Table' },
    { id: 'TeamStats', label: 'Team Stats' },
    { id: 'Fixtures', label: 'Fixtures' },
  ];

  const handleNavClick = (item) => {
    setCurrentPage(item.id);
    setSidebarOpen(false);
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
    <AppContainer>
      <Sidebar isOpen={sidebarOpen}>
        <Logo>Premier Predictor</Logo>
        {navItems.map((item) => (
          <NavItem
            key={item.id}
            active={currentPage === item.id}
            onClick={() => handleNavClick(item)}
          >
            {item.label}
          </NavItem>
        ))}
      </Sidebar>
      
      <MainContent>
        <Header>
          <PageTitle>{currentPage}</PageTitle>
        </Header>
        <ContentWrapper>
          {renderPage()}
        </ContentWrapper>
      </MainContent>
    </AppContainer>
  );
}

export default App;