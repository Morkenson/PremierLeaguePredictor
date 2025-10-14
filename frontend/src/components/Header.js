import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { Menu, Bell, User } from 'lucide-react';

const HeaderContainer = styled(motion.header)`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;
  margin-bottom: 24px;
  border-bottom: 1px solid ${props => props.theme?.colors?.border || '#2D3748'};
`;

const LeftSection = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const MobileMenuButton = styled.button`
  display: none;
  padding: 8px;
  background: transparent;
  border: none;
  color: ${props => props.theme.colors.textSecondary};
  border-radius: 6px;
  cursor: pointer;

  @media (max-width: 768px) {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  &:hover {
    background: ${props => props.theme.colors.surfaceLight};
    color: ${props => props.theme.colors.text};
  }
`;

const PageTitle = styled.h1`
  font-size: 28px;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
  margin: 0;
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const NotificationButton = styled.button`
  position: relative;
  padding: 8px;
  background: transparent;
  border: none;
  color: ${props => props.theme.colors.textSecondary};
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.colors.surfaceLight};
    color: ${props => props.theme.colors.text};
  }
`;

const UserButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: ${props => props.theme.colors.surfaceLight};
  border: none;
  border-radius: 8px;
  color: ${props => props.theme.colors.text};
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.colors.surface};
  }
`;

const Header = ({ onMenuClick }) => {
  return (
    <HeaderContainer
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <LeftSection>
        <MobileMenuButton onClick={onMenuClick}>
          <Menu size={20} />
        </MobileMenuButton>
        <PageTitle>Premier League Predictor</PageTitle>
      </LeftSection>

      <RightSection>
        <NotificationButton>
          <Bell size={20} />
        </NotificationButton>
        
        <UserButton>
          <User size={16} />
          <span>User</span>
        </UserButton>
      </RightSection>
    </HeaderContainer>
  );
};

export default Header;