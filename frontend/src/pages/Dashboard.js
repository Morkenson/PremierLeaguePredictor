import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';
import { 
  Activity, 
  Database, 
  Clock, 
  TrendingUp,
  RefreshCw,
  Trophy,
  Calendar,
  ArrowRight
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

const Button = styled(motion.button)`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.xl};
  background: ${props => props.theme.gradients.primary};
  border: none;
  border-radius: ${props => props.theme.borderRadius.medium};
  color: white;
  font-size: ${props => props.theme.typography.fontSize.base};
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  cursor: pointer;
  transition: all ${props => props.theme.transitions.normal};
  box-shadow: ${props => props.theme.shadows.small};

  &:hover:not(:disabled) {
    box-shadow: ${props => props.theme.shadows.medium};
    transform: translateY(-2px);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
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

const SectionTitle = styled.h2`
  font-size: ${props => props.theme.typography.fontSize['2xl']};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
  color: ${props => props.theme.colors.text};
  margin: ${props => props.theme.spacing['2xl']} 0 ${props => props.theme.spacing.lg} 0;
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
`;

const TopTeamsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing['2xl']};
  
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    grid-template-columns: repeat(2, 1fr);
  }
`;

const TeamCard = styled(motion.div)`
  background: ${props => props.theme.gradients.card};
  backdrop-filter: blur(10px);
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.large};
  padding: ${props => props.theme.spacing.lg};
  box-shadow: ${props => props.theme.shadows.small};
  transition: all ${props => props.theme.transitions.normal};
  position: relative;
  overflow: hidden;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: ${props => props.theme.shadows.medium};
    border-color: ${props => props.theme.colors.primary};
  }
`;

const PositionBadge = styled.div`
  position: absolute;
  top: ${props => props.theme.spacing.md};
  right: ${props => props.theme.spacing.md};
  width: 32px;
  height: 32px;
  border-radius: ${props => props.theme.borderRadius.full};
  background: ${props => {
    if (props.position <= 4) return props.theme.colors.success;
    if (props.position <= 6) return props.theme.colors.info;
    return props.theme.colors.textMuted;
  }};
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: ${props => props.theme.typography.fontWeight.bold};
  font-size: ${props => props.theme.typography.fontSize.sm};
`;

const TeamName = styled.div`
  font-size: ${props => props.theme.typography.fontSize.base};
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const TeamStats = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.xs};
  margin-top: ${props => props.theme.spacing.sm};
`;

const TeamStat = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.textSecondary};
`;

const TeamStatValue = styled.span`
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  color: ${props => props.theme.colors.text};
`;

const PointsHighlight = styled.div`
  font-size: ${props => props.theme.typography.fontSize.xl};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
  color: ${props => props.theme.colors.primary};
  margin-top: ${props => props.theme.spacing.xs};
`;

const FixturesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing['2xl']};
  
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    grid-template-columns: 1fr;
  }
`;

const FixtureCard = styled(motion.div)`
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

const FixtureDate = styled.div`
  font-size: ${props => props.theme.typography.fontSize.xs};
  color: ${props => props.theme.colors.textSecondary};
  margin-bottom: ${props => props.theme.spacing.md};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
`;

const FixtureTeams = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.sm};
`;

const FixtureTeam = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: ${props => props.theme.typography.fontSize.base};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  color: ${props => props.theme.colors.text};
`;

const FixtureVS = styled.div`
  text-align: center;
  color: ${props => props.theme.colors.textMuted};
  font-size: ${props => props.theme.typography.fontSize.sm};
  margin: ${props => props.theme.spacing.xs} 0;
`;

const LoadingSpinner = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: ${props => props.theme.spacing.xl};
  color: ${props => props.theme.colors.textSecondary};
`;

