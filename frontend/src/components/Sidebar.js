import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  Home, 
  Target, 
  Trophy, 
  BarChart3, 
  Calendar,
  Menu,
  Moon,
  Sun
} from 'lucide-react';

const SidebarContainer = styled(motion.aside)`
  position: fixed;
  top: 0;
  left: 0;
  width: 250px;
  height: 100vh;
  background: ${props => props.theme.gradients.surface};
  border-right: 1px solid ${props => props.theme.colors.border};
  z-index: 1000;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease;

  @media (max-width: 768px) {
    transform: ${props => props.isOpen ? 'translateX(0)' : 'translateX(-100%)'};
  }
`;

const SidebarHeader = styled.div`
  padding: 20px;
  border-bottom: 1px solid ${props => props.theme.colors.border};
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 700;
  color: ${props => props.theme.colors.primary};
`;

const LogoIcon = styled.div`
  width: 32px;
  height: 32px;
  background: ${props => props.theme.gradients.primary};
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
`;

const Nav = styled.nav`
  flex: 1;
  padding: 20px 0;
`;

const NavItem = styled(motion.div)`
  margin: 4px 16px;
  border-radius: 8px;
  overflow: hidden;
`;

const NavLink = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: ${props => props.active ? props.theme.colors.primary : props.theme.colors.textSecondary};
  background: ${props => props.active ? 'rgba(0, 212, 170, 0.1)' : 'transparent'};
  border-left: 3px solid ${props => props.active ? props.theme.colors.primary : 'transparent'};
  transition: all 0.2s ease;
  cursor: pointer;

  &:hover {
    background: rgba(0, 212, 170, 0.05);
    color: ${props => props.theme.colors.primary};
  }
`;

const NavIcon = styled.div`
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const SidebarFooter = styled.div`
  padding: 20px;
  border-top: 1px solid ${props => props.theme.colors.border};
`;

const ThemeToggle = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: transparent;
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 6px;
  color: ${props => props.theme.colors.textSecondary};
  transition: all 0.2s ease;
  width: 100%;

  &:hover {
    background: ${props => props.theme.colors.surfaceLight};
    color: ${props => props.theme.colors.text};
  }
`;

const Sidebar = ({ isOpen, onMenuClick }) => {
  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/predictor', icon: Target, label: 'Match Predictor' },
    { path: '/league-table', icon: Trophy, label: 'League Table' },
    { path: '/team-stats', icon: BarChart3, label: 'Team Stats' },
    { path: '/fixtures', icon: Calendar, label: 'Fixtures' },
  ];

  const handleNavClick = () => {
    onMenuClick();
  };

  return (
    <SidebarContainer
      isOpen={isOpen}
      initial={{ x: -250 }}
      animate={{ x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <SidebarHeader>
        <Logo>
          <LogoIcon>
            <Trophy size={18} />
          </LogoIcon>
          Premier Predictor
        </Logo>
      </SidebarHeader>

      <Nav>
        {navItems.map((item) => (
          <NavItem key={item.path}>
            <NavLink
              active={window.location.pathname === item.path}
              onClick={handleNavClick}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <NavIcon>
                <item.icon size={18} />
              </NavIcon>
              {item.label}
            </NavLink>
          </NavItem>
        ))}
      </Nav>

      <SidebarFooter>
        <ThemeToggle>
          <Sun size={16} />
          Light Mode
        </ThemeToggle>
      </SidebarFooter>
    </SidebarContainer>
  );
};

export default Sidebar;