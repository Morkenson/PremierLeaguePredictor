import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  Activity, 
  Database, 
  Clock, 
  TrendingUp
} from 'lucide-react';

const DashboardContainer = styled.div`
  padding: 0;
  max-width: 1400px;
  margin: 0 auto;
`;

const HeaderSection = styled(motion.div)`
  margin-bottom: ${props => props.theme.spacing['2xl']};
`;

const PageTitle = styled.h1`
  font-size: ${props => props.theme.typography.fontSize['4xl']};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
  color: ${props => props.theme.colors.text};
  margin: 0 0 ${props => props.theme.spacing.sm} 0;
  line-height: ${props => props.theme.typography.lineHeight.tight};
  
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    font-size: ${props => props.theme.typography.fontSize['3xl']};
  }
`;

const PageSubtitle = styled.p`
  font-size: ${props => props.theme.typography.fontSize.lg};
  color: ${props => props.theme.colors.textSecondary};
  margin: 0;
  line-height: ${props => props.theme.typography.lineHeight.normal};
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing['2xl']};
  
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    grid-template-columns: 1fr;
    gap: ${props => props.theme.spacing.md};
  }
`;

const StatCard = styled(motion.div)`
  background: ${props => props.theme.gradients.card};
  backdrop-filter: blur(10px);
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.large};
  padding: ${props => props.theme.spacing.lg};
  box-shadow: ${props => props.theme.shadows.small};
  transition: all ${props => props.theme.transitions.normal};
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: ${props => props.theme.shadows.medium};
    border-color: ${props => props.theme.colors.primary};
  }
`;

const StatHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: ${props => props.theme.spacing.md};
`;

const StatIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: ${props => props.theme.borderRadius.medium};
  background: ${props => props.iconBg || props.theme.gradients.primarySubtle};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${props => props.iconColor || props.theme.colors.primary};
`;

const StatLabel = styled.div`
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.textSecondary};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const StatValue = styled.div`
  font-size: ${props => props.theme.typography.fontSize['3xl']};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
  color: ${props => props.theme.colors.text};
  margin: ${props => props.theme.spacing.xs} 0;
  line-height: ${props => props.theme.typography.lineHeight.tight};
`;

const StatChange = styled.div`
  font-size: ${props => props.theme.typography.fontSize.xs};
  color: ${props => props.positive ? props.theme.colors.success : props.theme.colors.textMuted};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
  margin-top: ${props => props.theme.spacing.xs};
`;

const CardsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: ${props => props.theme.spacing.lg};
  
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    grid-template-columns: 1fr;
  }
`;

const StatusCard = styled(motion.div)`
  background: ${props => props.theme.gradients.card};
  backdrop-filter: blur(10px);
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.large};
  padding: ${props => props.theme.spacing.xl};
  box-shadow: ${props => props.theme.shadows.small};
  transition: all ${props => props.theme.transitions.normal};
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: ${props => props.theme.shadows.medium};
    border-color: ${props => props.theme.colors.primary};
  }
`;

const StatusHeader = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const StatusIcon = styled.div`
  width: 48px;
  height: 48px;
  border-radius: ${props => props.theme.borderRadius.medium};
  background: ${props => props.iconBg || props.theme.gradients.primarySubtle};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${props => props.iconColor || props.theme.colors.primary};
  flex-shrink: 0;
`;

const StatusTitle = styled.h3`
  font-size: ${props => props.theme.typography.fontSize.xl};
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  color: ${props => props.theme.colors.text};
  margin: 0;
`;

const StatusContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.sm};
`;

const StatusItem = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.sm} 0;
  border-bottom: 1px solid ${props => props.theme.colors.borderLight};
  
  &:last-child {
    border-bottom: none;
  }
`;

const StatusIndicator = styled.div`
  width: 8px;
  height: 8px;
  border-radius: ${props => props.theme.borderRadius.full};
  background: ${props => props.active ? props.theme.colors.success : props.theme.colors.error};
  box-shadow: 0 0 8px ${props => props.active ? props.theme.colors.success : props.theme.colors.error};
  flex-shrink: 0;
`;

const StatusText = styled.div`
  font-size: ${props => props.theme.typography.fontSize.base};
  color: ${props => props.theme.colors.textSecondary};
  flex: 1;
`;

const StatusLink = styled.a`
  color: ${props => props.theme.colors.primary};
  text-decoration: none;
  font-size: ${props => props.theme.typography.fontSize.sm};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  transition: color ${props => props.theme.transitions.fast};
  
  &:hover {
    color: ${props => props.theme.colors.primaryLight};
    text-decoration: underline;
  }
`;

const WelcomeMessage = styled(motion.div)`
  background: ${props => props.theme.gradients.primarySubtle};
  border: 1px solid ${props => props.theme.colors.primary};
  border-radius: ${props => props.theme.borderRadius.large};
  padding: ${props => props.theme.spacing.xl};
  margin-top: ${props => props.theme.spacing['2xl']};
  text-align: center;
`;

const WelcomeText = styled.p`
  font-size: ${props => props.theme.typography.fontSize.lg};
  color: ${props => props.theme.colors.text};
  margin: 0;
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const Dashboard = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
        ease: 'easeOut',
      },
    },
  };

  return (
    <DashboardContainer>
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <HeaderSection variants={itemVariants}>
          <PageTitle>Dashboard</PageTitle>
          <PageSubtitle>
            Welcome to Premier League Predictor — Your AI-powered match prediction platform
          </PageSubtitle>
        </HeaderSection>

        <StatsGrid>
          <StatCard variants={itemVariants} whileHover={{ scale: 1.02 }}>
            <StatHeader>
              <StatIcon iconBg="rgba(16, 185, 129, 0.1)" iconColor="#10B981">
                <TrendingUp size={20} />
              </StatIcon>
            </StatHeader>
            <StatLabel>Model Accuracy</StatLabel>
            <StatValue>78.2%</StatValue>
            <StatChange positive>
              <TrendingUp size={12} />
              +2.4% from last week
            </StatChange>
          </StatCard>

          <StatCard variants={itemVariants} whileHover={{ scale: 1.02 }}>
            <StatHeader>
              <StatIcon iconBg="rgba(6, 182, 212, 0.1)" iconColor="#06B6D4">
                <Database size={20} />
              </StatIcon>
            </StatHeader>
            <StatLabel>Matches Loaded</StatLabel>
            <StatValue>1,247</StatValue>
            <StatChange positive>
              <Activity size={12} />
              All systems operational
            </StatChange>
          </StatCard>

          <StatCard variants={itemVariants} whileHover={{ scale: 1.02 }}>
            <StatHeader>
              <StatIcon iconBg="rgba(139, 92, 246, 0.1)" iconColor="#8B5CF6">
                <Clock size={20} />
              </StatIcon>
            </StatHeader>
            <StatLabel>Last Update</StatLabel>
            <StatValue>2m ago</StatValue>
            <StatChange>
              Real-time sync active
            </StatChange>
          </StatCard>
        </StatsGrid>
      </motion.div>
    </DashboardContainer>
  );
};

export default Dashboard;