const Dashboard = () => {
  const [schedulerStatus, setSchedulerStatus] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [topTeams, setTopTeams] = useState([]);
  const [topTeamFixtures, setTopTeamFixtures] = useState([]);
  const [loadingTeams, setLoadingTeams] = useState(true);
  const [loadingFixtures, setLoadingFixtures] = useState(true);

  useEffect(() => {
    loadSchedulerStatus();
    loadTopTeams();
    loadTopTeamFixtures(); // Load fixtures immediately
    // Refresh status every minute
    const interval = setInterval(loadSchedulerStatus, 60000);
    return () => clearInterval(interval);
  }, []);

  const loadTopTeams = async () => {
    try {
      setLoadingTeams(true);
      const table = await apiService.getLeagueTable();
      
      // Ensure table is an array
      if (!Array.isArray(table)) {
        console.error('League table is not an array:', table);
        setTopTeams([]);
        return;
      }
      
      // Get top 6 teams
      const top = table.slice(0, 6);
      setTopTeams(top);
      // Reload fixtures with new team names
      if (top.length > 0) {
        const teamNames = top.map(team => team.team_name);
        loadTopTeamFixtures(teamNames);
      }
    } catch (error) {
      console.error('Failed to load top teams:', error);
      setTopTeams([]);
    } finally {
      setLoadingTeams(false);
    }
  };

  const loadTopTeamFixtures = async (teamNames = null) => {
    try {
      setLoadingFixtures(true);
      const fixtures = await apiService.getUpcomingFixtures();
      
      console.log('Loaded fixtures:', fixtures);
      
      // Ensure fixtures is an array
      if (!Array.isArray(fixtures)) {
        console.error('Fixtures is not an array:', fixtures);
        setTopTeamFixtures([]);
        return;
      }
      
      // Use provided team names or get from state
      const topTeamNames = teamNames !== null 
        ? teamNames 
        : (Array.isArray(topTeams) ? topTeams.map(team => team.team_name) : []);
      
      console.log('Filtering with team names:', topTeamNames);
      
      // If no top teams available yet, show first 6 fixtures
      if (!topTeamNames || topTeamNames.length === 0) {
        console.log('No top teams yet, showing first 6 fixtures');
        setTopTeamFixtures(fixtures.slice(0, 6));
        return;
      }
      
      // Filter fixtures to include only those with top teams
      const filtered = fixtures.filter(fixture => 
        topTeamNames.includes(fixture.home_team) || 
        topTeamNames.includes(fixture.away_team)
      ).slice(0, 6); // Limit to 6 fixtures
      
      console.log('Filtered fixtures:', filtered);
      
      // If no matches found, show first 6 fixtures anyway
      if (filtered.length === 0 && fixtures.length > 0) {
        console.log('No matches found, showing first 6 fixtures');
        setTopTeamFixtures(fixtures.slice(0, 6));
      } else {
        setTopTeamFixtures(filtered);
      }
    } catch (error) {
      console.error('Failed to load top team fixtures:', error);
      setTopTeamFixtures([]);
    } finally {
      setLoadingFixtures(false);
    }
  };

  const loadSchedulerStatus = async () => {
    try {
      const status = await apiService.getSchedulerStatus();
      setSchedulerStatus(status);
    } catch (error) {
      console.error('Failed to load scheduler status:', error);
    }
  };

  const handleManualRefresh = async () => {
    try {
      setRefreshing(true);
      await apiService.refreshData();
      toast.success('Data refreshed successfully!');
      await loadSchedulerStatus();
    } catch (error) {
      toast.error('Failed to refresh data');
    } finally {
      setRefreshing(false);
    }
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

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
            Welcome to Premier League Predictor
          </PageSubtitle>
        </HeaderSection>

        <SectionTitle variants={itemVariants}>
          <Calendar size={24} />
          Upcoming Fixtures (Top Teams)
        </SectionTitle>

        {loadingFixtures ? (
          <LoadingSpinner>Loading fixtures...</LoadingSpinner>
        ) : !Array.isArray(topTeamFixtures) || topTeamFixtures.length === 0 ? (
          <LoadingSpinner>No upcoming fixtures for top teams</LoadingSpinner>
        ) : (
          <FixturesGrid>
            {topTeamFixtures.map((fixture, index) => {
              const formatDate = (dateString) => {
                if (!dateString) return 'TBD';
                try {
                  const date = new Date(dateString);
                  // Check if date is valid
                  if (isNaN(date.getTime())) {
                    return 'TBD';
                  }
                  // Format with time in local timezone
                  return date.toLocaleString('en-US', {
                    weekday: 'short',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    timeZoneName: 'short'
                  });
                } catch (error) {
                  console.error('Error formatting date:', error, dateString);
                  return 'TBD';
                }
              };

              return (
                <FixtureCard
                  key={index}
                  variants={itemVariants}
                  whileHover={{ scale: 1.02 }}
                >
                  <FixtureDate>
                    <Clock size={14} />
                    {formatDate(fixture.date)}
                  </FixtureDate>
                  <FixtureTeams>
                    <FixtureTeam>
                      <span>{fixture.home_team}</span>
                    </FixtureTeam>
                    <FixtureVS>VS</FixtureVS>
                    <FixtureTeam>
                      <span>{fixture.away_team}</span>
                    </FixtureTeam>
                  </FixtureTeams>
                </FixtureCard>
              );
            })}
          </FixturesGrid>
        )}

        <SectionTitle variants={itemVariants}>
          <Trophy size={24} />
          Top Teams
        </SectionTitle>

        {loadingTeams ? (
          <LoadingSpinner>Loading top teams...</LoadingSpinner>
        ) : !Array.isArray(topTeams) || topTeams.length === 0 ? (
          <LoadingSpinner>No teams available</LoadingSpinner>
        ) : (
          <TopTeamsGrid>
            {topTeams.map((team, index) => (
              <TeamCard
                key={team.team_name || index}
                variants={itemVariants}
                whileHover={{ scale: 1.02 }}
              >
                <PositionBadge position={team.position}>
                  {team.position}
                </PositionBadge>
                <TeamName>{team.team_name}</TeamName>
                <PointsHighlight>{team.points} pts</PointsHighlight>
                <TeamStats>
                  <TeamStat>
                    <span>Played</span>
                    <TeamStatValue>{team.played || 0}</TeamStatValue>
                  </TeamStat>
                  <TeamStat>
                    <span>W-D-L</span>
                    <TeamStatValue>{team.wins || 0}-{team.draws || 0}-{team.losses || 0}</TeamStatValue>
                  </TeamStat>
                  <TeamStat>
                    <span>GD</span>
                    <TeamStatValue>
                      {team.goal_difference > 0 ? '+' : ''}{team.goal_difference || 0}
                    </TeamStatValue>
                  </TeamStat>
                </TeamStats>
              </TeamCard>
            ))}
          </TopTeamsGrid>
        )}

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
            <StatValue>
              {schedulerStatus?.last_update 
                ? formatDateTime(schedulerStatus.last_update)
                : 'Loading...'}
            </StatValue>
            <StatChange>
              {schedulerStatus?.next_update 
                ? `Next: ${formatDateTime(schedulerStatus.next_update)}`
                : 'Auto-update scheduled'}
            </StatChange>
          </StatCard>
        </StatsGrid>

        {schedulerStatus && (
          <motion.div
            variants={itemVariants}
            style={{ marginTop: '24px', display: 'flex', justifyContent: 'center' }}
          >
            <Button
              onClick={handleManualRefresh}
              disabled={refreshing}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <RefreshCw size={18} style={{ animation: refreshing ? 'spin 1s linear infinite' : 'none' }} />
              {refreshing ? 'Refreshing...' : 'Refresh Data Now'}
            </Button>
          </motion.div>
        )}
      </motion.div>
    </DashboardContainer>
  );
};

export default Dashboard;
